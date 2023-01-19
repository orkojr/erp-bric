# -*- coding: utf-8 -*-

from email.policy import default
from odoo import api, fields, models


class ApporteurOportunite(models.Model):
    _name = "sale.apporteur"
    _description = "Apporteur d'oportunite"

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

    cout = fields.Float(
       string='Coût Commission',
       help="Commission touchée par l'apporteur de marcher",
       compute="compute_cout",
       store=True,
       
   )
   
    is_paid = fields.Boolean(
        string='Payée',
        default = False,
    )

    
    paid_date = fields.Date(
        string='Date de paeiment',
    )
    
    
   
    order_id = fields.Many2one(
       string='Devis',
       comodel_name='sale.order',
       ondelete='cascade',
    )


    
    @api.depends('commission','order_id')
    def compute_cout(self):
        for app in self:
            ct = (app.order_id.amount_untaxed*app.commission)/100
            app.cout = round(ct, 2)
    



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    
    apporteur_ids = fields.One2many(
        string='Commissions',
        comodel_name='sale.apporteur',
        inverse_name='order_id',
    )

    apporteur = fields.Boolean(
        string='Apporteur d\'affaires',
        default=False,
    )
    
    

    



   


   
   
    

    

    
    
    