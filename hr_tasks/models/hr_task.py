# -*- coding: utf-8 -*-
from email.policy import default
import time
from datetime import datetime, timedelta
import datetime
from odoo import fields, models, api, _
from odoo import exceptions
from odoo.exceptions import UserError, ValidationError


class HrTimesheet(models.Model):
    _inherit = 'account.analytic.line'


    employee_task_id = fields.Many2one('hr.employee', string='Employé', required=True, help="Employee")
    objectif = fields.Char(string='Objectifs')
    percent = fields.Float(string='% Atteinte Objectifs')
    hour_from = fields.Float(string='Heure de debut')
    hour_to = fields.Float(string='Heure de fin')
