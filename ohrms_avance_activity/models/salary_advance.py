# -*- coding: utf-8 -*-
import time
import datetime
from datetime import timedelta
from odoo import fields, models, api, _
from odoo import exceptions
from odoo.exceptions import UserError, ValidationError


class SalaryAdvancePayment(models.Model):
    _inherit = "salary.advance"


    @api.model
    def create_activity(self):
        salaries = self.env['salary.advance'].search([('state','in', ['submit','waiting_approval'])])
        users = self.env.ref('hr.group_hr_manager').users
        today = datetime.date.today()
        for salary in salaries:
            d2 = abs((today - salary.date).days)
            if d2 > 5:
                salary.state = 'cancel'
            else:
                d1 = salary.date + timedelta(days=+5)
                for user in users:
                    data = {
                    'res_id': salary.id,
                    'res_model_id': self.env['ir.model'].search([('model', '=', 'salary.advance')]).id,
                    'user_id': user.id,
                    'summary': 'Approuver la demande d\'avance sur salaire',
                    'note' :f"La demande de { salary.employee_id.name } Est en attente d'approbation.\n Elle expire le {d1}",
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'date_deadline': d1
                    }
                    self.env['mail.activity'].create(data)