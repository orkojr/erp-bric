# -*- coding: utf-8 -*-

from email.policy import default
from odoo import api, fields, models, _
from odoo.exceptions import UserError



class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    
    
    urgence_type = fields.Selection(
        string='Type de Lien',
        selection=[('conjoint', 'Conjoint(e)'), ('parent', 'Parent'), ('famille', 'Famille'),('ami', 'Ami(e)')],
        default='',
    )
    


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'
    
    
    
    urgence_type = fields.Selection(
        string='Type de Lien',
        selection=[('conjoint', 'Conjoint(e)'), ('parent', 'Parent'), ('famille', 'Famille'),('ami', 'Ami(e)')],
        default="",
        readonly=True 
    )
    