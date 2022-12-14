# -*- coding: utf-8 -*-

from odoo import api, fields, models




    

class AutreCout(models.Model):
    _name = "purchase.request.line.cout"
    _description = 'Autre cout d\'achats'
    
    @api.depends('prix_unitaire', 'quantite_piece')
    def _cout_compute(self):
        for line in self:
            line.cout = line.prix_unitaire*line.quantite_piece

   
    @api.depends('product_id')
    def _compute_prix_unitaire(self):
        for line in self:
            line.prix_unitaire = line.product_id.standard_price


    cout = fields.Float(
        string='Cout',
        compute='_cout_compute',
        store=True,
        default=0.0
    )


    
    request_cout_id = fields.Many2one(
        string='Autre',
        comodel_name='purchase.request.line',
        ondelete='cascade',
    )
    

    quantite_piece = fields.Integer(
        string='Quantite utilisee',
        default=0
    )

    
   
    
    product_id = fields.Many2one('product.product','Article',domain=[("purchase_ok", "=", True)]) 
    
    prix_unitaire = fields.Float(
        string='Prix Unitaire',
        store=True,
    )
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom", string="UoM", required=False
    )
    
        
    

    
    
    
    
    
    