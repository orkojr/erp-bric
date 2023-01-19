# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ReservationCategorie(models.Model):
    _name = 'reservation.categorie'
    _rec_name = "code_cat"

    _description = """Renseigne sur la categorie."""
    code_cat = fields.Char('Code categorie',required=True, help="Code categorie")
    description = fields.Char('Description',required=True, help="Detail la description de la categorie")
    classe_ids = fields.Many2many('reservation.classe', string='Classe')
    chambre_ids = fields.One2many('reservation.chambre', 'categorie_id', string='Chambre')

    nb_classes = fields.Integer(string="Nombre de classe",compute='comp_class')

    def comp_class(self):
        self.nb_classes = len(self.classe_ids)

    # @api.multi
    # def name_get(self):
    #     result = []
    #     for categ in self:
    #         name = '[' + categ.classe_ids.nb_etoile + ']' + categ.description + ' '+ categ.code_cat
    