# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import datetime


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    estimated_cost = fields.Monetary(
        compute="_compute_estimated_cost",
        string="Coût Total",
        store=True,
    )

class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

    estimated_cost = fields.Monetary(
        compute="_compute_amount",
        string = "Coût Total",
        default=0.0,
        help="Coût estimé de la ligne de demande d'achat, non propagé à la commande.",
    )

class EmployeRequest(models.Model):
    _inherit = "employe.request"

    estimated_cost = fields.Monetary(
        compute="_compute_estimated_cost",
        string="Coût Total",
        store=True,
    )

class EmployeRequestLine(models.Model):
    _inherit = "employe.request.line"

    estimated_cost = fields.Monetary(
        compute="_compute_amount",
        string = "Coût Total",
        default=0.0,
        help="Coût estimé de la ligne de demande d'achat, non propagé à la commande.",
    )

    
