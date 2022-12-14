# -*- coding: utf-8 -*-

from email.policy import default
from odoo import api, fields, models, _
from datetime import timedelta, date
import datetime
from dateutil.relativedelta import *
from odoo.exceptions import ValidationError

class SuiviEpiEpi(models.Model):
    _inherit = 'hr.employee'

    

    epi_ids = fields.One2many(
        string='EPI',
        comodel_name='suivi.epi.line',
        inverse_name='poste_id1',
        store=True,
    )
    
    
    identification_id1 = fields.Char(
        string='N° d\'identification',
        compute='_compute_identification_id',
        store =True,
    )

    passport_id1 = fields.Char(
        string='N° de passeport',
        compute='_compute_passport_id',
        store =True,
    )

    gender1 = fields.Char(
        string='Genre',
        compute='_compute_gender',
        store =True,
    )
    
    birthday1 = fields.Date(
        string='Date de naissance',
        compute='_compute_birthday',
        store =True,
    )
    place_of_birth1 = fields.Char(
        string='Lieu de naissance',
        compute='_compute_place_of_birth',
        store =True,
    )

    country_of_birth1 = fields.Char(
        string='Pays de naissance',
        compute='_compute_country_of_birth',
        store =True,
    )

    address_home_id1 = fields.Many2one(
        string='Adresse',
        comodel_name='res.partner',
        ondelete='cascade',
        compute='_compute_address_home_id',
        store =True,
    )

    private_emaill = fields.Char(
        string='Courriel',
        compute='_compute_private_email',
        store =True,
    )
    km_h_w = fields.Integer(
        string='Distance domicile-travail',
        compute='_compute_km_home_work',
        store =True,
        default = 0,
    )

    country_id1 = fields.Many2one(
        string='Nationalité (pays)',
        comodel_name='res.country',
        compute='_compute_country_id',
        store =True,
        ondelete='cascade',
    )

    marital1 = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='État civil',
        compute='_compute_marital',
        store=True,
    )

    children1 = fields.Integer(
        string='Nombre d\'enfants',
        compute='_compute_children',
        store=True,
 
    )

    certificate1 = fields.Selection([
        ('graduate', 'Graduate'),
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('doctor', 'Doctor'),
        ('other', 'Other'),
    ], 'Niveau du certificat',
        compute='_compute_certificate',
        store=True,
    )

    
    study_field1 = fields.Char(
        string='Champ d’étude',
        compute='_compute_study_field',
        store=True,
    )

    study_school1 = fields.Char(
        string='École',
        compute='_compute_study_school',
        store=True,
    )

    emergency_phone1 = fields.Char(
        string='Téléphone d\'urgence',
        compute='_compute_emergency_phone',
        store=True,
    )

    emergency_contact1 = fields.Char(
        string='Contact d\'urgence',
        compute='_compute_emergency_contact',
        store=True,
    )
    
    
    
    


    
    
    @api.depends('country_id')
    def _compute_country_id(self):
        for record in self:
            record.country_id1 = record.country_id

    @api.depends('private_email')
    def _compute_private_email(self):
        for record in self:
            record.private_emaill = record.private_emaill
    
    @api.depends('km_home_work')
    def _compute_km_home_work(self):
        for record in self:
            record.km_h_w = record.km_home_work

    @api.depends('marital')
    def _compute_marital(self):
        for record in self:
            record.marital1 = record.marital
    
    @api.depends('children')
    def _compute_children(self):
        for record in self:
            record.children1 = record.children

    @api.depends('certificate')
    def _compute_certificate(self):
        for record in self:
            record.certificate1 = record.certificate
    
    
    @api.depends('address_home_id')
    def _compute_address_home_id(self):
        for record in self:
            record.address_home_id1 = record.address_home_id

    @api.depends('identification_id')
    def _compute_identification_id(self):
        for record in self:
            record.identification_id1 = record.identification_id

    @api.depends('passport_id')
    def _compute_passport_id(self):
        for record in self:
            record.passport_id1 = record.passport_id
    
    @api.depends('gender')
    def _compute_gender(self):
        for record in self:
            record.gender1 = record.gender

    @api.depends('birthday')
    def _compute_birthday(self):
        for record in self:
            record.birthday1 = record.birthday

    @api.depends('place_of_birth')
    def _compute_place_of_birth(self):
        for record in self:
            record.place_of_birth1 = record.place_of_birth
    
    @api.depends('country_of_birth')
    def _compute_country_of_birth(self):
        for record in self:
            record.country_of_birth1 = record.country_of_birth
    
    @api.depends('study_field')
    def _compute_study_field(self):
        for record in self:
            record.study_field1 = record.study_field
    
    @api.depends('study_school')
    def _compute_study_school(self):
        for record in self:
            record.study_school1 = record.study_school

    @api.depends('emergency_contact')
    def _compute_emergency_contact(self):
        for record in self:
            record.emergency_contact1 = record.emergency_contact
    
    @api.depends('emergency_phone')
    def _compute_emergency_phone(self):
        for record in self:
            record.emergency_phone1 = record.emergency_phone
    

    @api.model
    def create_activity(self):
        employee = self.env['hr.employee'].search([])
        
        users = self.env.ref('hr.group_hr_manager').users
        for emp in employee:
            length = len(emp.epi_ids)

            if length <= 0 :
                today = datetime.date.today()
                day = datetime.date.today().strftime('%A')
                if day in  ['Samedi','samedi','saturday','Saturday']:
                    for user in users:
                        data = {
                        'res_id': emp.id,
                        'res_model_id': self.env['ir.model'].search([('model', '=', 'hr.employee')]).id,
                        'user_id': user.id,
                        'summary': 'Attribution des EPI',
                        'note' :f"Pensez a Attribuer les  EPI  de {emp.name}",
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                        'date_deadline': today
                        }
                        self.env['mail.activity'].create(data)

            if  length > 0 :
                for epi in emp.epi_ids:
                    if epi.epi_attributed == True :
                        d1 = epi.date_exp
                        today = datetime.date.today()
                        day = datetime.date.today().strftime('%A')
                        d2 = abs((d1 - today).days)
                        if d2 <= 7  and day in  ['Samedi','samedi','saturday','Saturday']:
                            for user in users:
                                data = {
                                'res_id': emp.id,
                                'res_model_id': self.env['ir.model'].search([('model', '=', 'hr.employee')]).id,
                                'user_id': user.id,
                                'summary': 'MIse a jour des EPI',
                                'note' :f"Pensez a remplacer l'EPI { epi.epi_id.name } de {emp.name} qui expire le {epi.date_exp}",
                                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                                'date_deadline': d1
                                }
                                # act = self.env['mail.activity'].search([('summary', '=', 'MIse a jour des EPI'),('res_id',emp.id)])
                                # if len(act) < 7 :
                                self.env['mail.activity'].create(data)
                        if today == d1 or today > d1:
                            epi.epi_attributed = False
                            epi.date_attribution = None
                            epi.date_exp = None
            
                            
                                
    
    
    


    @api.onchange('job_id')
    def onchange_epi_ids(self):
        if self.job_id :
            epi_line = self.env['suivi.epi.line'].search([('poste_id', '=', self.job_id.id)])
            self.epi_ids = epi_line
        if not self.job_id :
            self.epi_ids = False
    
