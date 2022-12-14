# -*- coding: utf-8 -*-
from email.policy import default
import time
from datetime import datetime, timedelta
import datetime
from odoo import fields, models, api, _
from odoo import exceptions
from odoo.exceptions import UserError, ValidationError


class EmployeeObjectif(models.Model):
    _name = "employee.objectif"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description ="Représente les  objectifs annuels des employés"
    _rec_name = 'objectif' 



    objectif = fields.Char(string='Objectif', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employé', required=True, help="Employee")
    date_echeance = fields.Date(string='Écheance', required=True, default=lambda self: fields.Date.today(), help="Date Échéance")
    en_cours = fields.Selection(string='En Cours', selection=[('1', '0%'), ('2', '25%'),('3', '50%'),('4', '75%'),('5', '100%')], default='1')
    responsable_id = fields.Many2one('hr.employee', string='Responsable', required=True, help="Responsable Employé ")
    description = fields.Html(string='Description',help="Tapez '/' pour choisir la police")
    progress = fields.Integer(string='Progression', compute='_compute_progress',store=True)
    employee_id1 = fields.Many2one('hr.employee', string='Employé',)

    

    @api.depends('en_cours')
    def _compute_progress(self):
        for record in self:
            if record.en_cours == '1':
                record.progress = 0
            elif record.en_cours == '2':
                record.progress = 25
            elif record.en_cours == '3':
                record.progress = 50
            elif record.en_cours == '4':
                record.progress = 75
            elif record.en_cours == '5':
                record.progress = 100
    
    
    

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.responsable_id = self.employee_id.parent_id.id if self.employee_id.parent_id else None

    @api.model
    def create_activity(self):
        objectifs = self.env['employee.objectif'].search([('en_cours', '!=', '5')])
        employee = self.env['hr.employee'].search([])
        users = self.env.ref('hr.group_hr_manager').users
        today = datetime.date.today()
        day = datetime.date.today().strftime('%A')
        if day in  ['Saturday','Samedi','saturday','samedi']:

            for emp in employee:
                if len(emp.objectifs_ids)  == 0 :
                    emp.objectif_total_count = len(emp.objectifs_ids)
                    for user in users:
                        data = {
                        'res_id': emp.id,
                        'res_model_id': self.env['ir.model'].search([('model', '=', 'hr.employee')]).id,
                        'user_id': user.id,
                        'summary': 'Definir les objectifs',
                        'note' :f"Vous devez definir les objectifs de { emp.name } Aucun objectif n'a ete trouver",
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                        'date_deadline': today
                        }

                        self.env['mail.activity'].create(data)
        