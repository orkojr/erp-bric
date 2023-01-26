from odoo import api,fields,models
class Imputation(models.Model):
    _name='imputation.budgetaire'
    _description="Imputation budgétaire associé aux achats"

    imputation_line_id=fields.Many2one(comodel_name='account.move', string="Imputation")
    budget_id=fields.Many2one(comodel_name='budget.tache', string="Budget associé à l'achat")
    budget_line_id=fields.Many2one(comodel_name='budget.tache.line', string="Activités")
    montant_consomme=fields.Float("Montant consommé")
    montant_total=fields.Float("Montant budgetisé", compute="_compute_cout_total")
    montant_restant=fields.Float("Montant restant", compute="_compute_cout_restant")
    project_id=fields.Many2one(related='imputation_line_id.projet_id')


    @api.model
    def _compute_cout_total(self):
        for cout_t in self:
            cout_t.montant_total=cout_t.budget_line_id.cout_total
            return cout_t.montant_total
    
    @api.model
    def _compute_cout_restant(self):
        for cout_t in self:
            cout_t.montant_restant=cout_t.budget_line_id.cout_total-cout_t.montant_consomme
            return cout_t.montant_restant
    

  
        

class Achat(models.Model):
    _name="account.move"
    _inherit="account.move"

    imputation_line_ids=fields.One2many('imputation.budgetaire',"imputation_line_id",'Ligne imputation')
    projet_id=fields.Many2one(comodel_name='project.project', string='Projet')
    # budget_account_id=fields.Many2one(comodel_name='budget.tache', string='Budget')



    @api.model
    def action_post(self):
        # for cout_reel in self:
        #     for c in cout_reel.invoice_line_ids:
        #         c.poste_depense.c_r=0
        #         for c in cout_reel.imputation_line_ids:
        #             c.montant_consomme=0

        if self.payment_id:
            self.payment_id.action_post()
            
        else:
            self._post(soft=False)
            for cout_reel in self:
                for c in cout_reel.invoice_line_ids:
                    a=c.price_total+c.poste_depense.c_r
                    # a=c.price_subtotal+c.poste_depense.c_r
                    c.poste_depense.c_r=a
                    a=0
                for c in cout_reel.imputation_line_ids:
                    c.montant_consomme = c.budget_line_id.cout_reel

        return False


class Ligne_Achat(models.Model):
    _inherit="account.move.line"

    poste_depense=fields.Many2one(comodel_name='budget.tache.line.price', string='Poste de dépense')
    projet_posteD=fields.Many2one(related='move_id.projet_id')
    a=fields.Char('Test')


    @api.model
    def default_get(self, fields):
        res = super(Ligne_Achat, self).default_get(fields)
        
        return res