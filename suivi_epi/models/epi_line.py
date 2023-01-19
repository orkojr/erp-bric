# -*- coding: utf-8 -*-

from calendar import month
from dataclasses import field
from odoo import api, fields, models
from datetime import timedelta, date
import datetime
from dateutil.relativedelta import *
from odoo.exceptions import ValidationError

class SuiviEpiEpi(models.Model):
    _name = 'suivi.epi.line'
    _description = "Permet de Lister les EPI"



    epi_id = fields.Many2one(
        string='Nom EPI',
        comodel_name='suivi.epi.epi',
        ondelete='cascade',
    )
    
    epi_attributed = fields.Boolean(
        string='EPI Attribuer',
        default=False,
        help="Permet de savoir si les EPI sont attribues a l'employer",
    )
    
    date_attribution = fields.Date(string='Date attribution')
    date_exp = fields.Date(string='Date expiration',compute="_compute_expiration",store=True)
    
    poste_id = fields.Many2one(
        string='Poste',
        comodel_name='hr.job',
        ondelete='cascade',
    )

    poste_id1 = fields.Many2one(
        string='Poste Emp',
        comodel_name='hr.employee',
        ondelete='cascade',
    )

    poste_id11 = fields.Many2one(
        string='Poste Emp',
        comodel_name='hr.employee.public',
        ondelete='cascade',
    )

   
    
    @api.depends('epi_id','date_attribution')
    def _compute_expiration(self):
        for record in self:
            if record.epi_attributed == True :
                date11 = record.date_attribution.strftime("%Y-%m-%d")
                date1 = datetime.datetime.strptime(date11, "%Y-%m-%d")  
                date2 = date1 + relativedelta(months=+record.epi_id.duree)
                record.date_exp = date2.strftime('%Y-%m-%d')
 