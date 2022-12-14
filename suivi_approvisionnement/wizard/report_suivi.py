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
class SuiviApprocisionnement(models.TransientModel):
    _name = "suivi.approvisionnement.report.wizard"

    product_id = fields.Many2many('product.product', string="Articles")
    category = fields.Many2many('product.category', 'categ_wiz_rel11', 'categ', 'wiz', string='Categorie')
    
    select_type = fields.Selection(
        string='Type de suivi',
        selection=[('categ', 'Par categorie'), ('product', 'Par produit')],
        default='categ'
    )
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
    def suivi_xlsx(self):

        data = {
            'date_deb': self.date_deb.strftime("%m/%d/%Y"),
            'date_fin': self.date_fin.strftime("%m/%d/%Y"),
            'article': self.product_id.ids,
            'category': self.category.ids,
            'type': self.select_type,
            'date_stock':self.date_deb.strftime('%Y-%m-%d %H:%M:%S'),
            'deb1': self.date_deb.strftime('%d-%m-%y %H:%M:%S'),
            'fin1': self.date_fin.strftime('%d-%m-%y %H:%M:%S'),
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'suivi.approvisionnement.report.wizard',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Suivi approvisionnement',
                     },
            'report_type': 'stock_xlsx',
        }


    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # create some style to set up the font type, the font size, the border, and the aligment
        title_style = workbook.add_format({'font_name': 'Times', 'font_size': 23, 'bold': True, 'align': 'center','left': 1, 'bottom':1, 'right':1, 'top':1,})
        header_style = workbook.add_format({'font_name': 'Times', 'bold': True, 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'center'})
        text_style = workbook.add_format({'font_name': 'Times', 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'left'})
        number_style = workbook.add_format({'font_name': 'Times', 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'center'})

        
        # recuperer la liste des articles stockable selon le type de suivi choisi

        if data['type'] == 'categ':
            categ = data['category']
            article_obj = self.env['product.product'].search([('product_tmpl_id.categ_id', 'in', categ),('product_tmpl_id.detailed_type', '=', 'product')])
        
        elif data['type'] == 'product':
            articles = data['article']
            article_obj = self.env['product.product'].search([('id', 'in', articles), ('product_tmpl_id.detailed_type', '=', 'product')])
        else:
            article_obj = self.env['product.product'].search([('product_tmpl_id.detailed_type', '=', 'product')])
        for art in article_obj: 
            sheet = workbook.add_worksheet(art.name)
            # set the orientation to landscape
            sheet.set_landscape()
            # set up the paper size, 9 means A4
            sheet.set_paper(9)
            # set up the margin in inch
            sheet.set_margins(0.5,0.5,0.5,0.5)
            sheet.hide_gridlines(2)
 
            # set up the column width
            sheet.set_column('A:A', 12)
            sheet.set_column('B:B', 14)
            sheet.set_column('C:F', 17)
            sheet.set_column('G:G', 24)

 
            # the report title
            sheet.merge_range(2,2,3,6, 'SUIVI / APPROVISIONNEMENT  %s' %(art.name), title_style)

            
            
             
            # table title
            sheet.write('A5','DATE', header_style)
            sheet.write('B5','LIBELLE', header_style)
            sheet.write('C5','STOCK INITIAL (L)', header_style)
            sheet.write('D5','ENTRÉE (L)', header_style)
            sheet.write('E5','SORTIE (L)', header_style)
            sheet.write('F5','STOCK FINAL (L)', header_style)
            sheet.write('G5','OBSERVATION', header_style)

            deb = data['date_deb']
            fin = data['date_fin']
            article_id= art.id

        

            
            deb_1 = data['deb1']
            fin_1 = data['fin1']
            
            deb_date = datetime.datetime.strptime(deb_1, '%d-%m-%y %H:%M:%S')
            fin_date = datetime.datetime.strptime(fin_1, '%d-%m-%y %H:%M:%S')
            

            lines1=[]
            while deb_date <= fin_date:
                date = deb_date + timedelta(days=1)
                req_date = deb_date.strftime("%m/%d/%Y")
                req_date1 = deb_date.strftime("%m/%d/%Y")
                req_date2 = date.strftime("%m/%d/%Y")

                #permet de recuperer les matieres premieres utilisees
                
                composants = """select stm.product_id, sum(stm.quantity_done)  as qty_done
                from stock_move as stm 
                left join mrp_production mrp on mrp.id=stm.raw_material_production_id 
                where  stm.is_done=True  and mrp.state in ('progress','to_close','done','confirmed') 
                and DATE(stm.create_date) = %s and stm.product_id = %s group by stm.product_id"""

                purchase_query = """
                    SELECT sum(p_o_l.product_qty) AS product_qty, p_o_l.product_id 
                    FROM purchase_order_line AS p_o_l
                    JOIN purchase_order AS p_o ON p_o_l.order_id = p_o.id
                    INNER JOIN stock_picking_type AS s_p_t ON p_o.picking_type_id = s_p_t.id
                    WHERE p_o.state IN ('purchase','done') AND DATE(p_o.create_date)=%s
                    AND p_o_l.product_id=%s group by p_o_l.product_id"""

                params = req_date, article_id
                params1 = req_date1, req_date2
                
                self._cr.execute(composants, params)
                composant_obj = self._cr.dictfetchall()

                self._cr.execute(purchase_query, params)
                acheter_obj = self._cr.dictfetchall()


               
                
                

                date_stock = date.strftime('%Y-%m-%d %H:%M:%S')

                virtual_available = art.with_context({'to_date': date_stock}).virtual_available
                outgoing_qty = art.with_context({'to_date': date_stock}).outgoing_qty
                incoming_qty = art.with_context({'to_date': date_stock}).incoming_qty
                available_qty = virtual_available + outgoing_qty - incoming_qty


                liv = 0
                prod = 0
                acheter = 0

                if len(acheter_obj)>0:
                    for ob in acheter_obj:
                        acheter = ob['product_qty']

                


               

                entree = 0
                sortiee = 0

                # stock_final = available_qty + entree - sortiee

                stock_date = date.strftime('%Y-%m-%d')

                if len(composant_obj) > 0 :
                    for obj in composant_obj :
                        sortiee = obj['qty_done']
                if len(acheter_obj) > 0 :
                    for obj in composant_obj :
                        entree = obj['product_qty']

                stock_final = available_qty + entree - sortiee
                vals = {
                'date': stock_date,
                'stock_initial': available_qty,
                'entree': entree,
                'sortie': sortiee,
                'stock_final': stock_final
                }
                lines1.append(vals)
                    

                deb_date = date
            
 
            row = 5
            col = 0
            lines_val = []
            
            for line in lines1:

                if line['entree'] == 0 and line['sortie'] == 0:

                    lines_val = lines_val
                else:
                    lines_val.append(line)

            for line in lines_val:

                sheet.write(row, col, line['date'], text_style)
                sheet.write(row, col + 1, art.default_code, text_style)
                sheet.write(row, col + 2, line['stock_initial'], number_style)
                sheet.write(row, col + 3, line['entree'], number_style)
                sheet.write(row, col + 4, line['sortie'], number_style)
                sheet.write(row, col + 5, line['stock_final'], number_style)
                sheet.write(row, col + 6, '', text_style)
                row +=1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
 
        return response