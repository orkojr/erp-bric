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



class MrpPorduction(models.Model):
    _inherit ='mrp.production'
    
    
    request_id = fields.Many2one(
        string='Ordre de production',
        comodel_name='stock.request',
        ondelete='restrict',
    )
    
