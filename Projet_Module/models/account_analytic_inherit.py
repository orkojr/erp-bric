from odoo import api,fields,models
class Account_analytic(models.Model):
    _name="account.analytic.account"
    _inherit="account.analytic.account"
    _description="Modèle de liason entre le budget et le compte analytique"
    
    type=fields.Selection(string='Type',selection=[('projet', 'Projet'),('administration','Administration'),('maintenance','Maintenance'),('distribution','Distribution'),('approvisionnement','Approvisionnement') ])
    project_id=fields.Many2one(comodel_name='project.project',string='Projet')
        