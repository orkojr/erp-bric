# -*- coding: utf-8 -*-
import time
import datetime
from datetime import timedelta
from odoo import fields, models, api, _
from odoo import exceptions
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"


    @api.model
    def create_activity(self):
        receptions = self.env['stock.picking'].search([('state','in', ['confirmed','assigned'])])
        users = self.env.ref('mrp.group_mrp_manager').users
        users2 = self.env.ref('purchase.group_purchase_manager').users
        usrs = []
        for u in users:
            usrs.append(u)
        for u in users2:
            if u in usrs:
                continue
            usrs.append(u)
        users = usrs
        today = datetime.date.today()
        for reception in receptions:
            if reception.date_deadline :
                if today > reception.date_deadline.date() and today > reception.scheduled_date.date():
                    continue
                else:
                    for user in users:
                        data = {
                        'res_id': reception.id,
                        'res_model_id': self.env['ir.model'].search([('model', '=', 'stock.picking')]).id,
                        'user_id': user.id,
                        'summary': 'Nouvelle réception de stock',
                        'note' :f"La réception  { reception.name } Est prévue le {reception.scheduled_date}",
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                        'date_deadline': reception.date_deadline
                        }
                        self.env['mail.activity'].create(data)
            else :
                if  today > reception.scheduled_date.date():
                    continue
                else:
                    for user in users:
                        data = {
                        'res_id': reception.id,
                        'res_model_id': self.env['ir.model'].search([('model', '=', 'stock.picking')]).id,
                        'user_id': user.id,
                        'summary': 'Nouvelle réception de stock',
                        'note' :f"La réception  { reception.name } Est prévue le {reception.scheduled_date}",
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                        'date_deadline': reception.scheduled_date.date()
                        }
                        self.env['mail.activity'].create(data)