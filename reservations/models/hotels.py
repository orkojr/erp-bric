# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ReservationHotel(models.Model):
    _name = 'reservation.hotel'
    _description = """Permet de lister les Hotels."""
    _rec_name = "nom_hotel"

    num_hotel = fields.Char('Numero Hotel',required=True, help="Numero de l'hotel")
    nom_hotel = fields.Char('Nom Hotel',required=True, help="Nom de l'hotel")
    adresse_hotel = fields.Char('Adresse Hotel', help="Adresse de l'hotel")
    cp_hotel = fields.Char('CP Hotel', help="Code postal de lotel")
    tel_hotel = fields.Char('Telephone Hotel',required=True, help="Numero de telephone de l'Hotel")
    chambre_ids = fields.One2many('reservation.chambre', 'hotel_id', string='Chambre')
    classe_id = fields.Many2one('reservation.classe', string='Classe')
    preststion_ids = fields.Many2many('reservation.prestation', string='Preststions de l\'hotel')

    nb_prestations = fields.Integer(string="Nombre de prestation", compute="comp_prestation")

    def comp_prestation(self):
        self.nb_prestations = len(self.preststion_ids)

    
    @api.model
    def hotel_test(self):
        print("Hotel")
    
