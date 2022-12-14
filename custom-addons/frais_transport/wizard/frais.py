from email.policy import default
from importlib.metadata import requires
import time
import json
import datetime
from datetime import timedelta
import io
from odoo import fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import date_utils
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter
class FraisTransport(models.TransientModel):
    _name = "frais.transport.wizard"

    
    def print_xlsx(self):

        data = {
            
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'frais.transport.wizard',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'FRAIS DE TRANSPORT',
                     },
            'report_type': 'stock_xlsx',
        }


    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # create some style to set up the font type, the font size, the border, and the aligment
        title_style = workbook.add_format({'font_name': 'Times', 'font_size': 20, 'bold': True, 'align': 'center','valign': 'vcenter','left': 2, 'bottom':2, 'right':2, 'top':2, 'text_wrap': True, 'bg_color': '#8B495E'})
        title_style21 = workbook.add_format({'font_name': 'Times', 'bold': True, 'align': 'center', 'valign': 'vcenter','left': 1, 'bottom':1, 'right':1, 'top':1, 'text_wrap': True})
        title_style1 = workbook.add_format({'font_name': 'Times', 'font_color':'red','font_size': 23, 'bold': True, 'align': 'center', 'valign': 'vcenter','left': 1, 'bottom':1, 'right':1, 'top':1, 'text_wrap': True})
        header_style = workbook.add_format({'font_name': 'Times', 'bold': True, 'left': 2, 'bottom':2, 'right':2, 'top':2, 'align': 'center','valign': 'vcenter', 'text_wrap': True})
        text_style = workbook.add_format({'font_name': 'Times', 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'center','valign': 'vcenter', })
        number_style = workbook.add_format({'font_name': 'Times', 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'center','valign': 'vcenter', 'text_wrap': True, })




        sheet = workbook.add_worksheet("FRAIS DE TRANSPORT")
        # set the orientation to landscape
        sheet.set_landscape()
        # set up the paper size, 9 means A4
        sheet.set_paper(9)
        # set up the margin in inch
        sheet.set_margins(0.5,0.5,0.5,0.5)
        sheet.hide_gridlines(2)
        # set up the column width
        sheet.set_column('B:B', 20)
        sheet.set_column('C:C', 37)
        sheet.set_column('D:E', 20)
        sheet.set_row(8, 25)
        sheet.set_row(9, 20)
        sheet.set_row(10, 20)
        sheet.set_row(11, 20)
        sheet.set_row(12, 50)
        sheet.set_row(13, 70)
        sheet.set_row(14, 50)

        zone_obj = self.env['bric1.zone'].search([])
        lines = []
        for zone  in zone_obj :
            name = zone.designation
            ville = ""
            quartier_obj = self.env['bric1.quartier'].search([('zone_id', '=', zone.id)])
            for quartier in quartier_obj:
                ville +=quartier.appelation +" - "
            line = {
                'zone' : name,
                'ville' : ville,
                'man' : zone.frais_transport_man,
                'actros' : zone.frais_transport_actros,
            }

            lines.append(line)

        sheet.merge_range(8,1,8,4, 'COUTS  DE LIVRAISON DE PRODUITS A DOUALA', title_style)
        sheet.merge_range(10,3,10,4, "FRAIS DE TRANSPORT", title_style21)


        sheet.write('B12', 'ZONE', title_style21)
        sheet.write('C12', 'VILLES', title_style21)
        sheet.write('D12', 'MAN', title_style21)
        sheet.write('E12', 'ACTROS', title_style21)
        row =12
        col = 0
        for line in lines :
            sheet.write(row, col + 1, line['zone'], title_style21)
            sheet.write(row, col + 2, line['ville'], title_style21)
            sheet.write(row, col + 3, line['man'], number_style)
            sheet.write(row, col + 4, line['actros'], number_style)
            row += 1

            
        
        
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

        return response