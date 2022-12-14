# -*- coding:utf-8 -*-

import babel
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError



class PurchaseApprov(models.Model):
    _name = 'purchase.approvisionnement'
    _description = 'Aprovisionnement des matieres premieres'
    _rec_name = "product_id"
    


    product_id = fields.Many2one('product.product', string='Article', required=True)
    product_qty = fields.Float(
        'Quantite', default=1.0,
        digits='Product Unit of Measure', required=True)
    product_uom_qty = fields.Float(
        'Quantite', default=1.0,
        digits='Product Unit of Measure', required=True)
    product_uom_id = fields.Many2one(
        'uom.uom', 'Unite de mesure Achat',      
        required=True,
        help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control")
    pu = fields.Float(
        string='Prix Unitaire',
        default=0.0,
        required=True,
    )

    
    date = fields.Date(
        string='Date d\'achat',
        default=fields.Date.context_today,
    )
    
    quantite_total = fields.Float(
        string='Quantite total par achat',
        compute='_compute_quantite_total',
        store=True,
    )
    prix_pu = fields.Float(
        string='Prix par unite',
        compute='_compute_prix_pu',
        store=True,
    )
    total = fields.Float(
        string='Total',
        compute='_compute_total_value',
        store=True,
    )
    cout_total = fields.Float(
        string='Cout d\'achat',
        compute='_compute_cout_achat',
        store=True,
    )   
    eq = fields.Float(
        string='Equivalent Unite de production',
        help="Ex 1t = 1000Kg"
    )

    unite_mesure = fields.Many2one(
        'uom.uom', 'Unite de mesure Production',      
        required=True)

    
    
    line_ids = fields.One2many('purchase.approvisionnement.line', 'purchase_approv_id', string='Elements')


    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.product_uom_id = self.product_id.product_tmpl_id.uom_po_id
    
    


    @api.depends('product_qty', 'pu')
    def _compute_total_value(self):
        for record in self:
            record.total = record.product_qty * record.pu
    
    @api.depends('total', 'line_ids')
    def _compute_cout_achat(self):
        for record in self:
            total = record.total
            for line in record.line_ids :
                total += line.total
            record.cout_total = total

    @api.onchange('product_uom_id')
    def _onchange_unite(self):
        if self.product_uom_id.name == 'kg' or self.product_uom_id.name == 'L':
            self.eq = self.product_qty

    
    
    @api.depends('cout_total', 'quantite_total')
    def _compute_prix_pu(self):
        for record in self:
            if record.quantite_total == 0 :
                record.prix_pu = 0
            else :
                record.prix_pu = record.cout_total / record.quantite_total
    
    
    


    @api.depends('product_qty', 'product_uom_id','eq','unite_mesure')
    def _compute_quantite_total(self):
        for record in self:
            if record.unite_mesure == record.product_uom_id :
                record.quantite_total = record.product_qty
            else :
                record.quantite_total = record.product_qty * record.eq
    


    
    
    


    