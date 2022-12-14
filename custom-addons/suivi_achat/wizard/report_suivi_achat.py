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
        
        else :
            deb_1 = data['deb1']
            fin_1 = data['fin1']
            day = 31

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

            purchase =  """select po.id,DATE(po.date_approve), po.lieu, po.motif_achat,
                po.vehicule, po.partner_id, po.service_id, po.purchase_request 
                from purchase_order po where po.purchase_request in (select pr.id from purchase_request pr) 
                and po.state in ('purchase', 'sent') and DATE(po.date_approve) between %s and %s  """

            purchase_req_obj = self.env['purchase.request'].search([])
            purchase_location_obj = self.env['purchase.location'].search([])
            purchase_mot_obj1 = self.env['account.budget.post'].search([])
            vehicle_obj = self.env['fleet.vehicle'].search([])
            service_obj = self.env['hr.department'].search([])
            partner_obj = self.env['res.partner'].search([])
            chantier_obj = self.env['project.project'].search([])
            account_move_obj = self.env['account.move'].search([])
            account_move_line_obj = self.env['account.move.line'].search([])
            account_payment_obj = self.env['account.payment'].search([])
            purchase_req_line_obj = self.env['purchase.request.line'].search([])
            autre_cout_obj = self.env['purchase.request.line.cout'].search([])

            # print(purchase_location_obj)

            
            params = req_date1, req_date2

            self._cr.execute(purchase, params)
            purchase_obj = self._cr.dictfetchall()

            lines = []

            # recuperer les valeurs des achats effectues.

            for purchase in  purchase_obj:
                motif_achat = ""
                date_ach =  purchase['date']
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
                p_o_l_obj = self.env['purchase.order.line'].search([('order_id', '=', purchase['id'])])
                chantier_obj = self.env['project.project'].search([])
                for mov in account_move_obj :
                    if mov.purchase_request.id == purchase['purchase_request']:
                        for mov_line in account_move_line_obj :
                            if mov_line.move_id.id == mov.id and mov_line.product_id ==mov.purchase_request.product_id:
                                montant_avance = ""
                                if mov.payment_state == 'partial':
                                    montant_avance = mov.amount_total - mov.amount_residual
                                    statut = "AVANCE"
                                    date_paiement = mov.invoice_date_due.strftime("%d/%m/%Y")
                                elif mov.payment_state == 'paid' :
                                    statut = "PAYE"
                                else :
                                    date_paiement = mov.invoice_date_due.strftime("%d/%m/%Y")
                                    statut = "NON PAYE"
                            else:
                                if mov.payment_state == 'partial':
                                    statut_autre_cout = "AVANCE"
                                    date_paiement_autre = mov.invoice_date_due.strftime("%d/%m/%Y")
                                elif mov.payment_state == 'paid' :
                                    statut_autre_cout = "PAYE"
                                else :
                                    date_paiement_autre = mov.invoice_date_due.strftime("%d/%m/%Y")
                                    statut_autre_cout = "NON PAYE"


                
                for lot in purchase_location_obj:
                    if lot.id == purchase['lieu']:
                        achat_location = lot.name
                for mot in purchase_mot_obj1:
                    if mot.id == purchase['motif_achat']:
                        motif_achat = mot.name
                for serv in service_obj :
                    if serv.id == purchase['service_id']:
                        service = serv.name
                if purchase['vehicule'] :
                    for vh in vehicle_obj :
                        if vh.id == purchase['vehicule']:
                            moyen_transport = vh.name
                for part in partner_obj :
                    if part.id == purchase['partner_id']:
                        lieu_achat = part.street
                
                for req in purchase_req_obj :
                    if req.id == purchase['purchase_request']:
                        if req.chantier_id :
                            for ch in chantier_obj:
                                if ch.id == req.chantier_id.id:
                                    chantier = ch.name

                for pol in p_o_l_obj:
                    design = pol.name
                    qty = pol.product_qty
                    pu = pol.price_unit
                    pt = pol.price_total
                
                
                    val = {
                        "mois" : date_ach.strftime("%B"),
                        "date" : date_ach.strftime("%d/%m/%Y"),
                        "motif" : motif_achat ,
                        "design" : design,
                        "moyen" : moyen_transport,
                        "lieu" : achat_location if achat_location != "" else lieu_achat,
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
                    design = ""
                    qty = 0,
                    pu = 0
                    pt = 0
                    lieu_achat =""
                    statut = ""
                    montant_avance = ""
                    date_paiement =""
                    statut_fin = ""
                    for req_line in purchase_req_line_obj:
                        if req_line.request_id.id == purchase['purchase_request']:
                            for autre in autre_cout_obj:
                                if autre.request_cout_id.id == req_line.id:
                                    design = autre.product_id.name
                                    pu = autre.prix_unitaire
                                    qty = autre.quantite_piece
                                    pt = autre.cout
                                    val = {
                                    "mois" : date_ach.strftime("%B"),
                                    "date" : date_ach.strftime("%d/%m/%Y"),
                                    "motif" : motif_achat,
                                    "design" : design,
                                    "moyen" : moyen_transport,
                                    "lieu" : lieu_achat,
                                    "service" : service,
                                    "chantier" : chantier,
                                    "qty" : qty,
                                    "pu" : pu,
                                    "pt" : pt,
                                    "statut" : statut_autre_cout,
                                    "avance" : montant_avance,
                                    "datp" : date_paiement_autre,
                                    "statut_fin" : statut_fin,
                                }
                                    lines.append(val)


            
            # prix total achat
            prix_achat = 0
            for line in lines :
                prix_achat += line['pt']
            
            prix_achat_aff = "%s XAF"%(prix_achat)
            

            

            sheet = workbook.add_worksheet("suivi %s"%(name_report))
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