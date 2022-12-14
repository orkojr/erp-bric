# -*- coding:utf-8 -*-

import babel
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError



class PurchaseApprovLine(models.Model):
    _name = 'purchase.approvisionnement.line'
    _description = 'Autres couts d\'aprovisionnement des matieres premieres'
    _rec_name = "product_id"
    


    product_id = fields.Many2one('product.product', string='Article', required=True)
    product_qty = fields.Float(
        'Quantite', default=1.0,
        digits='Product Unit of Measure', required=True)
    product_uom_qty = fields.Float(
        'Quantite', default=1.0,
        digits='Product Unit of Measure', required=True)
    product_uom_id = fields.Many2one(
        'uom.uom', 'Unite de mesure',      
        required=True,
        help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control")
    pu = fields.Float(
        string='Prix Unitaire',
        default=0.0,
        required=True,
    )
    total = fields.Float(
        string='Total',
        compute='_compute_total_value',
        store=True,
    )
    
    purchase_approv_id = fields.Many2one(
        string='Purchase Approvisionnement',
        comodel_name='purchase.approvisionnement',
        ondelete='cascade',
        
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.product_uom_id = self.product_id.product_tmpl_id.uom_po_id
    
    


    @api.depends('product_qty', 'pu')
    def _compute_total_value(self):
        for record in self:
            record.total = record.product_qty * record.pu
    