# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CustomCrmQuartier(models.Model):
    _name = 'bric11.quartier'
    _rec_name = "appelation"
    _description = """Decrit les quartiers."""
    _sql_constraints =  [
        ('name_unique','UNIQUE(appelation)',
         'Le Nom du  quartier doit etre Unique!'),       
    ]
    appelation = fields.Char('Appelation quartier',required=True, help="Designe le nom du quartier")
    zone_id = fields.Many2one(
        string='Zone',
        comodel_name='bric11.zone',
        ondelete='restrict',
        help="Identifie la zone du quartier",
        auto_join=True
        
    )