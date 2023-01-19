# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ReservationChambre(models.Model):
    _name = 'reservation.chambre'
    _rec_name = "num_chambre"
    
    _description = """Decrit les chambres."""
    num_chambre = fields.Char('Numero chambre',required=True, help="Numero  de chambre")
    tel_chambre = fields.Char('Numero Telehone Chambre',required=True, help="Numero  de telephone chambre")
    reservation_ids = fields.One2many('reservation.reservation', 'chambre_id', string='Reservation')
    hotel_id = fields.Many2one('reservation.hotel', string='Hotel')
    categorie_id = fields.Many2one('reservation.categorie', string='Categorie')