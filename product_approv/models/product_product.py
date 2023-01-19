# -*- coding: utf-8 -*-
from email.policy import default
import time
from datetime import datetime, timedelta
import datetime
from odoo import fields, models, api, _
from odoo import exceptions
from odoo.exceptions import UserError, ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'


    min_quantity = fields.Float(string='Quantité min', store=True, default=0, help="Lorsque la Quantité disponible est inférieur ou egale a cette quantité une alerte est Envoyée.")
    
 
class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def create_activity(self):
        products = self.env['product.product'].search([('detailed_type', 'in', ['consu', 'product'])])
        today = datetime.date.today()
        users = self.env.ref('stock.group_stock_manager').users
        users2 = self.env.ref('purchase.group_purchase_manager').users
        usrs = []
        for u in users:
            usrs.append(u)
        for u in users2:
            if u in usrs:
                continue
            usrs.append(u)
        users = usrs
        for product in products:
            if product.min_quantity == 0:
                continue
            if product.qty_available <= product.min_quantity:
                for user in users:
                    data = {
                    'res_id': product.id,
                    'res_model_id': self.env['ir.model'].search([('model', '=', 'product.product')]).id,
                    'user_id': user.id,
                    'summary': 'Règle de Réapprovisionnement',
                    'note' :f"La quantité disponible du produit ``{ product.product_tmpl_id.name } `` est inférieur à la quantité minimale.",
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'date_deadline': today
                    }

                    self.env['mail.activity'].create(data)
               