# -*- coding: utf-8 -*-

from email.policy import default
from itertools import product
from odoo import api, fields, models, SUPERUSER_ID, _


class HrExpense(models.Model):
    _inherit = "hr.expense"
    
    post_depense = fields.Many2one('account.budget.post', 'Poste de depense')




    
    
    


   

    
    
    
    
    
    