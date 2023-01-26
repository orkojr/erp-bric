from odoo import api,fields,models

class Task_timesheet(models.Model):
        _name = "project.task"
        _inherit = "project.task"
        _description="Périodicité des tâches du projet à effectuer"
        
        #date de début effective de la tâche
        debut_effectif = fields.Date("Date de début effective") 
        #date de fin effective de la tâche
        fin_effective = fields.Date("Date de fin effective")
        #durée effective de la tâche
        duree_effective=fields.Float("Durée effective de la tâche", compute='_compute_depassement_duree')

        #Durée et date planifiées pour la mise sur pied de la tâche
        duree_plan_debut=fields.Float("Durée prévue")
        date_debut_plan=fields.Date("Date de début planifiée")
        date_fin_plan=fields.Date("Date de fin plannifiée")

        # timesheet_task_id=fields.Many2one(comodel_name='project.task',string='Date_tâche')
        encode_uom_in_days=fields.Boolean("False")
        #Tache-engins
        tache_engin_ids=fields.One2many('fleet.vehicle.line',"engin_taches_id",string='Engins utilisés')
        #Budget taches
        budget_tache_ids=fields.One2many('budget.tache',"budget_id",string='Budget')

        #taches ligne budgétaire
        budget_tache_line_ids=fields.One2many('budget.tache.line',"task_budget_id",string='Ligne Budgetaire')

        #Employés
        planif_employee_ids=fields.Many2many('hr.employee',string='Temporaires affectés à la tâche')


        #Etat effectif d'une tâche (démarrage et durée allouée à chaque tâche)
        statut_demarrage=fields.Char('Statut', compute='_compute_statut_demarrage')
        depassement_duree=fields.Float("Dépassement des délais plannifiés", compute='_compute_depassement_duree')


        @api.depends('duree_effective','subtask_effective_hours')
        def _compute_effective_hours(self):
         for task in self:
          #multiplié par 8 car par défaut divisé par 8 avant l'affichage sur la page feuille de temps
          task.effective_hours = task.duree_effective*8

        @api.depends('effective_hours', 'subtask_effective_hours', 'planned_hours')
        def _compute_progress_hours(self):
                for task in self:
                        if (task.planned_hours > 0.0):
                            task_total_hours = task.effective_hours + task.subtask_effective_hours
                            task.overtime = max(task_total_hours - task.planned_hours, 0)
                            if task_total_hours > task.planned_hours:
                                task.progress = 100
                            else:
                                 task.progress = round(100.0 * task_total_hours / task.planned_hours, 2)
                        else:
                           task.progress = 0.0
                           task.overtime = 0

        @api.depends('debut_effectif','fin_effective')
        def _compute_statut_demarrage(self):
         for task in self:
                if (task.debut_effectif==False and task.fin_effective==False):
                        task.statut_demarrage="N/A"
                        
                else:
                        if(task.debut_effectif==False or task.fin_effective==False or task.date_debut_plan==False):
                         task.statut_demarrage="N/A"
                        else:
                         if(task.debut_effectif==task.date_debut_plan):
                          task.statut_demarrage="Démarrage sans retard"
                         if(task.debut_effectif>task.date_debut_plan):
                          task.statut_demarrage="Démarrage retardé"
                         if(task.debut_effectif<task.date_debut_plan):
                          task.statut_demarrage="Démarrage en avance"
        

        @api.depends('debut_effectif','fin_effective')
        def _compute_depassement_duree(self):
         
         for task in self:
                if (task.debut_effectif==False or task.fin_effective==False or task.date_debut_plan==False):
                        task.depassement_duree=0
                        task.duree_effective=0
                else:
                        task.duree_effective=(task.fin_effective-task.debut_effectif).days+1
                        a=task.effective_hours-task.planned_hours
                        if(a>0):
                                task.depassement_duree=a/8
                        if(a<=0):
                                task.depassement_duree=0
        



        @api.depends('effective_hours', 'subtask_effective_hours')
        def _compute_total_hours_spent(self):
         for task in self:
                if (task.subtask_effective_hours==0):
                        task.total_hours_spent = task.effective_hours + task.subtask_effective_hours
                else:
                        task.total_hours_spent = task.subtask_effective_hours

        @api.depends('effective_hours', 'subtask_effective_hours', 'planned_hours')
        def _compute_remaining_hours(self):
                for task in self:
                        if (task.subtask_effective_hours==0):
                                task.remaining_hours = task.planned_hours - task.effective_hours
                        else:
                                task.remaining_hours = task.planned_hours - task.subtask_effective_hours

                        
        

                
                        
                        







    


