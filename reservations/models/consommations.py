# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ReservationConsommation(models.Model):
    _name = 'reservation.consommation'
    _description = """Permet de renseigner sur les consommations du client."""
    _rec_name = "num_conso"

    num_conso = fields.Char('Numero Consommation',required=True, help="Numero de Consommation")
    date_conso = fields.Date(string='Date consommation', help="Date consommation client")
    heure_conso = fields.Datetime(string='Heure consommation', help="Heure consommation client")
    client_id = fields.Many2one('reservation.client', string='Client')
    prestation_ids = fields.Many2many('reservation.prestation', string='Prestation')

    nb_prestations = fields.Integer(string="Nombre de prestation",compute='comp_prestation')

    def comp_prestation(self):
        self.nb_prestations = len(self.prestation_ids)