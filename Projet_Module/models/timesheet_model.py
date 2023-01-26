from odoo import api,fields,models

class Timesheet_fields(models.Model):
        _inherit = "account.analytic.line"
        _description="Ajout des champs dans les feuilles de temps"

        plan_id=fields.Many2one(comodel_name='project.task',string='Nom employé')
        jour_passe=fields.Float('Durée totale effectuée') 
        date_ajout=fields.Date("Date")
