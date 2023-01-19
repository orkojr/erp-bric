# -*- coding: utf-8 -*-

from email.policy import default
from odoo import api, fields, models


class MaintenanceComposant(models.Model):
    _inherit = "maintenance.request"
    _description = 'Ordre de Maintenance'
    
    
    line_request_ids = fields.One2many(string='Maintenance Request', comodel_name='maintenance.request.line', inverse_name='request_id')
    cout_total = fields.Float(string='Cout Total', compute='_compute_cout_total', store=True, default=0.0)
    causes = fields.Char(string='Causes ou Utilité', placeholder='Causes')
    observations = fields.Html(string='Observations', placeholder='observations')
    mise_en_marche = fields.Date(string='Date Mise en marche')
    main_doeuvre = fields.Float(string='Montant main d\'oeuvre', default=0.0)
    bon_commande_id = fields.Many2one(string='Numero bon de Commande', comodel_name='purchase.order', ondelete='cascade')
    debut = fields.Datetime(string='Date de debut') 
    chekpoint_ids = fields.One2many(string='Points de controle', comodel_name='maintenance.checkpoint.line', inverse_name='request_id')
    executant_id = fields.Many2one(string='Employé exécutant',comodel_name='hr.employee')
    purchase_id = fields.Many2one(comodel_name='purchase.request', string='Purchase', copy=False, readonly=True, tracking=True)
    request = fields.Boolean('Bon de commande interne', copy=False, readonly=True)
    repaired = fields.Boolean('Repare', copy=False, readonly=True)
    executant_ids = fields.One2many(string='Employés exécutants',comodel_name='hr.employee', required=True, inverse_name='maintenance_r_id')
    type_intervention = fields.Selection(string='Type d\'intervention',selection=[('interne', 'Interne'), ('externe', 'Externe'), ('deux', 'Interne & Externe')],default='interne')
    secteur = fields.Selection(string='Secteur',selection=[('unite_production', 'Unite de production'), ('parc_info', 'Parc informatique'), ('autres', 'Autres')],default='unite_production')
    ser_demandeur_id = fields.Many2one(string='Service Demandeur',comodel_name='hr.department',ondelete='cascade',required=True)
    ser_beneficiaire_id = fields.Many2one(string='Service Bénéficiaire',comodel_name='hr.department',ondelete='cascade',required=True)
    fees_lines = fields.One2many(
        'maintenance.fee', 'repair_id', 'Operations',
        copy=True, readonly=False)
    

    @api.onchange('equipment_id')
    def onchange_chekpoint_ids(self):
        self.chekpoint_ids = self.equipment_id.checkpoint_ids
    """ @api.onchange('secteur')
    def onchange_secteur(self):
        equipement=self.env["maintenance.equipment"]
        self.equipment_id = self.equipment_id.checkpoint_ids     """
    # @api.model
    # def _notification_task(self):
    #     request = self.search([('done', '=', False)])
    #     if len(request)>0 :
    #         return True

    
    @api.depends('line_request_ids.cout', 'main_doeuvre')
    def _compute_cout_total(self):
        for main in self:
            cout_t = 0.0
            for line in main.line_request_ids:
                cout_t += line.cout
            self.cout_total = cout_t + main.main_doeuvre

   
    def action_open_purchase_request(self):
        """ Creates purchase request for repair order.
      
        @return: purchase request Ids.
        """
        for repair in self:
          
            
            purchase_vals = {
                'requested_by' : repair.employee_id.user_id.id,
                'service_demandeur_id': repair.ser_demandeur_id.id,
                'service_id' : repair.ser_beneficiaire_id.id,
                'description' : repair.name,
                'objet':'maint',
                'date_start': repair.request_date,
                #'repair_ids': [(4, repair.id)],
                'line_ids': [],
              
            }
            

            # Create invoice lines from pieces detachees.
            for operation in repair.line_request_ids:
                
               

                invoice_line_vals = {
                    'name': operation.product_id.default_code,
                    'product_qty': operation.quantite_piece,
                   
                    'product_uom_id': operation.product_uom.id,
                    'price_unit': operation.prix_unitaire,
                    'product_id': operation.product_id.id,
                    'date_required': repair.request_date,
                    'repair_line_ids': [(4, operation.id)],
                }

               
                purchase_vals['line_ids'].append((0, 0, invoice_line_vals))
            
            # Create invoice lines from main doeuvre.
            main_oeuvre = repair.main_doeuvre
            
            
            self.env['purchase.request'].create(purchase_vals)

            repair.write({'request': True})
            repair.mapped('line_request_ids').write({'invoiced': True})
            
    def action_created_purchase_request(self):
        action = self.env["ir.actions.actions"]._for_xml_id("purchase_request.purchase_request_form_action")
        #lines = self.mapped("self.purchase_id")
        invoices = self.purchase_id
        print("PURCHASE", invoices)
        """ if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
        
            form_view = [(self.env.ref('purchase_request.view_purchase_request_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id """

      
        return action

