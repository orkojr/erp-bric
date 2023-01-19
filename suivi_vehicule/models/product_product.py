# -*- coding: utf-8 -*-
from email.policy import default
import time
from datetime import datetime, timedelta
import datetime
from odoo import fields, models, api, _
from odoo import exceptions
from odoo.exceptions import UserError, ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'


    suivi_vehicule = fields.Boolean(string='Suivi de vehicule obligatoire',)
  
  
# class MaintenanceEquipment(models.Model):
#     _inherit = 'maintenance.equipment'


    
#     duree_de_vie = fields.Float(string='Durée de vie')
#     date_mise = fields.Date(string='Date de mise en marche')
    
#     @api.model
#     def create_activity(self):
#         equipment = self.env['maintenance.equipment'].search([])
        
#         users = self.env.ref('maintenance.group_equipment_manager').users
#         for eq in equipment:
#             if eq.duree_de_vie > 0 :
#                 print(type(eq.date_mise),"ffffffffffffffffffff")
#                 date_fin = eq.date_mise + timedelta(days=eq.date_mise)
#                 today = datetime.date.today()
#                 d2 = abs((today - date_fin).days)
#                 if d2 <= 7 :
#                     for user in users:
#                         data = {
#                         'res_id': eq.id,
#                         'res_model_id': self.env['ir.model'].search([('model', '=', 'maintenance.equipment')]).id,
#                         'user_id': user.id,
#                         'summary': 'Maintenance Equipement',
#                         'note' :f"Pensez a faire une maintenance sur l'rquipement {eq.name}",
#                         'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
#                         'date_deadline': date_fin
#                         }
#                         self.env['mail.activity'].create(data)


