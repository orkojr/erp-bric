# -*- coding: utf-8 -*-



from unicodedata import name
from odoo import models, fields, api


class FraisTransport(models.Model):
    _name = 'bric.frais.tansport'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Represente les frais de Transport pour la livraison"

    
    name = fields.Char(
        string='Name',
        compute='_compute_name',
        store=True,
    )
    
    
    zone_id = fields.Many2one(
        string='Zone',
        comodel_name='bric1.zone',
        ondelete='cascade',
        required=True,
    )
    
    vehicle_id = fields.Many2one(
        string='Vehicule',
        comodel_name='fleet.vehicle',
        ondelete='cascade',
        required=True,
    )
    
    frais_transport = fields.Float(
        string='Frais de Transport',
        required=True,
    )

    @api.depends('zone_id','vehicle_id')
    def _compute_name(self):
        for line in self:
            line.name = str(line.zone_id.designation) + " " + str(line.vehicle_id.name)
    
    
    
    