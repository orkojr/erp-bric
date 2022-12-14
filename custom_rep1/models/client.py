# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _name="bric11.client"
    _description = 'Partner description'
    
    name = fields.Char()
    email = fields.Char()
    zone_id = fields.Many2one(
        string='Zone',
        comodel_name='bric11.zone',
        ondelete='restrict',
        help="determine la zone du client",
        auto_join=True,
        
    )