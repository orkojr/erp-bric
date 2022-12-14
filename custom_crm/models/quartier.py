# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CustomCrmQuartier(models.Model):
    _name = 'bric.quartier'
    _rec_name = "appelation"
    _description = """Decrit les quartiers."""
    _sql_constraints =  [
        ('name_unique','UNIQUE(code_quartier)',
         'Le code du  quartier doit etre Unique!'),       
    ]


    code_quartier = fields.Char('Code quartier',required=True, help="Identifie de maniere unique un quartier")
    appelation = fields.Char('Appelation quartier',required=True, help="Designe le nom du quartier")
    
    client_ids = fields.One2many('bric.client', 'quartier_id', string='Clients')
    
    zone_id = fields.Many2one(
        string='Zone',
        comodel_name='bric.zone',
        ondelete='restrict',
        help="Identifie la zone du quartier",
        auto_join=True
        
    )

    nb_client = fields.Integer(string="Nombre de Clients",compute='comp_cli')

    def comp_cli(self):
        self.nb_client = len(self.client_ids)
    
    
    