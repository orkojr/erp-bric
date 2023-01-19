# -*- coding: utf-8 -*-
from email.policy import default
import time
from datetime import datetime, timedelta
import datetime
from odoo import fields, models, api, _
from odoo import exceptions
from odoo.exceptions import UserError, ValidationError


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'
    _description = 'Maintenace Equipement'
    
    
    organe_ids = fields.One2many('maintenance.organe', 'parent_id', string="Organe")
    secteur = fields.Selection(string='Secteur',selection=[('unite_production', 'Unite de production'), ('parc_info', 'Parc informatique'), ('autres', 'Autres')],default='unite_production')
    checkpoint_ids = fields.One2many(string='Point de controle',comodel_name='maintenance.checkpoint.line',inverse_name='equipment_id',)
    # piece_ids = fields.One2many(string='Pièces',comodel_name='maintenance.piece.line',inverse_name='equipment_id',)
    
    
    
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
            # 'piece_ids' : self.piece_ids,
        }


class MaintenanceOrgane(models.Model):
    _name = 'maintenance.organe'
    _description = 'Maintenace Organe'

    parent_id = fields.Many2one('maintenance.equipment', string='Organe')
    organe_id = fields.Many2one('maintenance.equipment', string='Organe')



# class MaintenanceEquipmentPiece(models.Model):
#     _name = 'maintenance.piece'
#     _description = "Piece"

#     name = fields.Char(string='Nom de la pièce',required=True)
#     duree = fields.Integer(string='Temps d\'utilisation',)
    
    


# class MaintenanceEquipmentPieceLine(models.Model):
#     _name = 'maintenance.piece.line'
#     _description = "Piece Equipement"
    
    
#     piece_id = fields.Many2one(string='Pièce',comodel_name='maintenance.piece',ondelete='restrict',required=True,)
#     mise_en_marche = fields.Datetime(string='Date de mise en marche',required=True,)
#     en_marche = fields.Boolean(string='En Marche',default=True,)
#     progress = fields.Integer(string='Utilisation(%)', compute='_compute_progress',store=True)
#     equipment_id = fields.Many2one(string='Equipement',comodel_name='maintenance.equipment',ondelete='restrict',)
#     request_id = fields.Many2one(string='Maintenace Request', comodel_name='maintenance.request', ondelete='restrict')
    
    
    
    
#     @api.depends('piece_id','en_marche')
#     def _compute_progress(self):
#         today = datetime.date.today()
#         for record in self:
#             prog = 0
#             duree = 0
#             if record.en_marche:
#                 mrp = self.env['mrp.production'].search([('date_planned_start', '>=',record.mise_en_marche),('date_planned_start', '<=', today)])
#                 if len(mrp) > 0:
#                     for mr in mrp:
#                         if mr.equipment_id.id == record.id:
#                             prog += mr.duree_production
#             if record.piece_id.duree > 0:
#                 duree = (prog/record.piece_id.duree)*100
#             record.progress = duree
                            
    
    
    
    
# class MrpProduction(models.Model):
#     _inherit = 'mrp.production'

#     equipment_id = fields.Many2one(string='Equipement',comodel_name='maintenance.equipment',ondelete='restrict',)
#     duree_production = fields.Float(string='Durée Production',)
    
    
   