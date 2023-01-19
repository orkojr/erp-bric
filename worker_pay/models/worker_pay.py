# -*- coding:utf-8 -*-

import babel
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError



class HrWorkerPayment(models.Model):
    _name = 'worker.payment'
    _description = 'Worker payment'
    _rec_name = "employee_id"
    


    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    date_from = fields.Date(string='Date debut', readonly=True, required=True,
        default=lambda self: fields.Date.to_string(date.today().replace(day=1)), states={'draft': [('readonly', False)]})
    date_to = fields.Date(string='Date fin', readonly=True, required=True,
        default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(weeks=+1, day=1, days=-1)).date()),
        states={'draft': [('readonly', False)]})
    # this is chaos: 4 states are defined, 3 are used ('verify' isn't) and 5 exist ('confirm' seems to have existed)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Waiting'),
        ('done', 'Done'),
        ('cancel', 'Rejected'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft',
        help="""* When the payslip is created the status is \'Draft\'
                \n* If the payslip is under verification, the status is \'Waiting\'.
                \n* If the payslip is confirmed then status is set to \'Done\'.
                \n* When user cancel payslip the status is \'Rejected\'.""")
    line_ids = fields.One2many('worker.payment.line', 'worker_pay_id', string='Lignes de paie', readonly=True,
        states={'draft': [('readonly', False)]})

    
    montant_t = fields.Float(
        string='Montant total',
        compute="_compute_montant_t",
    )


    @api.depends('line_ids')
    def _compute_montant_t(self):
        for record in self:
            total = 0
            for mnt in record.line_ids:
                total += mnt.montant
            record.montant_t = total
    
    
    
    

    def action_payslip_draft(self):
        return self.write({'state': 'draft'})

    def action_payslip_done(self):
        return self.write({'state': 'done'})

    def action_payslip_cancel(self):
        # if self.filtered(lambda slip: slip.state == 'done'):
        #     raise UserError(_("Cannot cancel a payslip that is done."))
        return self.write({'state': 'cancel'})

    