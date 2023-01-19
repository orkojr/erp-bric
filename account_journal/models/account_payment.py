# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Account_journal(models.Model):
    _inherit = 'account.journal'
    
    
    payment_debit_account_id = fields.Many2one(
        string='Payment debit',
        comodel_name='account.account',
        ondelete='cascade',
    )

    payment_credit_account_id = fields.Many2one(
        string='Payment Credit',
        comodel_name='account.account',
        ondelete='cascade',
    )

    
    
    