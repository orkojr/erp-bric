from email.policy import default
from importlib.metadata import requires
import time
import json
import datetime
from dateutil.relativedelta import relativedelta
from datetime import timedelta
import io
from odoo import fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import date_utils
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter
class SuiviAchat(models.TransientModel):
    _name = "suivi.activite.wizard"



    date_deb = fields.Date(
        "Date debut", 
        required=True,
        default=fields.Datetime.now,
    )
    date_fin = fields.Date(
        "Date fin", 
        required=True,
        default=fields.Datetime.now,
        )
    def print_xlsx(self):

        data = {
            'date_deb': self.date_deb.strftime("%m/%d/%Y"),
            'annee': self.date_deb.strftime("%Y"),
            'mois': self.date_deb.strftime("%m"),
            'date_fin': self.date_fin.strftime("%m/%d/%Y"),
            'date_stock':self.date_deb.strftime('%Y-%m-%d %H:%M:%S'),
            'deb1': self.date_deb.strftime('%d-%m-%y %H:%M:%S'),
            'fin1': self.date_fin.strftime('%d-%m-%y %H:%M:%S'),
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'suivi.activite.wizard',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Suivi activite de l\'entreprise',
                     },
            'report_type': 'stock_xlsx',
        }


    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # create some style to set up the font type, the font size, the border, and the aligment
        title_style = workbook.add_format({'font_name': 'Times','font_size': 13, 'bold': True, 'align': 'center','valign': 'vcenter','bg_color':'#D2D9D9','border_color' : 'white', 'left': 1, 'bottom':1, 'right':1, 'top':1,'text_wrap': True})
        title_style11 = workbook.add_format({'font_name': 'Times','font_size': 13, 'bold': True, 'align': 'center','valign': 'vcenter','bg_color':'#87CEFA','border_color' : 'white', 'left': 1, 'bottom':1, 'right':1, 'top':1,'text_wrap': True})
        title_style1 = workbook.add_format({'font_name': 'Times', 'bold': True, 'align': 'center','valign': 'vcenter','bg_color':'#f07979', 'text_wrap': True})
        title_style21 = workbook.add_format({'font_name': 'Times', 'bold': True, 'align': 'center', 'valign': 'vcenter','left': 2, 'bottom':2, 'right':2, 'top':2, 'text_wrap': True})
        header_style = workbook.add_format({'font_name': 'Times', 'bold': True, 'left': 2, 'bottom':2, 'right':2, 'top':2, 'align': 'center','valign': 'vcenter', 'text_wrap': True})
        text_style = workbook.add_format({'font_name': 'Times', 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'center','valign': 'vcenter', })
        number_style = workbook.add_format({'font_name': 'Times', 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'center','valign': 'vcenter', 'text_wrap': True})




        # deb = datetime.date(data['annee'], 1, 1)
        # fin = datetime.date(data['annee'], 12, 31)
        # deb_1 = deb.strftime('%d-%m-%y %H:%M:%S')
        # fin_1 = fin.strftime('%d-%m-%y %H:%M:%S')
        # day = 365
    
        deb_1 = data['deb1']
        fin_1 = data['fin1']
        # day = 31

        #formate la date pour la requete sql  
        deb_date = datetime.datetime.strptime(deb_1, '%d-%m-%y %H:%M:%S')
        fin_date = datetime.datetime.strptime(fin_1, '%d-%m-%y %H:%M:%S')

    
        req_date1 = deb_date.strftime("%m/%d/%Y")
        req_date11 = deb_date.strftime("%A %d %B %Y")
        req_date_name = deb_date.strftime("%B")
        req_date2 = fin_date.strftime("%m/%d/%Y")
        date_deb = deb_date.strftime('%Y-%m-%d')
        date_fin = fin_date.strftime('%Y-%m-%d')

        #recuperer les  resultats de l'annee precedante

        previous_deb = deb_date + relativedelta(years= -1)
        previous_fin = fin_date + relativedelta(years= -1)

        year = deb_date.strftime('%Y')
        month = deb_date.strftime('%B')
        date = deb_date.strftime('%d/%m/%Y')

        date_deb1 = previous_deb.strftime('%Y-%m-%d')
        date_fin1 = previous_fin.strftime('%Y-%m-%d')
        previous_year = previous_deb.strftime('%Y')
        

        budget_obj =  self.env['crossovered.budget'].search([('date_from', '>=', date_deb), ('date_from', '<=', date_fin)])


        lines = []

        # recuperer les valeurs des budgets.

        sheet = workbook.add_worksheet("suivi ")
        # set the orientation to landscape
        sheet.set_landscape()
        # set up the paper size, 9 means A4
        # sheet.set_paper(9)
        # set up the margin in inch
        sheet.set_margins(0.5,0.5,0.5,0.5)
        sheet.hide_gridlines(2)
        # set up the column width
        sheet.set_column('A:A', 14)
        sheet.set_column('B:W', 8)
        sheet.set_row(6, 20)
        sheet.set_row(11, 15)
        sheet.set_row(12, 30)
        sheet.set_row(23, 30)

        sheet.merge_range(6,7,6,15, 'REPORTING MENSUEL', title_style1)

        sheet.merge_range(0,21,0,22, 'Exercice : %s'%(year))
        sheet.merge_range(1,21,1,22, 'MOIS : %s'%(month))
        sheet.merge_range(2,21,2,22, 'DATE : %s'%(date))

        sheet.merge_range(11,1,11,3, 'Chiffre d\'affaire', title_style)
        sheet.merge_range(11,4,11,5, 'Ecart CA', title_style)
        sheet.merge_range(11,6,11,8, 'Charges', title_style)
        sheet.merge_range(11,9,11,10, 'Ecart Charges', title_style)
        sheet.merge_range(11,11,11,13, 'Marges', title_style)
        sheet.merge_range(11,14,11,15, 'Ecart Marges', title_style)
        sheet.merge_range(11,16,11,18, 'Taux de marge', title_style)
        sheet.merge_range(11,19,11,20, 'Ecart Tx de mg', title_style)
        sheet.merge_range(11,21,11,22, 'Evol tx de mg', title_style)
        sheet.write('A13', 'Villes', title_style11)
        sheet.write('B13', 'Histo (%s)'%(previous_year), title_style11)
        sheet.write('C13', 'Budget (%s)'%(year), title_style11)
        sheet.write('D13', 'Réel (%s)'%(year), title_style11)
        sheet.write('E13', '(R-H)', title_style11)
        sheet.write('F13', '(R-B)', title_style11)
        sheet.write('G13', 'Histo (%s)'%(previous_year), title_style11)
        sheet.write('H13', 'Budget (%s)'%(year), title_style11)
        sheet.write('I13', 'Réel (%s)'%(year), title_style11)
        sheet.write('J13', '(R-H)', title_style11)
        sheet.write('K13', '(R-B)', title_style11)
        sheet.write('L13', 'Histo (%s)'%(previous_year), title_style11)
        sheet.write('M13', 'Budget (%s)'%(year), title_style11)
        sheet.write('N13', 'Réel (%s)'%(year), title_style11)
        sheet.write('O13', '(R-H)', title_style11)
        sheet.write('P13', '(R-B)', title_style11)
        sheet.write('Q13', 'Histo (%s)'%(previous_year), title_style11)
        sheet.write('R13', 'Budget (%s)'%(year), title_style11)
        sheet.write('S13', 'Réel (%s)'%(year), title_style11)
        sheet.write('T13', '(R-H)', title_style11)
        sheet.write('U13', '(R-B)', title_style11)
        sheet.write('V13', '(H/R)', title_style11)
        sheet.write('W13', '(B/R)', title_style11)




        sheet.merge_range(22,1,22,3, 'Chiffre d\'affaire', title_style)
        sheet.merge_range(22,4,22,5, 'Ecart CA', title_style)
        sheet.merge_range(22,6,22,8, 'Charges', title_style)
        sheet.merge_range(22,9,22,10, 'Ecart Charges', title_style)
        sheet.merge_range(22,11,22,13, 'Marges', title_style)
        sheet.merge_range(22,14,22,15, 'Ecart Marges', title_style)
        sheet.merge_range(22,16,22,18, 'Taux de marge', title_style)
        sheet.merge_range(22,19,22,20, 'Ecart Tx de mg', title_style)
        sheet.merge_range(22,21,22,22, 'Evol tx de mg', title_style)
        sheet.write('A24', 'Villes', title_style11)
        sheet.write('B24', 'Histo (%s)'%(previous_year), title_style11)
        sheet.write('C24', 'Budget (%s)'%(year), title_style11)
        sheet.write('D24', 'Réel (%s)'%(year), title_style11)
        sheet.write('E24', '(R-H)', title_style11)
        sheet.write('F24', '(R-B)', title_style11)
        sheet.write('G24', 'Histo (%s)'%(previous_year), title_style11)
        sheet.write('H24', 'Budget (%s)'%(year), title_style11)
        sheet.write('I24', 'Réel (%s)'%(year), title_style11)
        sheet.write('J24', '(R-H)', title_style11)
        sheet.write('K24', '(R-B)', title_style11)
        sheet.write('L24', 'Histo (%s)'%(previous_year), title_style11)
        sheet.write('M24', 'Budget (%s)'%(year), title_style11)
        sheet.write('N24', 'Réel (%s)'%(year), title_style11)
        sheet.write('O24', '(R-H)', title_style11)
        sheet.write('P24', '(R-B)', title_style11)
        sheet.write('Q24', 'Histo (%s)'%(previous_year), title_style11)
        sheet.write('R24', 'Budget (%s)'%(year), title_style11)
        sheet.write('S24', 'Réel (%s)'%(year), title_style11)
        sheet.write('T24', '(R-H)', title_style11)
        sheet.write('U24', '(R-B)', title_style11)
        sheet.write('V24', '(H/R)', title_style11)
        sheet.write('W24', '(B/R)', title_style11)


        

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
 
        return response