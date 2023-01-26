from odoo import api,fields,models
class Budget(models.Model):
    _name='budget.tache'
    _description="budget des tâches"
    _rec_name="name"

    name=fields.Char("Nom du budget")
    project_id=fields.Many2one(comodel_name='project.project', string='Projet')
    som_cout_total=fields.Float("Coût total", compute='_compute_som_cout_total')
    som_cout_reel=fields.Float("Coût réel", compute='_compute_som_cout_reel')
    date_deb=fields.Date("Date de début")
    date_fin=fields.Date("Date de fin")
    budget_line_ids=fields.One2many('budget.tache.line',"budget_line_task_id",'Budget')
    budget_id=fields.Many2one(comodel_name='project.task', string='Taches')
    imputation_ids=fields.One2many('imputation.budgetaire',"budget_id")

    @api.model
    def _compute_som_cout_total(self):
        som=0
        som1=0
        for cout in self:
            for cout1 in cout.budget_line_ids:
                som1=som1+cout1.cout_total
            som=som+som1
            cout.som_cout_total=som
        return cout.som_cout_total

    
    @api.model
    def _compute_som_cout_reel(self):
        som=0
        som1=0
        for cout in self:
            for cout1 in cout.budget_line_ids:
                som1=som1+cout1.cout_reel
            som=som+som1
            cout.som_cout_reel=som
        return cout.som_cout_reel


class BudgetLine(models.Model):
    _name='budget.tache.line'
    _description="ligne budget des tâches"
    _rec_name="task_budget"

    proj_id=fields.Many2one(related='budget_line_task_id.project_id')
    cout_total=fields.Float("Coût total", compute='_compute_cout_total')
    cout_reel=fields.Float("Coût réel", compute='_compute_cout_reel')
    analytic_account_action_id=fields.Many2one(comodel_name='account.analytic.account', string='Action')
    task_budget_id=fields.Many2one(comodel_name='project.task',string='Taches liées au projet')
    task_budget=fields.Char("Activités")
    budget_line_task_id=fields.Many2one(comodel_name='budget.tache',string='Ligne Budget')
    prix_budget_line_ids=fields.One2many('budget.tache.line.price',"line_prix_id",'Poste de dépense')
    budget_line_id=fields.Many2one(comodel_name='project.task', string='Taches')


    @api.model
    def _compute_cout_total(self):
        som2=0
        som3=0
        for cout in self:
            som3=0
            for cout1 in cout.prix_budget_line_ids:
                som3=som3+cout1.c_t
            cout.cout_total=som3
        return cout.cout_total

    @api.model
    def _compute_cout_reel(self):
        som2=0
        som3=0
        for cout in self:
            som3=0
            for cout1 in cout.prix_budget_line_ids:
                som3=som3+cout1.c_r
            cout.cout_reel=som3
        return cout.cout_reel



class BudgetLine_Prix(models.Model):
    _name='budget.tache.line.price'
    _description="calcul des coûts ligne budget des tâches"
    _rec_name="analytic_account_posteD_id"
    quantite=fields.Float("Quantité")
    prix_u=fields.Float("Prix unitaire")
    c_t=fields.Float("Coût total", compute='_compute_cout_total_line_prix')
    c_r=fields.Float("Coût réel")
    action_parent=fields.Many2one(related='line_prix_id.analytic_account_action_id')
    analytic_account_posteD_id=fields.Many2one(comodel_name='account.analytic.account', string='Poste de dépense')
    line_prix_id=fields.Many2one(comodel_name='budget.tache.line', string='Ligne analytique')
    project=fields.Many2one(related='line_prix_id.proj_id')
    # poste_dep_account_ids=fields.One2many('account.move.line',"poste_depense")


    @api.depends('quantite','prix_u')
    def _compute_cout_total_line_prix(self):
        for cout in self:
            cout.c_t=cout.quantite*cout.prix_u
        return cout.c_t


   


