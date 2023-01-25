# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    def _prepare_chargement_line(self,sequence):
        self.ensure_one()
        res = {
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'product_qty': self.product_uom_qty,
            
        }
        
        return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    check_oc = fields.Boolean(string="Ordre de chargement genere",default=False)
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('valide', 'Ordre de chargement'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    chargement_ids = fields.Many2one("sales.chargement", string='Ordre de chargement', copy=False)
    
    def prepare_chargement(self):
        chargement_vals = {
            'origin': self.name,
            'user_id': self.user_id.id,
            'partner_id': self.partner_invoice_id.id,
            'order_id' : self.id,
            'move_lines': [],
            'name' : "OC",
            'state':'draft',
                
            }
        return chargement_vals

    

    def _prepare_so_line(self, order, amount):
        context = {'lang': order.partner_id.lang}
        so_values = {
            'name': "OC",
            'price_unit': amount,
            'product_uom_qty': 0.0,
            'order_id': order.id,
            'product_uom': self.product_id.uom_id.id,
            'product_id': self.product_id.id,

           
            'sequence': order.order_line and order.order_line[-1].sequence + 1 or 10,
        }
        del context
        return so_values

    def action_print_oc(self):
        chargement_vals_list = []
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        print ('Bon de commande:',self)
        chargement_item_sequence = 0
        sale_line_obj = self.env['sale.order.line']
        for order in self:
            chargement_vals = order.prepare_chargement()           
            chargement_line_vals = []
            
            for line in order.order_line:
                chargement_line_vals.append(
                    (0, 0, line._prepare_chargement_line(
                        sequence=chargement_item_sequence,
                    )),
                )
                chargement_item_sequence += 1

            chargement_vals['move_lines'] += chargement_line_vals
            chargement_vals_list.append(chargement_vals)
        print (chargement_vals_list)
        moves = self.env['sales.chargement'].sudo().with_context().create(chargement_vals_list)
        print ('ORDRE DE CHARGEMENT:',moves)
        self.write({'invoice_status': 'to invoice', 'check_oc': True, 'chargement_ids' : moves.id, 'state': 'valide', })
        
        
        return moves
        
    def action_view_chargement(self):
        invoices = self.chargement_ids
        print ('CHARGEMENT:',invoices)
        action = self.env["ir.actions.actions"]._for_xml_id("sales_bric.action_move_chargement_type")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
        
            form_view = [(self.env.ref('sales_bric.view_sales_chargement_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        
        return action

    def action_view_invoice(self):
        
        if self.check_oc == False:
            raise UserError('Impossible de traiter une livraison sans ordre de chargement')
        
        invoices = self.mapped('invoice_ids')
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        context = {
            'default_move_type': 'out_invoice',
        }
        if len(self) == 1:
            context.update({
                'default_partner_id': self.partner_id.id,
                'default_partner_shipping_id': self.partner_shipping_id.id,
                'default_invoice_payment_term_id': self.payment_term_id.id or self.partner_id.property_payment_term_id.id or self.env['account.move'].default_get(['invoice_payment_term_id']).get('invoice_payment_term_id'),
                'default_invoice_origin': self.name,
                'default_user_id': self.user_id.id,
            })
        action['context'] = context
        return action


class Chargement(models.Model):
    _name = "sales.chargement"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Transfer"


    name = fields.Char(
        'Reference', default='/',
        copy=False, index=True, readonly=True)
    origin = fields.Char(
        'Document Source', index=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Reference of the document")
    note = fields.Html('Notes')
    
    
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('valide', 'Valide'),
        ('cancel', 'Annule'),
    ], string='Status',
        copy=False, index=True, readonly=True, store=True, tracking=True,default="draft")
    
    
    date_deadline = fields.Datetime(
        "Deadline", compute='_compute_date_deadline', store=True,
        help="Date Promise to the customer on the top level document (SO/PO)")
    has_deadline_issue = fields.Boolean(
        "Is late", compute='_compute_has_deadline_issue', store=True, default=False,
        help="Is late or will be late depending on the deadline and scheduled date")
    date = fields.Datetime(
        'Date de creation',
        default=fields.Datetime.now, tracking=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Creation Date, usually the time of the order")
    date_done = fields.Datetime('Date of Transfer', copy=False, readonly=True, help="Date at which the transfer has been processed or cancelled.")
    delay_alert_date = fields.Datetime('Delay Alert Date', compute='_compute_delay_alert_date', search='_search_delay_alert_date')
    
    @api.model
    def create(self,vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('sales.chargement') or _('New')
        return super(Chargement,self).create(vals)
    
    move_lines = fields.One2many('stock.move.chargement', 'picking_chargement_id', string="Stock Moves", copy=True)
    
    partner_id = fields.Many2one(
        'res.partner', 'Client',
        check_company=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    company_id = fields.Many2one(
        'res.company', string='Company',readonly=True, store=True, index=True)
    user_id = fields.Many2one(
        'res.users', 'Responsible', tracking=True,
        domain=lambda self: [('groups_id', 'in', self.env.ref('stock.group_stock_user').id)],
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        default=lambda self: self.env.user)
    show_check_availability = fields.Boolean(
        compute='_compute_show_check_availability',
        help='Technical field used to compute whether the button "Check Availability" should be displayed.')
    show_mark_as_todo = fields.Boolean(
        compute='_compute_show_mark_as_todo',
        help='Technical field used to compute whether the button "Mark as Todo" should be displayed.')
   
    owner_id = fields.Many2one(
        'res.partner', 'Assign Owner',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        check_company=True,
        help="When validating the transfer, the products will be assigned to this owner.")
    printed = fields.Boolean('Printed', copy=False)
    order_id = fields.Many2one(
        'sale.order', string='Sale Order',readonly=True, store=True, index=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id)', 'Reference must be unique per company!'),
    ]

    def valide(self):
        if self.state:
            self.state = 'valide'



class MoveChargement(models.Model):
    _name = "stock.move.chargement"
    _description = "Chargement Line"
    _order = 'id'
    _rec_name = "product_id"


     
    
    product_id = fields.Many2one('product.product', 'Designation', required=True, check_company=True)
    
    name = fields.Char('Name')
    
    product_qty = fields.Float(
        'Quantite', default=1.0,
        digits='Product Unit of Measure', required=True)
    
    product_uom_id = fields.Many2one(
        'uom.uom', 'Product Unit of Measure',      
        required=True,
        help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control", domain="[('category_id', '=', product_uom_category_id)]")
    
    production_order_id = fields.Many2one(
        'mrp.production', 'Ordre de Fabrication',
        index=True, ondelete='cascade')
    production_plan_line_id = fields.Many2one(
        'mrp.plan', 'Parent BoM',
        index=True, ondelete='cascade')  
    note = fields.Html('Observations') 
    picking_chargement_id = fields.Many2one('sales.chargement', 'Assign Owner')



class DemandeInterne(models.Model):
    _name = "demande.interne"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Demande interne Achat"


    name = fields.Char(
        'Reference', default='/',
        copy=False, index=True)
    origin = fields.Char(
        'Source Document', index=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Reference of the document")
    note = fields.Html('Notes')
    
    
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('valide', 'Valide'),
        ('done', 'Fait'),
        ('cancel', 'Annule'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, tracking=True,default="draft")
    
    
    date_deadline = fields.Datetime(
        "Deadline", compute='_compute_date_deadline', store=True,
        help="Date Promise to the customer on the top level document (SO/PO)")
    has_deadline_issue = fields.Boolean(
        "Is late", compute='_compute_has_deadline_issue', store=True, default=False,
        help="Is late or will be late depending on the deadline and scheduled date")
    date = fields.Datetime(
        'Date',
        default=fields.Datetime.now, tracking=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Creation Date, usually the time of the order")
    date_done = fields.Datetime('Date of Transfer', copy=False, readonly=True, help="Date at which the transfer has been processed or cancelled.")
    delay_alert_date = fields.Datetime('Delay Alert Date', compute='_compute_delay_alert_date', search='_search_delay_alert_date')
   
    
    move_lines = fields.One2many('demande.interne.line', 'demande_id', string="Stock Moves", copy=True)
    
    partner_id = fields.Many2one(
        'hr.department', 'Service',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    company_id = fields.Many2one(
        'res.company', string='Company',readonly=True, store=True, index=True)
    user_id = fields.Many2one(
        'res.users', 'Responsable', tracking=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        default=lambda self: self.env.user)
    user_destinataire_id = fields.Many2one(
        'res.users', 'Destinataire', tracking=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    printed = fields.Boolean('Printed', copy=False)
    order_id = fields.Many2one(
        'sale.order', string='Sale Order',readonly=True, store=True, index=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id)', 'Reference must be unique per company!'),
    ]

        
    def cancel(self):
        if self.state:
            self.state = 'cancel'
    
        
    def valide(self):
        if self.state:
            self.state = 'valide'
    
    
class DemandeInterneLine(models.Model):
    _name = "demande.interne.line"
    _description = "Demande Line"
    _order = 'id'
    _rec_name = "product_id"


     
    
    product_id = fields.Many2one('product.product', 'Designation', required=True)
    
    name = fields.Char('Name')
    
    product_qty = fields.Float(
        'Quantite', default=1.0,
        digits='Product Unit of Measure', required=True)
    
    product_uom_id = fields.Many2one(
        'uom.uom', 'Unite de mesure',      
        required=True,
        help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control")
    
   
    note = fields.Html('Observations') 
    demande_id = fields.Many2one('demande.interne', 'Service')
