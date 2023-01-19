# -*- coding:utf-8 -*-

from email.policy import default
from importlib.metadata import requires
import time
import json
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import io
from odoo import fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import date_utils
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter
class MrpPlanMensuel(models.Model):
    _name = 'plan.mensuel.line'


    debut_date = fields.Datetime('Date Debut', required=True,)
    fin_date = fields.Datetime('Date Fin', required=True,)
    production_id = fields.Many2one('mrp.production','Production', required=True,)

    
    plan_id = fields.Many2one(
        string='Planning',
        comodel_name='mrp.plan',
        ondelete='cascade',
    )
    
    def duplicate_line(self, default=None):
        default = default or {}
        return super(MrpPlanMensuel, self).copy(default)
    
    

    
