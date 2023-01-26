from odoo import api,fields,models
class Chantier(models.Model):
    _name='projet_chantier'
    _description="Modèle de chantiers"
    _rec_name="titre"

    titre = fields.Char('Titre', required=True)
    taches_ids=fields.One2many('taches',"chantier_id",string='Ensemble des tâches')
    # titre_id=fields.One2many('projet.projet',"nom_module_id",string='Titre')
