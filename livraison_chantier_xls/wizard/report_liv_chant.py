import time
import json
import datetime
import io
from odoo import fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import date_utils
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter
class LivChantier(models.TransientModel):
    _name = "chantier.xlsx.report.wizard"
    start_date = fields.Date(string="Date debut",  default=time.strftime('%Y-%m-01'), required=True)
    end_date = fields.Date(string="Date fin",  default=datetime.datetime.now(), required=True)
    project_id = fields.Many2many(
        string='Chantiers',
        comodel_name='project.project',
        required=True,
    )
    
    
    def print_xlsx(self):
        if self.start_date > self.end_date:
            raise ValidationError('Start Date must be less than End Date')
        data = {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'projet' : self.project_id.ids,
            'deb1': self.start_date.strftime('%d-%m-%y %H:%M:%S'),
            'fin1': self.end_date.strftime('%d-%m-%y %H:%M:%S'),
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'chantier.xlsx.report.wizard',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Suivi livraison chantier',
                     },
            'report_type': 'stock_xlsx',
        }


    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # create some style to set up the font type, the font size, the border, and the aligment
        title_style = workbook.add_format({'font_name': 'Times', 'font_size': 25, 'bold': True, 'align': 'center','left': 1, 'bottom':1, 'right':1, 'top':1,})
        header_style = workbook.add_format({'font_name': 'Times', 'bold': True, 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'center'})
        text_style = workbook.add_format({'font_name': 'Times', 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'left'})
        number_style = workbook.add_format({'font_name': 'Times', 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'center'})

        
        # recuperer la liste des chantiers
        chantiers = data['projet']
        chantier_obj = self.env['project.project'].search([('id', 'in', chantiers)])
        product_obj = self.env['product.product'].search([])

        partner_obj = self.env['res.partner'].search([])

        deb_1 = data['deb1']
        fin_1 = data['fin1']

       

        #formate la date pour la requete sql  
        deb_date = datetime.datetime.strptime(deb_1, '%d-%m-%y %H:%M:%S')
        fin_date = datetime.datetime.strptime(fin_1, '%d-%m-%y %H:%M:%S')

        req_date1 = deb_date.strftime("%m/%d/%Y")
        req_date2 = fin_date.strftime("%m/%d/%Y")

        for ch in chantier_obj: 
            sheet = workbook.add_worksheet(ch.name)
            # set the orientation to landscape
            sheet.set_landscape()
            # set up the paper size, 9 means A4
            sheet.set_paper(9)
            # set up the margin in inch
            sheet.set_margins(0.5,0.5,0.5,0.5)
            sheet.hide_gridlines(2)
 
            # set up the column width
            sheet.set_column('A:K', 15)
 
            # the report title
            # merge the A1 to E1 cell and apply the style font size : 14, font weight : bold
            sheet.merge_range(1,2,2,11, 'TABLEAU DU SUIVI DES LIVRAISONS DU CHANTIER %s' %(ch.name), title_style)
            #tab de livraison
            lines = []

            ordre_charg = """select sl.id ,sl.name as oc ,sl.origin from sales_chargement sl"""
            vehicle = """select fv.id,  fv.license_plate, fv.driver_id from fleet_vehicle fv"""
            livraison ="""
                select distinct sp.id,DATE(sp.date_done), sp.name as bl, sp.partner_id, sp.vehicle_id, 
                sp.origin as origin_sp, sl.id as oc_id ,sl.name as oc ,sl.origin as devis 
                from stock_picking sp  join sales_chargement as sl on sl.origin=sp.origin  
                where sp.state ='done' and DATE(sp.date_done) BETWEEN %s and %s"""
            livree = """select sml.product_id, sp.id, sml.qty_done as livree from stock_move_line sml 
                left join stock_picking sp on sp.id=sml.picking_id 
                left join stock_warehouse wh on wh.lot_stock_id=sml.location_id 
                where sp.state='done'"""
           

            

            params = req_date1, req_date2
            self._cr.execute(livraison, params)
            livraison_obj = self._cr.dictfetchall()

            self._cr.execute(ordre_charg)
            ordre_charg_obj = self._cr.dictfetchall()

            self._cr.execute(livree)
            livree_obj = self._cr.dictfetchall()

            self._cr.execute(vehicle)
            vehicle_obj = self._cr.dictfetchall()
            

            for livr in livraison_obj :
                
                
                if livr['partner_id'] == ch.partner_id.id :
                    id = livr['id']
                    print(id, "livre")
                    dat = livr['date']
                    qty = 0
                    product =""
                    partner = ""
                    chauff = ""
                    num_vh = ""
                    bl = livr['bl']
                    oc = livr['oc']
                    date = dat.strftime("%d/%m/%Y")
                    for part in partner_obj:
                        if part.id == livr['partner_id']:
                            partner = part.name
                    for vh in vehicle_obj :
                        if vh['id'] == livr['vehicle_id']:
                            num_vh = vh['license_plate']
                            for par in partner_obj :
                                if par.id == vh['driver_id'] :
                                    chauff = part.name
                    for lv in livree_obj :
                        
                        if lv['id'] == id:
                            qty = lv['livree']
                            pid = lv['product_id']
                            for pro in product_obj:
                                if pro.id == pid:
                                    product = pro.default_code
                            val = {
                            'date' : date,
                            'product' : product,
                            'qty' : qty,
                            'part' : partner,
                            'chauff' : chauff,
                            'vh' : num_vh,
                            'bl' : bl,
                            'oc' : oc,
                            }
                            lines.append(val)
            
                            

            com = """select sum(sol.product_uom_qty) as com 
            from sale_order_line sol join sale_order so on so.id=sol.order_id 
            where so.state in ('sale', 'valide') and so.partner_id=%s 
            and so.date_order between %s and %s"""
            chant_part = ch.partner_id.id if ch.partner_id.id else 0
            params1 = chant_part, req_date1, req_date2
            self._cr.execute(com, params1)
            com_obj = self._cr.dictfetchall()
            commander_total = 0
            # print("Jusqu'ici jk", com_obj)

            for comm in com_obj:
                commander_total = comm['com'] if comm['com'] else 0
                    
            liv_total = 0
            for li in lines:
                liv_total += li['qty']
            reste_liv = commander_total - liv_total

            
                    


            
             
        #     # # table title
            sheet.write('A6','DATES', header_style)
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
            sheet.write('L6','RESTE', header_style)
 
            row = 6
            col = 0

            if len(lines):
                for line in lines :
                    sheet.write(row, col, line['date'], number_style)
                    sheet.write(row, col + 1, line['product'], number_style)
                    sheet.write(row, col + 2, line['qty'], number_style)
                    sheet.write(row, col + 3, line['part'], number_style)
                    sheet.write(row, col + 4, line['chauff'], number_style)
                    sheet.write(row, col + 5, line['vh'], number_style)
                    sheet.write(row, col + 6, line['bl'], number_style)
                    sheet.write(row, col + 7, line['oc'], number_style)
                    sheet.write(row, col + 8, "", text_style)
                    sheet.write(row, col + 9, "", text_style)
                    sheet.write(row, col + 10, "", text_style)
                    sheet.write(row, col + 11, "", text_style)
                    row  += 1
                sheet.write(row, col + 9, commander_total, header_style)
                sheet.write(row, col + 10, liv_total, header_style)
                sheet.write(row, col + 11, reste_liv, header_style)
                row += 1
        
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
 
        return response

      