class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'


    epi_ids = fields.One2many(
        string='EPI',
        comodel_name='suivi.epi.line',
        inverse_name='poste_id1',
        readonly=True,

    )


    address_home_id1 = fields.Many2one(
        string='Adresse',
        comodel_name='res.partner',
        readonly=True,
        ondelete='cascade',
    )

    private_emaill = fields.Char(
        string='Courriel',
        readonly=True,
    )
    km_h_w = fields.Integer(
        string='Distance domicile-travail',
        readonly=True,
        default = 0,
    )
    
    country_id1 = fields.Many2one(
        string='Nationalité (pays)',
        comodel_name='res.country',
        readonly=True,
        ondelete='cascade',
    )

    country_id1 = fields.Many2one(
        string='Nationalité (pays)',
        comodel_name='res.country',
        readonly=True,
        ondelete='cascade',
    )

    
    identification_id1 = fields.Char(
        string='N° d\'identification',
        readonly=True,
    )

    passport_id1 = fields.Char(
        string='N° de passeport',
        readonly=True,
    )

    gender1 = fields.Char(
        string='Genre',
        readonly=True,
    )
    
    birthday1 = fields.Date(
        string='Date de naissance',
        readonly=True,
    )
    place_of_birth1 = fields.Char(
        string='Lieu de naissance',
        readonly=True,
    )

    country_of_birth1 = fields.Char(
        string='Pays de naissance',
        readonly=True,
    )

    marital1 = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='État civil',
        readonly=True,

    )

    children1 = fields.Integer(
        string='Nombre d\'enfants',
        readonly=True,
    )

    certificate1 = fields.Selection([
        ('graduate', 'Graduate'),
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('doctor', 'Doctor'),
        ('other', 'Other'),
    ], 'Niveau du certificat',
    readonly=True,
    )

    
    study_field1 = fields.Char(
        string='Champ d’étude',
        readonly=True,

    )

    study_school1 = fields.Char(
        string='École',
        readonly=True,

    )

    emergency_phone1 = fields.Char(
        string='Téléphone d\'urgence',
        readonly=True,
    )

    emergency_contact1 = fields.Char(
        string='Contact d\'urgence',
        readonly=True,
    )

