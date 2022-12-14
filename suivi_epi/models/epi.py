# -*- coding: utf-8 -*-

from email.policy import default
from odoo import api, fields, models


class SuiviEpiEpi(models.Model):
    _name = 'suivi.epi.epi'
    _description = "Permet de Lister les EPI"

    
    name = fields.Char(
        string='Nom EPI',
        required=True,
    )

    duree = fields.Integer(
        string='Durée de vie(mois)',
        required=True,
        default=0,
    )
    

    

    
    
    