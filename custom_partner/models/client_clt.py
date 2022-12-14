# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Partner description'
    
        
    zone_id = fields.Char(
        string='Zone Id',
        help="determine la zone du client",
        
    )
    