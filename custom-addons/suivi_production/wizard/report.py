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
class SuiviProduction(models.TransientModel):
    _name = "suivi.production.report.wizard"

    select_type = fields.Selection(
        string='Type de suivi',
        selection=[('an', 'Annuel'), ('men', 'Mensuel'), ('sem', 'Semaine')],
        default='sem'
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
    def suivi_xlsx(self):

        data = {
            'date_deb': self.date_deb.strftime("%m/%d/%Y"),
            'date_fin': self.date_fin.strftime("%m/%d/%Y"),
            'type': self.select_type,
            'annee': self.annee,
            'date_stock':self.date_deb.strftime('%Y-%m-%d %H:%M:%S'),
            'deb1': self.date_deb.strftime('%d-%m-%y %H:%M:%S'),
            'fin1': self.date_fin.strftime('%d-%m-%y %H:%M:%S'),
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'suivi.production.report.wizard',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'RAPPORT PRODUCTION',
                     },
            'report_type': 'stock_xlsx',
        }


    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # create some style to set up the font type, the font size, the border, and the aligment
        title_style = workbook.add_format({'font_name': 'Times', 'font_size': 13, 'bold': True, 'align': 'center','valign': 'vcenter','left': 1, 'bottom':1, 'right':1, 'top':1, 'text_wrap': True})
        title_style21 = workbook.add_format({'font_name': 'Times', 'bold': True, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
        title_style1 = workbook.add_format({'font_name': 'Times', 'font_color':'red','font_size': 23, 'bold': True, 'align': 'center', 'valign': 'vcenter','left': 1, 'bottom':1, 'right':1, 'top':1, 'text_wrap': True})
        header_style = workbook.add_format({'font_name': 'Times', 'bold': True, 'align': 'center', 'text_wrap': True, 'bg_color':'#D9D9D9','left': 1, 'bottom':1, 'right':1, 'top':1,})
        text_style = workbook.add_format({'font_name': 'Times', 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'left', 'text_wrap': True})
        number_style = workbook.add_format({'font_name': 'Times', 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'center','valign': 'vcenter', 'text_wrap': True})
        number_style1 = workbook.add_format({'font_name': 'Times','bold': True, 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'center','valign': 'vcenter', 'text_wrap': True})


        #tableau contenant  la production 
        lines=[]

        if data['type'] == 'an':
            deb = datetime.date(data['annee'], 1, 1)
            fin = datetime.date(data['annee'], 12, 31)
            deb_1 = deb.strftime('%d-%m-%y %H:%M:%S')
            fin_1 = fin.strftime('%d-%m-%y %H:%M:%S')
            day = 365
        
        elif data['type'] == 'men':
            deb_1 = data['deb1']
            fin_1 = data['fin1']
            day = 31
        else :
            deb_1 = data['deb1']
            fin_1 = data['fin1']
            day = 7
            
        #formate la date pour la requete sql  
        deb_date = datetime.datetime.strptime(deb_1, '%d-%m-%y %H:%M:%S')
        fin_date = datetime.datetime.strptime(fin_1, '%d-%m-%y %H:%M:%S')
        #recupere les articles  a fabriquer
        article_obj = self.env['product.product'].search([])
        
        #parcours la production a une periode definie
        while deb_date <= fin_date:
            date = deb_date + timedelta(days=day)
            req_date1 = deb_date.strftime("%m/%d/%Y")
            req_date11 = deb_date.strftime("%A %d %B %Y")
            req_date2 = date.strftime("%m/%d/%Y")
            if data['type'] == 'an':
                name_report = data['annee']
                titre =  data['annee']
            else:
                titre =  req_date11
                name_report = req_date11
        
            # date = deb_date + timedelta(days=1)
            # req_date = date.strftime("%m/%d/%Y")
            sheet = workbook.add_worksheet("suivi %s"%(name_report))
            # set the orientation to landscape
            sheet.set_landscape()
            # set up the paper size, 9 means A4
            sheet.set_paper(9)
            # set up the margin in inch
            sheet.set_margins(0.5,0.5,0.5,0.5)
            sheet.hide_gridlines(2)
            # set up the column width
            sheet.set_column('A:A', 4)
            sheet.set_column('B:B', 15)
            sheet.set_column('C:C', 25)
            sheet.set_column('D:D', 14)
            sheet.set_column('E:E', 17)
            sheet.set_column('F:F', 15)
            # sheet.set_row(0, 40)
            #en-tete du  rapport de production 
            sheet.merge_range(0,2,3,3, 'RAPPORT D ACTIVITES DE PRODUCTION' , title_style)
            sheet.merge_range(0,4,3,4, 'PRQ 004 ENG9/A' , title_style)
            sheet.merge_range(4,0,4,4, titre , title_style21)
            sheet.write('A6','N°', header_style)
            sheet.write('B6','DESIGNATION', header_style)
            sheet.write('C6','QUANTITES PRODUITES', header_style)
            sheet.write('D6','PRIX UNITAIRE', header_style)
            sheet.write('E6','PRIX TOTAL', header_style)
            #permet de recuperer les quantites produites
            produite = """SELECT m.product_id, sum(m.product_qty) AS qte_prod FROM  mrp_production AS m
                JOIN stock_warehouse AS wh ON wh.lot_stock_id = m.location_dest_id 
                WHERE DATE(m.create_date) BETWEEN %s AND %s AND state='done' group by m.product_id"""

            produite1 = """select m.product_id, sum(m.qty_producing) as qte_prod 
                from mrp_production as m  
                where m.state in ('progress','to_close','done','confirmed') and DATE(m.create_date) BETWEEN %s AND %s
                group by product_id"""
            
            #permet de recuperer les matieres premieres utilisees(nomenclature)
            pour = """select mrp.product_id as fab, stm.product_id as comp, pt.default_code 
                from stock_move as stm 
                left join mrp_production as mrp on mrp.id=stm.raw_material_production_id 
                left join product_template as pt on pt.id=mrp.product_id 
                where  stm.is_done=True  and mrp.state in ('progress','to_close','done','confirmed') 
                and DATE(stm.create_date) between %s and %s
                group by mrp.product_id, stm.product_id, pt.default_code"""


            composants = """select stm.product_id, sum(stm.quantity_done)  as qty_done
                from stock_move as stm 
                left join mrp_production mrp on mrp.id=stm.raw_material_production_id 
                where  stm.is_done=True  and mrp.state in ('progress','to_close','done','confirmed') 
                and DATE(stm.create_date) between %s and %s group by stm.product_id"""

            planification = """select  mrp.product_id as id, sum(mrp.product_qty) as plan
                from mrp_production as mrp 
                where DATE(mrp.date_planned_start) between %s and %s and mrp.state in ('confirmed', 'progress', 'to_close', 'done')
                group by product_id"""

            planif_nbr = """select  mrp.id as id
                from mrp_production as mrp 
                where DATE(mrp.date_planned_start) between %s and %s and mrp.state in ('confirmed', 'progress', 'to_close', 'done')
                """
            realiser_nbre = """select  mrp.id as id
                from mrp_production as mrp 
                where DATE(mrp.date_planned_start) between %s and %s and mrp.state in ('to_close', 'done')
                """
            casse_prod = """SELECT sc.product_id, sum(sc.scrap_qty) AS scrap_qty FROM stock_scrap AS sc 
                JOIN mrp_production as p ON sc.product_id = p.product_id 
                INNER JOIN stock_warehouse AS wh ON wh.lot_stock_id = p.location_dest_id 
                WHERE sc.state IN ('done', 'Done') AND p.state ='done' 
                AND DATE(date_done) BETWEEN %s AND %s  GROUP BY sc.product_id"""
            
            
            params = req_date1,req_date2

            # quantite produite pour une periode
            self._cr.execute(produite1, params)
            prod_obj = self._cr.dictfetchall()

            # quantite casse production pour une periode
            self._cr.execute(casse_prod, params)
            casse_prod_obj = self._cr.dictfetchall()

            # produit et matiere premiere
            self._cr.execute(pour, params)
            pour_obj = self._cr.dictfetchall()

            # planification fabrication pour une periode
            self._cr.execute(planification, params)
            planification_obj = self._cr.dictfetchall()

            # nombre ordre de production planifier pour la periode
            self._cr.execute(planif_nbr, params)
            planif_nbr_obj = self._cr.dictfetchall()

            # nombre ordre de production terminer
            self._cr.execute(realiser_nbre, params)
            realiser_nbre_obj = self._cr.dictfetchall()

            # matiere premiere utilisee pour une periode
            self._cr.execute(composants, params)
            composant_obj = self._cr.dictfetchall()

            lines = []

            #recupere les lignes de production
            if len(article_obj) > 0 :
                for obj in article_obj:
                    qty = 0
                    prix_total=0
                    if len(prod_obj) > 0 :
                        for pro in prod_obj:
                            if obj.id == pro['product_id']:
                                qty = pro['qte_prod']
                                prix_total = qty*obj.standard_price
                                line = {
                                    "id":obj.id,
                                    "designation":obj.product_tmpl_id.default_code,
                                    "qty":qty,
                                    "pu":obj.standard_price,
                                    "pt":prix_total,
                                }
                                lines.append(line)
            row = 6
            col = 0
            id =1

            # recuperer les casses de production 
            casse = 0
            if len(prod_obj) > 0 :
                for obj in prod_obj:
                    if len(casse_prod_obj) > 0 :
                        for ob in casse_prod_obj:
                            if obj['product_id'] == ob['product_id'] :
                                casse += ob['scrap_qty']

           

            matiere_obj =[]
            #recupere les  lines de matieres premieres
            if len(article_obj) > 0 :
                for obj in article_obj:
                    qty_use = 0
                    pu = 0
                    pt = 0
                    designa = ""
                    if len(composant_obj) > 0 :
                        for mat in composant_obj:
                            if obj.id == mat['product_id']:
                                qty_use = mat['qty_done']
                                prix_total = qty_use*obj.standard_price
                                designa = obj.product_tmpl_id.name
                                line_mat = {
                                    'id': obj.id,
                                    'designation' : designa,
                                    'qty' : qty_use,
                                    'pu' : obj.standard_price,
                                    'pt' : prix_total,
                                }
                                matiere_obj.append(line_mat)
            pour_val = []
            

            if len(matiere_obj) > 0 :
                for mat in matiere_obj:
                    pour_name = ""
                    if len(pour_obj) > 0 :
                        for p in pour_obj:
                            if p['comp'] == mat['id']:
                                pour_name += p['default_code'] + '  '
                        val = {
                            'designation': mat['designation'],
                            'pour': pour_name,
                            'qty': mat['qty'],
                            'pu': mat['pu'],
                            'pt': mat['pt'],
                        }
                        pour_val.append(val)

            

            #affiche les lignes de production
            if len(lines) > 0 :
                for line in lines:
                    sheet.write(row,col,id ,number_style)
                    sheet.write(row,col + 1,line['designation'] ,number_style)
                    sheet.write(row,col + 2,line['qty'] ,number_style)
                    sheet.write(row,col + 3,line['pu'] ,number_style)
                    sheet.write(row,col + 4,line['pt'] ,number_style)
                    row += 1
                    id += 1
            prix_prod = 0
            qty_totale = 0
            if len(lines) > 0:
                for line in lines:
                    prix_prod += line['pt']
                    qty_totale += line['qty']
            sheet.write(row,col , id, number_style1 )
            sheet.write(row,col + 1, "TOTAL", number_style1 )
            sheet.write(row,col + 2, qty_totale, number_style1 )
            sheet.write(row,col + 3, "", number_style1 )
            sheet.write(row,col + 4, prix_prod, number_style1 )
            row += 1

            #pourcentage casses
            casse_pourcentage = 0
            if qty_totale > 0 :
                casse_pourcentage = (casse / qty_totale) * 100
                casse_pourcentage = round(casse_pourcentage, 2)



            plan = 0
            prix_plan = 0

            if len(planification_obj) > 0 :
                for ob in planification_obj:
                    plan += ob['plan']
            pour_plan = 0

            if len(article_obj) > 0 :
                for obj in article_obj:
                    if len(planification_obj) > 0 :
                        for ob in planification_obj:
                            if obj.id == ob['id']:
                                prix_plan += ob['plan']* obj.standard_price
            if prix_plan != 0 :
                pourcen_realisation = (prix_prod/prix_plan)*100
                pourcen_realisation = round(pourcen_realisation , 2)
            else:
                pourcen_realisation = 0

            if plan !=0 :
                pour_plan = qty_totale/plan
                pour_plan *= 100
                pour_plan = round(pour_plan, 2)
            plan_val = pour_plan if pour_plan > 0 else ""

            taux_pro_plan = 0
            if len(planif_nbr_obj) > 0:
                taux_pro_plan = (len(realiser_nbre_obj)/len(planif_nbr_obj))*100
                taux_pro_plan = round(taux_pro_plan, 2)
                


            sheet.merge_range(row,col,row,col + 4, '' , text_style)
            row += 1
            sheet.write(row,col , '', number_style1 )
            sheet.write(row,col + 1, "%. de réalisation", text_style )
            sheet.write(row,col + 2, pourcen_realisation, number_style1 )
            sheet.write(row,col + 3, "sur les prévisions de ", text_style )
            sheet.write(row,col + 4, prix_plan, number_style1 )
            row += 2
            id +=1
            sheet.merge_range(row,col,row,col + 1, 'Difficultés :' , header_style)
            row +=1
            sheet.set_row(row, 60)
            sheet.merge_range(row,col,row,col + 4, '' , text_style)
            row += 1
            sheet.merge_range(row,col,row,col + 1, 'Solutions envisagées:' , header_style)
            row += 1
            sheet.set_row(row, 25)
            sheet.merge_range(row,col,row,col + 4, '' , text_style)
            row += 1
            sheet.merge_range(row,col,row,col + 1, 'Autres activités:  ' , header_style)
            row += 1
            sheet.set_row(row, 15)
            sheet.merge_range(row,col,row,col + 4, '' , text_style)
            row += 3

            #en-tete des matieres premieres                
            sheet.merge_range(row,0,row,4, "MATIERES PREMIERES UTILISEES" , title_style21)
            row +=1
            sheet.write(row, col,'N°', header_style)
            sheet.write(row, col + 1,'DESIGNATION', header_style)
            sheet.write(row, col + 2,'pour...', header_style)
            sheet.write(row, col + 3,'Qte(en kg)', header_style)
            sheet.write(row, col + 4,'PRIX UNITAIRE', header_style)
            sheet.write(row, col + 5,'PRIX TOTAL', header_style)
            row += 1
            id = 1
            #affiche les lignes des matieres premieres
            if len(pour_val) > 0 :
                for line in pour_val:
                    sheet.write(row,col,id ,number_style)
                    sheet.write(row,col + 1,line['designation'] ,number_style)
                    sheet.write(row,col + 2,line['pour'] ,number_style)
                    sheet.write(row,col + 3,line['qty'] ,number_style)
                    sheet.write(row,col + 4,line['pu'] ,number_style)
                    sheet.write(row,col + 5,line['pt'] ,number_style)
                    row += 1
                    id += 1
            prix_comp = 0
            qty_total_comp = 0
            if len(matiere_obj) > 0 :
                for line in matiere_obj:
                    prix_comp += line['pt']
                    qty_total_comp += line['qty']
            #ration prix_comp_total/prix_fab_total
            rat_num = 0
            rat_den = 0
            if len(matiere_obj) > 0 :
                for line in matiere_obj:
                    rat_num += line['pt']
            if len(lines) > 0 :
                for line in lines:
                    rat_den += line['pt']
            ratio = 0
            if rat_num != 0 and rat_den != 0 :
                ratio = rat_num/rat_den
                ratio *= 100
                ratio = round(ratio, 2)
            aff = ratio
            affiche = aff if ratio > 0 else ""

            
            sheet.write(row,col , id, number_style1 )
            sheet.write(row,col + 1, "TOTAL", number_style1 )
            sheet.write(row,col + 2, "", number_style1 )
            sheet.write(row,col + 3, qty_total_comp, number_style1 )
            sheet.write(row,col + 4, "", number_style1 )
            sheet.write(row,col + 5, prix_comp, number_style1 )
            row += 1
            sheet.merge_range(row,col,row,col + 5, '' , text_style)
            row += 1
            sheet.write(row,col , '', number_style1 )
            sheet.write(row,col + 1, "RATIO", number_style1 )
            sheet.write(row,col + 2, affiche, number_style1 )
            sheet.write(row,col + 3, "%.", number_style1 )
            sheet.write(row,col + 4, "", number_style1 )
            sheet.write(row,col + 5, "", number_style1 )
            row += 2
            id +=1
            sheet.merge_range(row,col,row,col + 1, 'Prévision :' , header_style)
            row +=1
            sheet.set_row(row, 40)
            sheet.merge_range(row,col,row,col + 5, '' , text_style)
            row += 1
            sheet.write(row,col , '', number_style1 )
            sheet.write(row,col + 1, "KPI", header_style )
            sheet.write(row,col + 2, "", number_style1 )
            sheet.write(row,col + 3, "", text_style )
            sheet.write(row,col + 4, "pourcentage", header_style )
            sheet.write(row,col + 5, "", number_style1 )
            row += 1
            # sheet.set_row(row, 40)
            sheet.merge_range(row,col,row,col + 2, 'taux de rendement synthétique' , text_style)
            sheet.merge_range(row,col + 3,row,col + 5, plan_val , number_style)
            row += 1
            sheet.merge_range(row,col,row,col + 2, 'taux de réalisation des productions  planifiées' , text_style)
            sheet.merge_range(row,col + 3,row,col + 5, taux_pro_plan , number_style)
            row += 1
            sheet.merge_range(row,col,row,col + 2, 'taux de perte matières en cours de production(ciment)' , text_style)
            sheet.merge_range(row,col + 3,row,col + 5, '' , number_style)
            row += 1
            sheet.merge_range(row,col,row,col + 2, 'taux de casses' , text_style)
            sheet.merge_range(row,col + 3,row,col + 5, casse_pourcentage , number_style)
            row += 1
            sheet.merge_range(row,col ,row,col + 5, 'Le responsable de production' , header_style)

            deb_date = date

            #permet de fixer une colonne
            # sheet.freeze_panes(10,0)
            

         
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
 
        return response