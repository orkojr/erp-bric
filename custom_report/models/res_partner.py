# -*- coding: utf-8 -*-



from odoo import models, fields


class Partner(models.Model):
    _inherit = 'res.partner'

    supplier_id = fields.Many2many('report.stock.history', 'supp_wiz_rel1', 'wiz', 'supp', invisible=True)


class Category(models.Model):
    _inherit = 'product.category'

    obj = fields.Many2many('report.stock.history', 'categ_wiz_rel1', 'wiz', 'categ', invisible=True)


class Warehouse(models.Model):
    _inherit = 'stock.warehouse'

    obj = fields.Many2many('report.stock.history',  'wh_wiz_rel1', 'wiz', 'wh', invisible=True)
