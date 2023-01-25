# -*- coding: utf-8 -*-

from email.policy import default
from odoo import api, fields, models, _
from odoo.exceptions import UserError



class ApporteurOportunite(models.Model):
    _name = "sale.apporteur"
    _description = "Apporteur d'oportunite"



    def generate_emp_request(self):

        emp_request = self.env['employe.request']
        product_obj = self.env['product.product'].search([('product_tmpl_id.detailed_type', '=', 'service'),('product_tmpl_id.name', '=', 'Commissions suivantes')])
        id = None
        design = None
        qty = None
        um = None
        if len(product_obj) > 0:
            for pro in product_obj:
                id = pro.id 
                design = pro.product_tmpl_id.name
                qty = 1
                um = pro.product_tmpl_id.uom_id.id
            request_by = self.env["res.users"].browse(self.env.uid)
            service = request_by.employee_id.department_id
            vals = {
                "requested_by": request_by.id,
                "service_demandeur_id": service.id,
                "service_id": service.id,
                "objet": 'admin',
                "description": "paiement d'une commission",
                "state": 'draft',
                "is_administration": True,
                "move_id": self.move_id.id,
            }

            vals.update({'line_ids': [(0, 0, {'product_id':id, "name": design , "price_unit": self.cout, "product_qty": qty, "product_uom_id": um, })]})

            print("Nous sommes ici Mr Orko")

            emp_request.create(vals)

            return {
            'type': 'ir.actions.act_window',
            'name': 'Demandes internes',
            'view_mode': 'tree,form',
            'res_model': 'employe.request',
            'domain': [('move_id', '=', self.move_id.id)],
            # 'context': "{'create': False}"
            }
            # return {
            #     "name": _("Demande interne"),
            #     "view_mode": "tree,form",
            #     "res_model": "employe.request",
            #     "view_id": False,
            #     "context": False,
            #     "type": "ir.actions.act_window",
            # }
        else:
            raise UserError(
                    _("Le produit Commission n'existe pas")
                )
        

    partner_id = fields.Many2one(
       string='Apporteur d\'affaires',
       comodel_name='res.partner',
       ondelete='cascade',
       help="apporteur de marcher externe",
   )
    commission = fields.Float(
       string='Commission(%)',
       help="pourcentage de Commission touchée par l'apporteur de marcher",
       default=0.0
       
   )
    active = fields.Boolean('Active', default=True)
    team_id = fields.Many2one('crm.team', string='Equipe commerciale')
    employe_id = fields.Many2one('hr.employee', string='Employé')
    cout = fields.Float(
       string='Coût Commission',
       help="Commission touchée par l'apporteur de marché",
       compute="compute_cout",
       store=True,
       
   )
   
    is_paid = fields.Boolean(
        string='Payée',
        default = False,
    )

    validation_date = fields.Date(
        string='Date de validation',
    )
    paid_date = fields.Date(
        string='Date de paiement',
    )
    
    

    move_id = fields.Many2one(
       string='Facture',
       comodel_name='account.move',
       ondelete='cascade',
    )

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('valide', 'Validé'),
        ('cancel', 'Annule'),
    ], string='Statut',
        copy=False, index=True, readonly=True, store=True, tracking=True,default="draft")
    
    @api.depends('commission','move_id')
    def compute_cout(self):
        for app in self:
            ct = (app.move_id.amount_untaxed*app.commission)/100
            app.cout = round(ct, 2)
    
    def valide(self):
        if self.state:
            self.state = 'valide'



class SaleOrder(models.Model):
    _inherit = 'account.move'

    
    apporteur_ids = fields.One2many(
        string='Commissions',
        comodel_name='sale.apporteur',
        inverse_name='move_id',
    )

    apporteur = fields.Boolean(
        string='Commissions sur la vente',
        default=False,
    )

    # apporteur_count = fields.Integer(compute='compute_count')
    
    # def compute_count(self):
    #     for record in self:
    #         record.apporteur_count = self.env['sale.apporteur'].search_count(
    #             [('move_id', '=', self.id)])
    

    def action_employee_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Demandes internes',
            'view_mode': 'tree,form',
            'res_model': 'employe.request',
            'domain': [('move_id', '=', self.id)],
            # 'context': "{'create': False}"
        }


    # def action_employee_request(self):
        
    #     requests = self.apporteur_ids
    #     action = self.env["ir.actions.actions"]._for_xml_id("purchase_request.employe_request_form_action")
    #     if len(requests) > 1:
    #         action['domain'] = [('id', 'in', requests.ids)]
    #     elif len(requests) == 1:
        
    #         form_view = [(self.env.ref('purchase_request.view_employe_request_form').id, 'form')]
    #         if 'views' in action:
    #             action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
    #         else:
    #             action['views'] = form_view
    #         action['res_id'] = requests.id
        
    #     return action


    

class EmployeeRequest(models.Model):
    _inherit = 'employe.request'



    
    move_id = fields.Many2one(
        string='apporteur',
        comodel_name='account.move',
        ondelete='cascade',
        readonly=True 
    )
    
   


   
   
    

    

    
    
    