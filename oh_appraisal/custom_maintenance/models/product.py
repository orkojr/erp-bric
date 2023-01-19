# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'
    _description = 'Prodcut pieces'
    

    
    maintenance_id = fields.Many2one(
        string='composant',
        comodel_name='maintenance.equipment',
        ondelete='restrict',
    )

    request_id = fields.Many2one(
        string='pieces',
        comodel_name='maintenance.request',
        ondelete='restrict',
    )
    
    

    
    
    
    
    
    