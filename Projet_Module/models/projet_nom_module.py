from odoo import api,fields,models
class Nom_modele(models.Model):
    _inherit="project.project"
    _description="Modèle de liason entre project et chantier"

    nom_module_id=fields.Many2one(comodel_name='projet_chantier',string='Nom du modèle')
    budget_ids=fields.One2many('budget.tache',"project_id",'Budget projet')

    
    def get_id(self):
        id=self.id,
        return id

    
    #vérification si la création du projet et ses tâches est déja effective
    
    def action_view_tasks2(self):
            action = self.with_context(active_id=self.id, active_ids=self.ids) \
                .env.ref('project.act_project_project_2_project_task_all') \
                .sudo().read()[0]
            action['display_name'] = self.name

            project_task_List_type ={
             'name': "Ensemble des activités",
             'legend_normal': "En cours",
             'legend_blocked': "Bloqué",
             'legend_done': "Teminé",
             'project_ids':self.get_id(),

            }
            project_task_type=self.env['project.task.type'].create(project_task_List_type),

            for i in self.nom_module_id.taches_ids :
                project_task_List ={
                    'name':i.task,
                    'project_id':self.get_id(),
                    'stage_id':project_task_type[0].id
                    
                }
                project_task=self.env['project.task'].create(project_task_List),
                # parent=project_task.fetchall()

                for subtask in i.subtask_ids :

                    project_subtask_List={
                            'name':subtask.Subtask,
                            'project_id':self.get_id(),
                            'parent_id':project_task[0].id,
                        }
                    project_subtask=self.env['project.task'].create(project_subtask_List),

            
            return action

