
from email.policy import default
from odoo import api, fields, models


class MaintenanceCheckpoint(models.Model):
    _name = 'maintenance.checkpoint'
    _description = "POINT DE CONTRÔLE"


    name = fields.Char(string='Point de controle', required = True)

class MaintenanceCheckpointLine(models.Model):
    _name = 'maintenance.checkpoint.line'
    _description = " ligne POINT DE CONTRÔLE"

    checkpoint_id = fields.Many2one(
        string='Point de controle', 
        comodel_name='maintenance.checkpoint', 
        ondelete='cascade'
    ) 
    equipment_id = fields.Many2one(
        string='Maintenace Equipment', 
        comodel_name='maintenance.equipment', 
        ondelete='cascade'
    )
    request_id = fields.Many2one(
        string='Maintenace Request', 
        comodel_name='maintenance.request', 
        ondelete='cascade'
    )
    fait = fields.Boolean(string='Fait', default=False)
    pas_fait = fields.Boolean(string='Pas Fait', default=False)
    autre = fields.Boolean(string='Autre', default=False)
    observation = fields.Char(string='observations')
    
    
    