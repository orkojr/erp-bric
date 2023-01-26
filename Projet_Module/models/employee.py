from odoo import api,fields,models

class Task_timesheet(models.Model):
        _inherit = "hr.employee"
        _description="Employés"

        # date_jour=fields.Date("Date")
        # nbre_temporaires_chantier=fields.Integer("Nombre de temporaires sur le chantier")
        # nbre_temporaires_tache=fields.Integer("Nombre de temporaires sur la tâche")
        employees_name_id= fields.Many2many('project.task',string='Temporaires')
