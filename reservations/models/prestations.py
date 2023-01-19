# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ReservationPrestation(models.Model):
    _name = 'reservation.prestation'
    _description = """Renseigne sur les prestations."""
    _rec_name = "code_pres"

    code_pres = fields.Char('Code Prestation',required=True, help="Code prestation")
    designation_pres = fields.Char('Designation Prestation',required=True, help="Designation de la prestation")
    prix_u = fields.Float('Prix Unitaire ',required=True, help="prix de la prestation")
    qte_cons = fields.Float('Quantite consernee ',required=True, help="Quantite consernee")
    hotel_ids = fields.Many2many('reservation.hotel', string='Hotel')
    consommation_ids = fields.Many2many('reservation.consommation', string='Consommation')

    nb_hotels = fields.Integer(string="Nombre d'hotels", compute='comp_hotel')
    nb_conso = fields.Integer(string="Nombre de consommation", compute='comp_conso')


    def comp_hotel(self):
        self.nb_hotels = len(self.hotel_ids)

    def comp_conso(self):
        self.nb_conso = len(self.consommation_ids)
