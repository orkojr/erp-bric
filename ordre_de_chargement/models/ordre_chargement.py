
from odoo import models, fields



class OrdreChargemet(models.Model):
    _name="ordre.chargement"
    _description="designe l'ordre de chargement pour un chantier"


    picking_id = fields.Many2one(
        string='Bon de livraison',
        comodel_name='stock.picking',
        ondelete='restrict',
    )
    
    