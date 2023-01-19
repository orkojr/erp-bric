# -*- coding: utf-8 -*-

from email.policy import default
from itertools import product
from odoo import api, fields, models, SUPERUSER_ID, _


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'
    _description = 'Maintenace Equipement'
    
    
    organe_ids = fields.One2many('maintenance.organe', 'parent_id', string="Organe")
    secteur = fields.Selection(string='Secteur',selection=[('unite_production', 'Unite de production'), ('parc_info', 'Parc informatique'), ('autres', 'Autres')],default='unite_production')
    checkpoint_ids = fields.One2many(
        string='Point de controle',
        comodel_name='maintenance.checkpoint.line',
        inverse_name='equipment_id',
    )

    def _prepare_maintenance_request_vals(self, date):
        self.ensure_one()
        return {
            'name': _('Preventive Maintenance - %s', self.name),
            'request_date': date,
            'schedule_date': date,
            'category_id': self.category_id.id,
            'equipment_id': self.id,
            'maintenance_type': 'preventive',
            'owner_user_id': self.owner_user_id.id,
            'user_id': self.technician_user_id.id,
            'maintenance_team_id': self.maintenance_team_id.id,
            'duration': self.maintenance_duration,
            'company_id': self.company_id.id or self.env.company.id,
            'chekpoint_ids': self.checkpoint_ids,
        }


class MaintenanceOrgane(models.Model):
    _name = 'maintenance.organe'
    _description = 'Maintenace Organe'

    parent_id = fields.Many2one('maintenance.equipment', string='Organe')
    organe_id = fields.Many2one('maintenance.equipment', string='Organe')




    
    
    


   

    
    
    
    
    
    