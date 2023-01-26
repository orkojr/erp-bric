from odoo import api,fields,models
class Sous_Taches(models.Model):
    _name='sous_taches'
    _description="Sous-tâches"
    _rec_name="Subtask"
    
    Subtask = fields.Char('Nom de la sous-tâche', required=True)
    quantite=fields.Integer('Quantité')
    task_id=fields.Many2one('taches',string='Code Activité')