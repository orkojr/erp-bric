# -*- coding: utf-8 -*-
 
from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit="stock.picking",
    _description="vehicule d'une livraison"

    vehicle_id = fields.Many2one(
        string='Vehicule',
        comodel_name='fleet.vehicle',
        ondelete='restrict',
    )
    