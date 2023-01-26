import time
from datetime import date, datetime
import pytz
import json
import datetime
import io
from odoo import api, fields, models, _
from odoo.tools import date_utils
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

class Wizard_export(models.TransientModel):
    _name='project.model.export'

    chantier_export_id = fields.Many2many('projet_chantier', string='Titre du modèle')
    debut = fields.Date("Date de début")
    fin = fields.Date("Date de fin")

    def get_excel_report(self):
        # redirect to /Configuration/excel_report controller to generate the excel file
        return {
            'type': 'ir.actions.act_url',
            'url': '/project/excel_report/%s' % (self.id),
            'target': 'new',
        }
 

