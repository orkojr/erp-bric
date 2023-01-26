# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import content_disposition, request
import io
from io import BytesIO
import base64
import xlsxwriter
from odoo.addons.web.controllers.main import _serialize_exception
from odoo.tools import html_escape


class ReportController(http.Controller):
    @http.route([
        '/project/excel_report/<model("project.model.export"):mymodel>',
    ], type="http", auth="user", csrf=False)

    def get_all_excel_report(self,mymodel=None,**args):
        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('Planning des travaux' + '.xlsx'))
            ]
        )
         # Création d'un workbook à partir de la librairie xlsxwriter
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # Style utilisé dans le document excel
        title_style = workbook.add_format({'font_name': 'Times', 'font_size': 14, 'bold': True, 'align': 'center'})
        title1_style = workbook.add_format({'font_name': 'Times', 'font_size': 16, 'bold': True, 'align': 'center','bg_color':'DDD9C4'})
        header_style = workbook.add_format({'font_name': 'Times','font_size':10, 'bold': True, 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'center','bg_color':'BFBFBF'})
        text_style = workbook.add_format({'font_name': 'Times', 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'left'})
        number_style = workbook.add_format({'font_name': 'Times', 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'right'})
        tache_style= workbook.add_format({'font_name': 'Times','font_size':14, 'bold':True, 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'left', 'bg_color': 'C6E0B4','font_color': 'FF0000'})
        # Ajout des éléments dans la feuille excel
        for mod in mymodel.chantier_export_id:
            # create worksheet/tab per salesperson 
            sheet = workbook.add_worksheet(mod.titre)
            # set the orientation to landscape
            sheet.set_landscape()
            # set up the paper size, 9 means A4
            sheet.set_paper(9)
            # set up the margin in inch
            sheet.set_margins(0.5,0.5,0.5,0.5)

            # set up the column width
            sheet.set_column('A:A',18)
            sheet.set_column('B:B',8)
            sheet.set_column('C:C',45)
            sheet.set_column('D:D',7)
            sheet.set_column('E:E',10)
            sheet.set_column('F:F',15)

           
            # the report title
            # merge the A1 to E1 cell and apply the style font size : 14, font weight : bold
            sheet.merge_range('A3:F3', 'Planning des travaux de construction', title1_style)
            #the report subtitle
            sheet.merge_range('C5:E5', 'Désignation des travaux', title_style)

            # table title
            sheet.write(7, 0, 'NUMERO TACHE', header_style)
            sheet.write(7, 1, 'TACHE A', header_style)
            sheet.write(7, 2, 'Nature des travaux', header_style)
            sheet.write(7, 3, 'QTE', header_style)
            sheet.write(7, 4, 'Quantité/J', header_style)
            sheet.write(7, 5, 'Délai J/Semaine', header_style)
            row=8
            number=1
            row_sub=7

            # Freeze pane on the top row.
            sheet.freeze_panes(8, 0)

            # search the sales order  
            orders = request.env['projet_chantier'].search([('titre','=',mod.titre)])
            for order in orders:  
                
                for t in order['taches_ids']:
                    row=row_sub+1
                # the report content
                    sheet.write(row, 0, number, text_style)
                    sheet.write(row, 1, t.code, text_style) 
                    sheet.write(row,2,t.task, tache_style)


                    row_sub=row
                    for t1 in t['subtask_ids']:
                        row_sub+=1
                        sheet.write(row_sub,3,t1.quantite, text_style)
                        sheet.write(row_sub, 2, t1.Subtask, text_style)
                number+=1
                                   


            # return the excel file as a response, so the browser can download it
            workbook.close()
            output.seek(0)
            response.stream.write(output.read())
            output.close()
            return response
