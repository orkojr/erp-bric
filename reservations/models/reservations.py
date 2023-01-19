# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ReservationReservation(models.Model):
    _name = 'reservation.reservation'
    _description = """Renseigne sur les Reservations."""
    _rec_name = "num_reser"

    num_reser = fields.Char("Numero Reservation", required=True, help="Numero reservation")
    date_debut = fields.Date(string='Date Debut', help="Date de debut de la reservation")
    date_fin = fields.Date(string='Date Fin', help="Date de Fin de la reservation")
    date_paye = fields.Datetime(string='Date Paye', help="Date de paye de la reservation")
    montant = fields.Float("Montant paye", help="Montant de la reservation")
    client_id = fields.Many2one('reservation.client', string='Client')
    chambre_id = fields.Many2one('reservation.chambre', string='Chambre')