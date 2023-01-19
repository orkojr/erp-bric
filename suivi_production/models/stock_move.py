# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    quantity_done = fields.Float(
        'Quantity Done', 
        compute='_quantity_done_compute', 
        digits='Product Unit of Measure', 
        inverse='_quantity_done_set', 
        store=True, 
        index=True,
    )
    