class MaintenanceComposantLine(models.Model):
    _name = "maintenance.request.line"
    _description = 'Ordre de Maintenance line'
    
    
    cout = fields.Float(string='Cout', compute='cout_compute', store=True, default=0.0)
    invoiced = fields.Boolean('Invoiced', copy=False, readonly=True)
    request_id = fields.Many2one(string='Request', comodel_name='maintenance.request', ondelete='cascade')
    quantite_piece = fields.Integer(string='Quantite utilisee', default=0)
    product_id = fields.Many2one(string='Pièces', comodel_name='product.product', ondelete='restrict')
    product_uom = fields.Many2one(comodel_name="uom.uom",string="Unite de Mesure", tracking=True)
    prix_unitaire = fields.Float(string='Prix Unitaire', default=0.0)
    invoice_line_id = fields.Many2one(
        'purchase.request.line', 'Purchase Request Line',
        copy=False, readonly=True, check_company=True)

    
    @api.depends('prix_unitaire', 'quantite_piece')
    def cout_compute(self):
        for line in self:
            line.cout = line.prix_unitaire*line.quantite_piece

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    
    maintenance_r_id = fields.Many2one(string='Requete Maintenance',comodel_name='maintenance.request',ondelete='cascade',)   
    
class MaintenanceFee(models.Model):
    _name = 'maintenance.fee'
    _description = 'Maintenance Fees'

    repair_id = fields.Many2one(
        'maintenance.request', 'Repair Order Reference',
        index=True, ondelete='cascade', required=True)
    company_id = fields.Many2one(
        related="repair_id.company_id", index=True, store=True)
    
    name = fields.Text('Description', index=True, required=True)
    product_id = fields.Many2one(
        'product.product', 'Product', check_company=True,
        domain="[('type', '=', 'service')]")
    product_uom_qty = fields.Float('Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price')
    product_uom = fields.Many2one('uom.uom', 'Product Unit of Measure', required=True, domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    price_subtotal = fields.Float('Subtotal', compute='_compute_price_subtotal', store=True, digits=0)
    
    invoice_line_id = fields.Many2one('account.move.line', 'Invoice Line', copy=False, readonly=True, check_company=True)
    invoiced = fields.Boolean('Invoiced', copy=False, readonly=True)

    @api.depends('price_unit', 'repair_id', 'product_uom_qty', 'product_id')
    def _compute_price_subtotal(self):
        for fee in self:
            taxes = fee.price_unit*fee.product_uom_qty
            fee.price_subtotal = taxes

    

    @api.onchange('repair_id', 'product_id', 'product_uom_qty')
    def onchange_product_id(self):
        """ On change of product it sets product quantity, tax account, name,
        uom of product, unit price and price subtotal. """
        if not self.product_id:
            return

        self = self.with_company(self.company_id)   

class EmployeePublic(models.Model):
    _inherit = 'hr.employee.public'
    
    
    maintenance_r_id = fields.Many2one(string='Requete Maintenance',comodel_name='maintenance.request',ondelete='cascade',) 