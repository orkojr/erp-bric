# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _name = 'bric1.client'
    _inherits = {'res.partner': 'partner_id'}
    _description = 'Partner description'
    
    
        
    zone_id = fields.Many2one(
        string='Zone',
        comodel_name='bric1.zone',
        ondelete='restrict',
        help="determine la zone du client",
        auto_join=True,
        
    )
    partner_id = fields.Many2one(
        string='Nom',
        comodel_name='res.partner',
        ondelete='cascade',
        help="Pour identifier le client",
        auto_join=True,
        required=True,
        
    )
    