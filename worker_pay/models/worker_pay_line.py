# -*- coding:utf-8 -*-

from email.policy import default
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError



class HrWorkerPaymentLine(models.Model):
    _name = 'worker.payment.line'
    _description = 'Worker payment Line'
    _rec_name = "product_id"



    
    date = fields.Date(
        string='Date',
        default=fields.Date.context_today,
        required=True,
    )

    
    worker_pay_id = fields.Many2one(
        string='Paid',
        comodel_name='worker.payment',
        ondelete='cascade',
    )
    

    product_id = fields.Many2one(
        string='Nature Travail',
        comodel_name='product.product',
        ondelete='cascade',
        required=True,
    )

    nb_palette = fields.Float(
        string='Nombre de palette',
        default=0.0,
    )
    nb_piece = fields.Float(
        string='Nombre de piece',
        default=0.0,
    )
    pu = fields.Float(
        string='PU',
        help="Prix Unitaire",
        default=0.0,
    )

    montant = fields.Float(
        string='Montant',
        compute="_compute_montant",
    )

    
    sign = fields.Char(
        string='Signature',
    )
    

    @api.depends('pu','nb_palette')
    def _compute_montant(self):
        for record in self:
            record.montant = record.pu*record.nb_palette
    
    
    
    
    
    

    