# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move'


    casse_livr = fields.Integer(
        string='Casses de livraison',
        default=0,
        
    )
    
    