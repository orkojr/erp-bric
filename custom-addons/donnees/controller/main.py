# -*- coding: utf-8 -*-
 
from odoo import http
from odoo.http import content_disposition, request
import io
import xlsxwriter

from datetime import date, datetime
     

 
class SaleExcelReportController(http.Controller):
    @http.route([
        '/livraison_chantier/excel_report/<model("livraison.chantier.wizard"):wizard>',
    ], type='http', auth="user", csrf=False)
    def get_suivi_livraison_excel_report(self,wizard=None,**args):
         
        response = request.make_response(
                    None,
                    headers=[
                        ('Content-Type', 'application/vnd.ms-excel'),
                        ('Content-Disposition', content_disposition('Suivi Livraison Chantier' + '.xlsx'))
                    ]
                )
 
        # create workbook object from xlsxwriter library
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
 
        # create some style to set up the font type, the font size, the border, and the aligment
        title_style = workbook.add_format({'font_name': 'Times', 'font_size': 25, 'bold': True, 'align': 'center','left': 1, 'bottom':1, 'right':1, 'top':1,})
        header_style = workbook.add_format({'font_name': 'Times', 'bold': True, 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'center'})
        text_style = workbook.add_format({'font_name': 'Times', 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'left'})
        number_style = workbook.add_format({'font_name': 'Times', 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'right'})
        
        date_wiz = wizard.start_date
        for project in wizard.project_id:
            # create worksheet/tab per salesperson 
            sheet = workbook.add_worksheet(project.name)
            # set the orientation to landscape
            sheet.set_landscape()
            # set up the paper size, 9 means A4
            sheet.set_paper(9)
            # set up the margin in inch
            sheet.set_margins(0.5,0.5,0.5,0.5)
            sheet.hide_gridlines(2)
 
            # set up the column width
            sheet.set_column('A:J', 15)
 
            # the report title
            # merge the A1 to E1 cell and apply the style font size : 14, font weight : bold
            sheet.merge_range(1,0,2,10, 'TABLEAU DU SUIVI DES LIVRAISONS DU CHANTIER %s' %(project.name), title_style)

            # """SELECT p.default_code AS product_code , sum(sm.product_uom_qty) AS qte_lvre, part.name AS partner, 
            #     FROM product_product AS p, stock_move AS sm, res.partner AS part
            #     JOIN project_task AS pro ON  pro.partner_id = part.id
            #     where sm.date_done >= %s"""

            chantier = """SELECT distinct p.default_code AS product_code , sum(sm.product_uom_qty) AS qte_lvre, 
                    part.name AS partner 
                FROM product_product AS p, stock_move AS sm, res_partner AS part  
                JOIN project_task AS pro ON  pro.partner_id = part.id 
                WHERE pro.partner_id = p.id                 
                GROUP BY  (p.default_code, part.name)"""
                

            # """SELECT distinct p.id, sum(s.product_uom_qty) As qte_lvre, sum(s.casse_livr) AS casse FROM product_product AS p,
            #         stock_move AS s, stock_move_line AS sml
            #         JOIN stock_warehouse AS wh ON wh.lot_stock_id = sml.location_dest_id
            #         WHERE s.is_done=True AND  sml.qty_done = s.product_uom_qty
            #         AND sml.product_id=p.id AND s.date>=%s AND s.date<%s AND wh.id=%s  group by p.id"""


            # partners = request.env['res.partner'].search([('partner_id', '=', project.partner_id)])
            products = request.env['product.product'].search([])

            # chantier_obj =  request._cr.execute(chantier)
            # partner = """SELECT *  FROM  product_product"""
            # partner_obj = request._cr.execute(partner)

            # print(partner_obj)

            
             
            # # table title
            sheet.write('A6','DATES(%s)'%(date_wiz.year), header_style)
            sheet.write('B6','PRODUITS', header_style)
            sheet.write('C6','QUANTITE', header_style)
            sheet.write('D6','CLIENTS', header_style)
            sheet.write('E6','CHAUFFEUR', header_style)
            sheet.write('F6','N° VEHICULE', header_style)
            sheet.write('G6','BL', header_style)
            sheet.write('H6','O.C', header_style)
            sheet.write('I6','SABLE MOYEN', header_style)
            sheet.write('J6','COMMANDE', header_style)
            sheet.write('K6','SORTIE', header_style)
            sheet.write('KL6','RESTE', header_style)
 
            row = 6
            col = 0
            # for prod in products:
            #     sheet.write(row, 0,prod.name, text_style )
            #     sheet.write(row, 1,prod.default_code, text_style )
            #     sheet.write(row, 2,500, text_style )
            #     sheet.write(row, 1,prod.default_code, text_style )
            #     sheet.write(row, 2,500, text_style )

            #     row += 1

            # for ch in partner_obj:

            #     sheet.write(row, 0,date_wiz, text_style )
            #     sheet.write(row, 1,ch.name, text_style )
            #     # sheet.write(row, 2,ch.qte_lvre, text_style )
            #     # sheet.write(row, 3,ch.qte_lvre, text_style )
               
            #     row += 1
                    

 
            # # search the sales order  
            # orders = request.env['sale.order'].search([('user_id','=',user.id), ('date_order','>=', wizard.start_date), ('date_order','<=', wizard.end_date)])
            # for order in orders:
            #     # the report content
            #     sheet.write(row, 0, number, text_style)
            #     sheet.write(row, 1, order.name, text_style)
            #     sheet.write(row, 2, str(order.date_order), text_style)
            #     sheet.write(row, 3, order.partner_id.name, text_style)
            #     sheet.write(row, 4, order.amount_total, number_style)
 
            #     row += 1
            #     number += 1
 
            # # create a formula to sum the total sales
            # sheet.merge_range('A' + str(row+1) + ':D' + str(row+1), 'Total', text_style)
            # sheet.write_formula(row, 4, '=SUM(E3:E' + str(row) + ')', number_style)
 
        # return the excel file as a response, so the browser can download it
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
 
        return response