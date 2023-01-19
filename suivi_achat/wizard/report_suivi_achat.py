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
class SuiviAchat(models.TransientModel):
    _name = "suivi.achat.report.wizard"

    select_type = fields.Selection(
        string='Type de suivi',
        selection=[('an', 'Annuel'), ('men', 'Mensuel')],
        default='men'
    )

    annee = fields.Integer(
        string='Annee',
        default=2023,
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
    def print_xlsx(self):

        data = {
            'date_deb': self.date_deb.strftime("%m/%d/%Y"),
            'date_fin': self.date_fin.strftime("%m/%d/%Y"),
            'annee': self.annee,
            'type': self.select_type,
            'date_stock':self.date_deb.strftime('%Y-%m-%d %H:%M:%S'),
            'deb1': self.date_deb.strftime('%d-%m-%y %H:%M:%S'),
            'fin1': self.date_fin.strftime('%d-%m-%y %H:%M:%S'),
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'suivi.achat.report.wizard',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Suivi achat',
                     },
            'report_type': 'stock_xlsx',
        }


    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # create some style to set up the font type, the font size, the border, and the aligment
        title_style = workbook.add_format({'font_name': 'Times', 'font_size': 23, 'bold': True, 'align': 'center','valign': 'vcenter','left': 2, 'bottom':2, 'right':2, 'top':2, 'text_wrap': True})
        title_style21 = workbook.add_format({'font_name': 'Times', 'bold': True, 'align': 'center', 'valign': 'vcenter','left': 2, 'bottom':2, 'right':2, 'top':2, 'text_wrap': True})
        title_style1 = workbook.add_format({'font_name': 'Times', 'font_color':'red','font_size': 23, 'bold': True, 'align': 'center', 'valign': 'vcenter','left': 1, 'bottom':1, 'right':1, 'top':1, 'text_wrap': True})
        header_style = workbook.add_format({'font_name': 'Times', 'bold': True, 'left': 2, 'bottom':2, 'right':2, 'top':2, 'align': 'center','valign': 'vcenter', 'text_wrap': True})
        text_style = workbook.add_format({'font_name': 'Times', 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'center','valign': 'vcenter', })
        number_style = workbook.add_format({'font_name': 'Times', 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'center','valign': 'vcenter', 'text_wrap': True})




        if data['type'] == 'an':
            deb = datetime.date(data['annee'], 1, 1)
            fin = datetime.date(data['annee'], 12, 31)
            deb_1 = deb.strftime('%d-%m-%y %H:%M:%S')
            fin_1 = fin.strftime('%d-%m-%y %H:%M:%S')
            day = 365
            print("C'est bon 1")
        
        else :
            deb_1 = data['deb1']
            fin_1 = data['fin1']
            day = 31
            print("C'est bon 2")


        #formate la date pour la requete sql  
        deb_date = datetime.datetime.strptime(deb_1, '%d-%m-%y %H:%M:%S')
        fin_date = datetime.datetime.strptime(fin_1, '%d-%m-%y %H:%M:%S')

        
        while deb_date <= fin_date:
            date = deb_date + timedelta(days=day)
            req_date1 = deb_date.strftime("%m/%d/%Y")
            req_date11 = deb_date.strftime("%A %d %B %Y")
            req_date_name = deb_date.strftime("%B")
            req_date2 = date.strftime("%m/%d/%Y")
            if data['type'] == 'an':
                name_report = data['annee']
            else:
                name_report = req_date_name
            print("C'est bon 3")
            
            purchase_obj = self.env['purchase.order'].search([('effective_date', '>=',deb_date),('effective_date', '<=', date)])


            motif_achat = ""
            date_ach =  ""
            design = ""
            statut_autre_cout =""
            moyen_transport = ""
            lieu_achat = ""
            achat_location = ""
            service = ""
            chantier = ""
            qty = 0
            pu = 0
            pt = 0
            statut = ""
            montant_avance = ""
            date_paiement = ""
            date_paiement_autre = ""
            statut_fin = ""
            lines = []

            if len(purchase_obj) > 0:
                for purchase in  purchase_obj:
                    if purchase.purchase_request:
                        dia = purchase.purchase_request
                        print("parfait")
                        motif_achat = dia.motif_achat.name if dia.motif_achat else ""
                        service = dia.service_id.name
                        date_ach =  purchase.effective_date
                        if dia.objet == 'projet':
                            chantier = dia.chantier_id.name if dia.chantier_id else ""
                        for order in purchase.order_line:
                            design = order.name
                            for line in dia.line_ids:
                                if line.product_id.id == order.product_id.id:
                                    moyen_transport = line.vehicule.name if line.vehicule else ""
                            statut_autre_cout =""
                            lieu_achat = dia.lieu.name if dia.lieu else ""
                            # achat_location = ""
                            
                            qty = order.product_qty
                            pu = order.price_unit
                            pt = order.price_subtotal
                            statut = ""
                            montant_avance = ""
                            date_paiement = dia.date_paiement if dia.date_paiement else ""
                            date_paiement_autre = ""
                            statut_fin = ""
                            val = {
                                "mois" : date_ach.strftime("%B"),
                                "date" : date_ach.strftime("%d/%m/%Y"),
                                "motif" : motif_achat ,
                                "design" : design,
                                "moyen" : moyen_transport,
                                "lieu" : lieu_achat,
                                "service" : service,
                                "chantier" : chantier,
                                "qty" : qty,
                                "pu" : pu,
                                "pt" : pt,
                                "statut" : statut,
                                "avance" : montant_avance,
                                "datp" : date_paiement,
                                "statut_fin" : statut_fin,
                            }
                            lines.append(val)
            print(lines)
                
                
            
            
            # prix total achat
            prix_achat = 0
            for line in lines :
                prix_achat += line['pt']
            
            prix_achat_aff = "%s XAF"%(prix_achat)
            

            # %(name_report)

            print("C'est bon 4")


            sheet = workbook.add_worksheet("suivi achat %s"%(name_report))
            # set the orientation to landscape
            sheet.set_landscape()
            # set up the paper size, 9 means A4
            sheet.set_paper(9)
            # set up the margin in inch
            sheet.set_margins(0.5,0.5,0.5,0.5)
            sheet.hide_gridlines(2)
            # set up the column width
            sheet.set_column('A:A', 12)
            sheet.set_column('B:B', 10)
            sheet.set_column('C:C', 14)
            sheet.set_column('I:J', 14)
            sheet.set_column('L:L', 14)
            sheet.set_column('P:P', 14)
            sheet.set_column('K:K', 20)
            sheet.set_column('D:E', 37)
            sheet.set_column('F:F', 25)
            sheet.set_column('G:H', 20)
            sheet.set_column('H:H', 30)
            sheet.set_column('N:N', 12)
            sheet.set_column('O:O', 20)
            sheet.set_row(6, 30)
            sheet.set_row(9, 34)

            sheet.merge_range(6,1,6,3, 'ACHATS', title_style)
            sheet.write('E7', 'PRQ009 ENG 3/A', title_style)
            sheet.write('G7', 'TOTAL', title_style1)
            sheet.merge_range(6,7,6,8, prix_achat_aff, title_style1)


            sheet.write('B10', 'MOIS', title_style21)
            sheet.write('C10', 'DATE', title_style21)
            sheet.write('D10', 'MOTIFS', title_style21)
            sheet.write('E10', 'DESIGNATION', title_style21)
            sheet.write('F10', 'MOYEN DE TRANSPORT', title_style21)
            sheet.write('G10', 'LIEU D \'ACHAT', title_style21)
            sheet.write('H10', 'SERVICE AFFECTE', title_style21)
            sheet.write('I10', 'CHANTIER AFFECTE', title_style21)
            sheet.write('J10', 'QUANTITE TOTALE', title_style21)
            sheet.write('K10', 'PRIX UNITAIRE', title_style21)
            sheet.write('L10', 'MONTANT TOTAL', title_style21)
            sheet.write('M10', 'STATUT', title_style21)
            sheet.write('N10', 'MONTANT AVANCE', title_style21)
            sheet.write('O10', 'DATE DE PAIEMENT(si avance ou non payé)', title_style21)
            sheet.write('P10', 'STATUT FIN DE MOIS', title_style21)
            sheet.freeze_panes(10,0)
            row = 10
            col = 1
            if len(lines):
                for line in lines :
                    sheet.write(row, col, line['mois'], text_style)
                    sheet.write(row, col + 1, line['date'], text_style)
                    sheet.write(row, col + 2, line['motif'], text_style)
                    sheet.write(row, col + 3, line['design'], text_style)
                    sheet.write(row, col + 4, line['moyen'], text_style)
                    sheet.write(row, col + 5, line['lieu'], text_style)
                    sheet.write(row, col + 6, line['service'], text_style)
                    sheet.write(row, col + 7, line['chantier'], text_style)
                    sheet.write(row, col + 8, line['qty'], number_style)
                    sheet.write(row, col + 9, line['pu'], number_style)
                    sheet.write(row, col + 10, line['pt'], number_style)
                    sheet.write(row, col + 11, line['statut'], text_style)
                    sheet.write(row, col + 12, line['avance'], text_style)
                    sheet.write(row, col + 13, line['datp'], text_style)
                    sheet.write(row, col + 14, line['statut_fin'], text_style)
                    row += 1
                
            deb_date = date
         
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
 
        return response