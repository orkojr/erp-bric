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
class PurchaseCout(models.TransientModel):
    _name = "purchase.cout.wizard"


    annee = fields.Integer(
        string='Annee',
        default=2022,
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
    select_type = fields.Selection(
        string='Type de suivi',
        selection=[('an', 'Annuel'), ('period', 'Periode')],
        default='an'
    )

    def print_xlsx(self):

        data = {
            'annee': self.annee,
            'date_deb': self.date_deb.strftime("%m/%d/%Y"),
            'date_fin': self.date_fin.strftime("%m/%d/%Y"),
            'type': self.select_type,
            'deb1': self.date_deb.strftime('%d-%m-%Y'),
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'purchase.cout.wizard',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Cout d\'achat des matieres premieres',
                     },
            'report_type': 'stock_xlsx',
        }


    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # create some style to set up the font type, the font size, the border, and the aligment
        title_style = workbook.add_format({'font_name': 'Times', 'font_size': 12, 'bold': True, 'align': 'center','valign': 'vcenter', 'text_wrap': True})
        title_style21 = workbook.add_format({'font_name': 'Times','font_size': 14,'bg_color':'#D3C2', 'bold': True, 'align': 'center', 'valign': 'vcenter','left': 2, 'bottom':2, 'right':2, 'top':2, 'text_wrap': True})
        header_style1 = workbook.add_format({'font_name': 'Times', 'bold': True, 'align': 'center', 'valign': 'vcenter','left': 2, 'bottom':2, 'right':2, 'top':2, 'text_wrap': True})
        title_style1 = workbook.add_format({'font_name': 'Times', 'font_color':'red','font_size': 23, 'bold': True, 'align': 'center', 'valign': 'vcenter','left': 1, 'bottom':1, 'right':1, 'top':1, 'text_wrap': True})
        header_style = workbook.add_format({'font_name': 'Times', 'bold': True, 'align': 'center', 'text_wrap': True, 'bg_color':'#D9D9D9','left': 1, 'bottom':1, 'right':1, 'top':1,})
        text_style = workbook.add_format({'font_name': 'Times', 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'center','valign': 'vcenter', })
        text_style1 = workbook.add_format({'font_name': 'Times', 'left': 1, 'bottom':2, 'right':1, 'top':1, 'align': 'center','valign': 'vcenter', })
        number_style = workbook.add_format({'font_name': 'Times', 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'center','valign': 'vcenter', 'text_wrap': True})



        if data['type'] == 'an':
            deb = datetime.date(data['annee'], 1, 1)
            fin = datetime.date(data['annee'], 12, 31)
            deb_date = deb.strftime("%m/%d/%Y")
            fin_date = fin.strftime("%m/%d/%Y")
            name = data['annee'] 
            
        
        else :
            deb_date = data['date_deb']
            fin_date = data['date_fin']
            name = data['deb1']


        
    
        purchase_cout =  """select * from purchase_approvisionnement as pa 
            where  DATE(pa.create_date) between %s and %s  """
        cout_line =  """select * from purchase_approvisionnement_line as pal
            where  DATE(pal.create_date) between %s and %s  """
        params = deb_date, fin_date

        self._cr.execute(purchase_cout, params)
        cout_obj = self._cr.dictfetchall()

        self._cr.execute(cout_line, params)
        cout_line_obj = self._cr.dictfetchall()

        


        lines = [] 
        for obj in cout_obj :
            article_obj = self.env['product.product'].search([('id', '=', obj['product_id'])])
            ump_obj = self.env['uom.uom'].search([('id', '=', obj['unite_mesure'])])
            umach_obj = self.env['uom.uom'].search([('id', '=', obj['product_uom_id'])])

            for art in article_obj :
                mp = art.product_tmpl_id.name
            for uo in ump_obj :
                um_p = uo.name
            for uo in umach_obj :
                um_ach = uo.name
            qty = obj['product_qty']
            pu  = obj['pu']
            total = obj['total']
            qtotal = round(obj['quantite_total'],2)
            pu1 = round(obj['prix_pu'],2)
            cout_a = round(obj['cout_total'],2)
            els = []
            for el in cout_line_obj:
                if el['purchase_approv_id'] == obj['id']:
                    elt_obj = self.env['product.product'].search([('id', '=', el['product_id'])])
                    for art1 in elt_obj :
                            mp1 = art1.product_tmpl_id.name
                    qty1 = el['product_qty']
                    pu11 = el['pu']
                    total1 = el['total']

                    val1 = {
                        'el' : mp1,
                        'qty' : qty1,
                        'pu' : pu11,
                        'total' : total1,
                    }
                    els.append(val1)

            val = {
                'mp' : mp + ' (en ' + um_ach + ')',
                'qty' : qty,
                'pu' : pu,
                'total' : total,
                'qtotal' : qtotal,
                'pu1' : pu1,
                'ump' : um_p,
                'uma' : um_ach,
                'cout' : cout_a,
                'elts' : els,
            }

            lines.append(val)
            

        
        

        sheet = workbook.add_worksheet("Analyse couts matieres premieres")
        # set the orientation to landscape
        sheet.set_landscape()
        # set up the margin in inch
        sheet.set_margins(0.5,0.5,0.5,0.5)
        sheet.hide_gridlines(2)
        # set up the column width
        sheet.set_column('A:A', 25)
        sheet.set_column('B:B', 15)
        sheet.set_column('F:F', 15)
        sheet.set_column('C:C', 8)
        sheet.set_column('G:G', 8)
        sheet.set_column('H:I', 10)
        sheet.set_column('E:E', 17)
        sheet.set_row(4, 27)
        sheet.set_row(7, 30)
        
        sheet.write('B1', 'Exercice %s'%(name), text_style)
        sheet.write('A5', 'SERVICE COMPTABILITÉ', title_style)

        sheet.merge_range(4,1,4,5, 'CALCUL DU COÛT D\'ACHAT DES MATIÈRES PREMIÈRES', title_style21)

        sheet.write('A8', 'MATIÈRES PREMIÈRES', header_style1)
        sheet.write('B8', 'ÉLÉMENTS', header_style1)
        sheet.write('C8', 'QTE', header_style1)
        sheet.write('D8', 'PU', header_style1)
        sheet.write('E8', 'TOTAL', header_style1)
        sheet.write('F8', 'Coût d\'achat', header_style1)
        sheet.write('G8', 'Unité de mesure', header_style1)
        sheet.write('H8', 'Qte totale par achat', header_style1)
        sheet.write('I8', 'Prix par unité', header_style1)
        
        row = 8
        col = 0

        i = 0
        f = len(lines) - 1

        elt_comp = []
        comp_plus = lines
        while i != f :
            k = lines[i]
            j = i + 1
            while j < len(lines):
                if lines[j] != k and lines[j]['mp'] == k['mp']:
                    k['qty'] +=  lines[j]['qty']
                    k['qty'] /=  2
                    k['qty'] =  round(k['qty'], 2)
                    k['pu'] +=  lines[j]['pu']
                    k['pu'] /=  2
                    k['pu'] =  round(k['pu'], 2)
                    k['pu1'] +=  lines[j]['pu1']
                    k['pu1'] /=  2
                    k['pu1'] =  round(k['pu1'], 2)
                    k['total'] += lines[j]['total']
                    k['total'] /= 2
                    k['total'] =  round(k['total'], 2)
                    k['qtotal'] += lines[j]['qtotal']
                    k['qtotal'] /= 2
                    k['qtotal'] =  round(k['qtotal'], 2)
                    k['cout'] += lines[j]['cout']
                    k['cout'] /= 2
                    k['cout'] =  round(k['cout'], 2)
                    list_elt = []
                    for el in k['elts']:
                        elt = el
                        for l in lines[j]['elts']:
                            if l['el'] ==  el['el']:
                                elt['qty'] += l['qty']
                                elt['qty'] /= 2
                                elt['qty'] = round(elt['qty'], 2)
                                elt['total'] += l['total']
                                elt['total'] /= 2
                                elt['total'] = round(elt['total'], 2)
                                elt['pu'] += l['pu']
                                elt['pu'] /= 2
                                elt['pu'] = round(elt['pu'], 2)
                        
                        list_elt.append(elt)
                    k['elts'] = list_elt
                    
                    del lines[j]
                    j += 1
                    elt_comp.append(k)
                else :
                    j += 1
                
            
            i += 1
                
        for el in comp_plus:
            if el['mp'] not in (line['mp'] for  line in elt_comp):
                elt_comp.append(el)    
            
        print(elt_comp)


        

            
        for line in elt_comp :
            
            long = len(line['elts'])
            if long == 0 :
                sheet.write(row, col, line['mp'], header_style1)
                sheet.write(row, col + 1, "Achat", text_style1)
                sheet.write(row, col + 2, line['qty'], text_style1)
                sheet.write(row, col + 3, line['pu'], text_style1)
                sheet.write(row, col + 4, line['total'], text_style1)
                sheet.write(row, col + 5, line['cout'], header_style1)
                sheet.write(row, col + 6, line['ump'], header_style1)
                sheet.write(row, col + 7, line['qtotal'], header_style1)
                sheet.write(row, col + 8, line['pu1'], header_style1)
                row +=  long + 1
            else :
                sheet.merge_range(row,col,row + long, col  , line['mp'], header_style1)
                sheet.write(row, col + 1, "Achat", text_style)
                col1 = 1
                sheet.write(row, col + 2, line['qty'], text_style)
                sheet.write(row, col + 3, line['pu'], text_style)
                sheet.write(row, col + 4, line['total'], text_style)
                for el in  line['elts']:
                    if el == line['elts'][-1]:
                        sheet.write(row  + col1, col + 1, el['el'], text_style1)
                        sheet.write(row  + col1, col + 2, el['qty'], text_style1)
                        sheet.write(row  + col1, col + 3, el['pu'], text_style1)
                        sheet.write(row  + col1, col + 4, el['total'], text_style1)
                        col1 += 1
                    else:
                        sheet.write(row  + col1, col + 1, el['el'], text_style)
                        sheet.write(row  + col1, col + 2, el['qty'], text_style)
                        sheet.write(row  + col1, col + 3, el['pu'], text_style)
                        sheet.write(row  + col1, col + 4, el['total'], text_style)
                        col1 += 1
                sheet.merge_range(row,col + 5,row + long, col + 5, line['cout'], header_style1)
                sheet.merge_range(row,col + 6,row + long, col + 6, line['ump'], header_style1)
                sheet.merge_range(row,col + 7,row + long, col + 7, line['qtotal'], header_style1)
                sheet.merge_range(row,col + 8,row + long, col + 8, line['pu1'], header_style1)
                row +=  long + 1
            
         
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
 
        return response