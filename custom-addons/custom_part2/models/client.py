# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    
    zone_id = fields.Many2one(
        string='Zone',
        comodel_name='bric1.zone',
        ondelete='restrict',
        help="determine la zone du client",
        auto_join=True,
        
    )
    
    