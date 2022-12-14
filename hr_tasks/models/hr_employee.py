# -*- coding: utf-8 -*-
import time
from datetime import datetime
from odoo import fields, models, api, _
from odoo import exceptions
from odoo.exceptions import UserError, ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description ="Employee"



    @api.depends('task_employee_ids')
    def _compute_tasks_count(self):
        for rec in self:
            rec.task_total_count = len(rec.task_employee_ids)
    

    
    
    task_employee_ids = fields.One2many(string='Tâches',comodel_name='account.analytic.line',inverse_name='employee_task_id')
    task_total_count = fields.Integer(string='Total Tâches',compute='_compute_tasks_count' , store=True)
    
    
    
    
    
    
        
   
    


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'
    _description ="Employee"


    task_employee_ids = fields.One2many(string='Tâches',comodel_name='account.analytic.line',inverse_name='employee_task_id', readonly=True)
    task_total_count = fields.Integer(string='Total Tâches',readonly=True, store=True)
    
    
    
    
    
    
    

    