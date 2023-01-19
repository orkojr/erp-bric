# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CustomCrmZone(models.Model):
    _name = 'bric1.zone'
    _rec_name = "designation"
    _description = """Decrit les zones."""
    _sql_constraints =  [
        ('name_unique','UNIQUE(designation)',
         'La designation de la zone doit etre Unique!'),       
    ]

    designation = fields.Char('Designation zone',required=True, help="Designe le nom de la zone")
    quartier_ids = fields.One2many('bric1.quartier', 'zone_id', string='Quartiers')
    client_ids = fields.One2many('bric1.client', 'zone_id', string='Partners')
    nb_quartier = fields.Integer(string="Nombre de Quartiers",compute='comp_quart')
    frais_transport_man = fields.Float(string="Frais de transport Man", default=0.0)
    frais_transport_actros = fields.Float(string="Frais de transport Actros", default=0.0)

    def comp_quart(self):
        self.nb_quartier = len(self.quartier_ids)
    
    