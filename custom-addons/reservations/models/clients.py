# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ReservationClient(models.Model):
    _name = 'reservation.client'
    _description = """Permet de renseigner sur les clients."""
    _rec_name = "l_name"

    code_cli = fields.Char('Code Client',required=True, help="Code du client")
    l_name = fields.Char('Last Name',required=True, help="renseigne sur le nom du  client")
    f_name = fields.Char('First Name', help="renseigne sur le prenom du  client")
    adresse = fields.Char('Adresse', help="renseigne sur l'adresse du  client")
    city = fields.Char('City', help="renseigne sur la ville du  client")
    cp = fields.Char('CP', help="renseigne sur le code postal du client")
    country = fields.Char('Country', help="renseigne sur le pays du client")
    phone = fields.Char('Phone Number',required=True, help="renseigne sur le numero de telephone du client")
    email = fields.Char('Email',required=True, help="renseigne sur l'adresse mail client")
    consommation_ids = fields.One2many('reservation.consommation', 'client_id', string='Consommations de ce client')
    reservation_ids = fields.One2many('reservation.reservation', 'client_id', string='Reservations de ce client')