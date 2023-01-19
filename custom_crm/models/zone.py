# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CustomCrmZone(models.Model):
    _name = 'bric.zone'
    _rec_name = "designation"
    _description = """Decrit les zones."""
    _sql_constraints =  [
        ('name_unique','UNIQUE(code_zone)',
         'Le code de la zone doit etre Unique!'),       
    ]


    code_zone = fields.Char('Code zone',required=True, help="Identifie de maniere unique une zone")
    designation = fields.Char('Designation zone',required=True, help="Designe le nom de la zone")
    quartier_ids = fields.One2many('bric.quartier', 'zone_id', string='Quartiers')

    nb_quartier = fields.Integer(string="Nombre de Quartiers",compute='comp_quart')

    def comp_quart(self):
        self.nb_quartier = len(self.quartier_ids)
    
    