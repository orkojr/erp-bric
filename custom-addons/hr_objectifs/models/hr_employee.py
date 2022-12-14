# -*- coding: utf-8 -*-
import time
from datetime import datetime
from odoo import fields, models, api, _
from odoo import exceptions
from odoo.exceptions import UserError, ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    

    
    @api.depends('objectifs_ids')
    def _compute_objectifs_count(self):
        for rec in self:
            rec.objectif_total_count = self.env['employee.objectif'].search_count([('employee_id', '=', rec.id)])
            # rec.objectif_total_count = len(rec.objectifs_ids)
    
    
    objectifs_ids = fields.One2many(string='Objectifs',comodel_name='employee.objectif',inverse_name='employee_id1')
    objectif_total_count = fields.Integer(string='Total objectifs',compute='_compute_objectifs_count' , store=True)
    
    
        
   
    


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    

    
    objectifs_ids = fields.One2many(
        string='Objectifs',
        comodel_name='employee.objectif',
        inverse_name='employee_id1',
        readonly=True
    )
    objectif_total_count = fields.Integer(
        string='Nombre d\'objectif', 
        readonly=True,
    )
    
    
    

    