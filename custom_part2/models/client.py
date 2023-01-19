# -*- coding: utf-8 -*-

from email.policy import default
from odoo import api, fields, models, _
from datetime import timedelta, date
import datetime
from dateutil.relativedelta import *
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    
    zone_id = fields.Many2one(
        string='Zone',
        comodel_name='bric1.zone',
        ondelete='restrict',
        help="determine la zone du client",
        auto_join=True,
        
    )
    type_contact = fields.Selection(string='Type de Contact',selection=[('emp', 'Employé'), ('client', 'Client'), ('four', 'Fournisseur')],default='emp')
    
    
    