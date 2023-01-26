from odoo import api,fields,models

class Engin(models.Model):
    _name="fleet.vehicle"
    _inherit="fleet.vehicle"
    _description="Modèle de liason entre parc automobile et task"
    _rec_name="nom"
    # nom_engin=fields.Char("Désignation")
    nom=fields.Char("Désignation")
    line_engin_ids=fields.One2many('fleet.vehicle.line',"nom_engin",'Ligne engin')


class Engin_line(models.Model):
    _name="fleet.vehicle.line"
    _description="Modèle de liason entre parc automobile et task"

    nom_engin=fields.Many2one(comodel_name='fleet.vehicle', string='Désignation')
    quantite=fields.Float("Quantité")
    nbre_jour=fields.Float("Nombre de jours")
    nbre_jour_total=fields.Float("Nombre de jours total", compute='_compute_nbre_jour_total')
    prix_unitaire=fields.Float("Prix unitaire")
    engin_taches_id=fields.Many2one(comodel_name='project.task',string='Nom engin')
    prix_total = fields.Float(
        string='Prix total',
        compute='_compute_prix',
        digits=(14,0),
        store=True,   
        compute_sudo=True
    )

    @api.depends('quantite','nbre_jour')
    def _compute_nbre_jour_total(self):
        for engin in self:
            engin.nbre_jour_total=engin.nbre_jour*engin.quantite
        return engin.nbre_jour_total

    @api.depends('prix_unitaire','nbre_jour_total')
    def _compute_prix(self):
        for engin in self:
           engin.prix_total=engin.prix_unitaire*engin.nbre_jour_total
        return engin.prix_total

    # @api
    # def name_get(self):
        result= []
        # for rec in self:
        #     result.append((rec.id,'%s'%(rec.nom_engin))) 
        # return result