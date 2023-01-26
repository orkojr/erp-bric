from odoo import api,fields,models
class Taches(models.Model):
    _name='taches'
    _description="Sous-tâches propres aux projets"
    _rec_name="task"

    task=fields.Char('Tâche', required=True)
    code=fields.Char('Code',required=True)
    chantier_id=fields.Many2one('projet_chantier',string='Chantier')
    subtask_ids=fields.One2many('sous_taches',"task_id",string='Sous-tâches')

    