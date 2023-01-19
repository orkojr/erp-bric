# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ReservationClasse(models.Model):
    _name = 'reservation.classe'
    _rec_name = "nb_etoile"
    _description = """Classe de l'hotel."""

    nb_etoile = fields.Integer('Nombre d\'etoiles',required=True, help="Nombre d'etoiles")
    tarif_unit = fields.Integer('Tarif unitaire',required=True, help="Tarif unitaire")
    hotel_ids = fields.One2many('reservation.hotel', 'classe_id', string='Hotel')
    categorie_ids = fields.Many2many('reservation.categorie', string='Categories')

    nb_categories = fields.Integer(string="Nombre de categorie", compute='comp_cat')


    def comp_cat(self):
       self.nb_categories = len(self.categorie_ids) 