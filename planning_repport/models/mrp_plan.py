# -*- coding:utf-8 -*-

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
class MrpPlan(models.Model):
    _inherit = 'mrp.plan'



    week_ids = fields.One2many(
        string='Production Semaine',
        comodel_name='plan.mensuel.line',
        inverse_name='plan_id',
    )
    
    
    def copy(self, default=None):
        default = default or {}
        list_plan_raws = self.plan_raw_ids
        new_plan_raws = []
        for plan in list_plan_raws:
            new_plan_raws.append((0, 0, {'id': plan.id,
                                        'priority': plan.priority,
                                        'jour': plan.jour,
                                        'backorder_sequence': plan.backorder_sequence,
                                        'origin': plan.origin,
                                        'product_id': plan.product_id.id,
                                        'product_qty': plan.product_qty,
                                        'product_uom_id': plan.product_uom_id.id,
                                        'lot_producing_id': plan.lot_producing_id.id,
                                        'qty_producing': plan.qty_producing,
                                        'product_uom_qty': plan.product_uom_qty,
                                        'picking_type_id': plan.picking_type_id.id,
                                        'location_src_id': plan.location_src_id.id,
                                        'location_dest_id': plan.location_dest_id.id,
                                        'date_planned_start': plan.date_planned_start,
                                        'date_planned_finished': plan.date_planned_finished,
                                        'date_deadline': plan.date_deadline,
                                        'date_start': plan.date_start,
                                        'date_finished': plan.date_finished,
                                        'bom_id': plan.bom_id.id,
                                        'state': plan.state,
                                        'reservation_state': plan.reservation_state,
                                        'user_id': plan.user_id.id,
                                        'company_id': plan.company_id.id,
                                        }))
        week_ids = self.week_ids
        new_week_ids = []
        for plan in week_ids:
            new_week_ids.append((0, 0, {'id': plan.id,
                                        'debut_date': plan.debut_date,
                                        'fin_date': plan.fin_date,
                                        'production_id': plan.production_id.id,
                                        }))
        default['plan_raw_ids'] = new_plan_raws
        default['week_ids'] = new_week_ids
        default['type'] = self.type
    
    

        return super(MrpPlan, self).copy(default)

    def planning_repport(self):

        data = {
            'model_id': self.id,
            'type' : self.type,
        }

        return {
            'type': 'ir.actions.report',
            'data': {'model': 'mrp.plan',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Planning de production',
                     },
            'report_type': 'stock_xlsx',
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # create some style to set up the font type, the font size, the border, and the aligment
        title_style = workbook.add_format({'font_name': 'Times', 'font_size': 12, 'bold': True, 'align': 'center','valign': 'vcenter', 'text_wrap': True})
        title_style21 = workbook.add_format({'font_name': 'Times','font_size': 14,'bg_color':'#D3C2', 'bold': True, 'align': 'center', 'valign': 'vcenter','left': 2, 'bottom':2, 'right':2, 'top':2, 'text_wrap': True})
        header_style = workbook.add_format({'font_name': 'Times', 'bold': True,'bg_color':'#D9D9D9', 'align': 'center', 'valign': 'vcenter','left': 2, 'bottom':2, 'right':2, 'top':2, 'text_wrap': True})
        title_style1 = workbook.add_format({'font_name': 'Times', 'font_color':'red','font_size': 23, 'bold': True, 'align': 'center', 'valign': 'vcenter','left': 1, 'bottom':1, 'right':1, 'top':1, 'text_wrap': True})
        text_style = workbook.add_format({'font_name': 'Times', 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'center','valign': 'vcenter', })
        text_style1 = workbook.add_format({'font_name': 'Times', 'left': 1, 'bottom':1, 'bold': True,'right':1, 'top':1, 'align': 'center','valign': 'vcenter', })
        number_style = workbook.add_format({'font_name': 'Times', 'left': 1, 'bottom':1, 'right':1, 'top':1, 'align': 'center','valign': 'vcenter', 'text_wrap': True})


        if data['type'] == 'heb':
            plan_obj = self.env['mrp.plan'].search([('id', '=', data['model_id'])])
            plan_line_obj = self.env['mrp.production'].search([('plan_production_id', '=', data['model_id'])])
            lundi_obj = self.env['mrp.production'].search([('plan_production_id', '=', data['model_id']),('jour', 'in',['Monday','Lundi','lundi','monday'])])
            mardi_obj = self.env['mrp.production'].search([('plan_production_id', '=', data['model_id']),('jour', 'in',['Tuesday','Mardi','tuesday','mardi'])])
            mecredi_obj = self.env['mrp.production'].search([('plan_production_id', '=', data['model_id']),('jour', 'in',['Wednesday','Mercredi','mednesday','mercredi'])])
            jeudi_obj = self.env['mrp.production'].search([('plan_production_id', '=', data['model_id']),('jour', 'in',['Thursday','Jeudi','thursday','jeudi'])])
            vendredi_obj = self.env['mrp.production'].search([('plan_production_id', '=', data['model_id']),('jour', 'in',['Friday','Vendredi','friday','vendredi'])])
            samedi_obj = self.env['mrp.production'].search([('plan_production_id', '=', data['model_id']),('jour', 'in',['Saturday','Samedi','saturday','samedi'])])
            mat_obj = self.env['product.product'].search([('product_tmpl_id.categ_id.name', 'in', ['Matières premières','Matières premières / Briqueterie','Matières premières / Commune', 'Matières premières / Tuilerie'])])



            print(mat_obj,"Liste des matieres premieres")
            lundi_line = []
            lundi_objectif = {'produit': '','objectif' : '', 'maintemp' : '','mainreq' : ''}
            if len(lundi_obj) >0:
                for lun in lundi_obj:
                    lundi_objectif['produit'] = lun.product_id.default_code
                    lundi_objectif['objectif'] = lun.product_qty
                    lundi_objectif['maintemp'] = lun.main_oeuvre_temporaire
                    lundi_objectif['mainreq'] = lun.main_oeuvre_requise
                    for matiere in lun.move_raw_ids:
                        cle = matiere.product_id.id
                        qty = matiere.product_uom_qty
                        unite = matiere.product_uom.name
                        pour = lun.product_id.default_code
                        val1 = {
                            'qty' : qty,
                            'unite' : unite,
                            'pour' : pour,
                        }
                        val ={
                            cle : val1,
                        }
                        lundi_line.append(val)
            mardi_line = []
            mardi_objectif = {'produit': '','objectif' : '', 'maintemp' : '','mainreq' : ''}
            if len(mardi_obj) >0:
                for lun in mardi_obj:
                    mardi_objectif['produit'] = lun.product_id.default_code
                    mardi_objectif['objectif'] = lun.product_qty
                    mardi_objectif['maintemp'] = lun.main_oeuvre_temporaire
                    mardi_objectif['mainreq'] = lun.main_oeuvre_requise
                    for matiere in lun.move_raw_ids:
                        cle = matiere.product_id.id
                        qty = matiere.product_uom_qty
                        unite = matiere.product_uom.name
                        pour = lun.product_id.default_code
                        val1 = {
                            'qty' : qty,
                            'unite' : unite,
                            'pour' : pour,
                        }
                        val ={
                            cle : val1,
                        }
                        mardi_line.append(val)
            mercredi_line = []
            mercredi_objectif = {'produit': '','objectif' : '', 'maintemp' : '','mainreq' : ''}
            if len(mecredi_obj) >0:
                for lun in mecredi_obj:
                    mercredi_objectif['produit'] = lun.product_id.default_code
                    mercredi_objectif['objectif'] = lun.product_qty
                    mercredi_objectif['maintemp'] = lun.main_oeuvre_temporaire
                    mercredi_objectif['mainreq'] = lun.main_oeuvre_requise
                    for matiere in lun.move_raw_ids:
                        cle = matiere.product_id.id
                        qty = matiere.product_uom_qty
                        unite = matiere.product_uom.name
                        pour = lun.product_id.default_code
                        val1 = {
                            'qty' : qty,
                            'unite' : unite,
                            'pour' : pour,
                        }
                        val ={
                            cle : val1,
                        }
                        mercredi_line.append(val)
            jeudi_line = []
            jeudi_objectif = {'produit': '','objectif' : '', 'maintemp' : '','mainreq' : ''}
            if len(jeudi_obj) >0:
                for lun in jeudi_obj:
                    jeudi_objectif['produit'] = lun.product_id.default_code
                    jeudi_objectif['objectif'] = lun.product_qty
                    jeudi_objectif['maintemp'] = lun.main_oeuvre_temporaire
                    jeudi_objectif['mainreq'] = lun.main_oeuvre_requise
                    for matiere in lun.move_raw_ids:
                        cle = matiere.product_id.id
                        qty = matiere.product_uom_qty
                        unite = matiere.product_uom.name
                        pour = lun.product_id.default_code
                        val1 = {
                            'qty' : qty,
                            'unite' : unite,
                            'pour' : pour,
                        }
                        val ={
                            cle : val1,
                        }
                        jeudi_line.append(val)
            vendredi_line = []
            vendredi_objectif = {'produit': '','objectif' : '', 'maintemp' : '','mainreq' : ''}
            if len(vendredi_obj) >0:
                for lun in vendredi_obj:
                    vendredi_objectif['produit'] = lun.product_id.default_code
                    vendredi_objectif['objectif'] = lun.product_qty
                    vendredi_objectif['maintemp'] = lun.main_oeuvre_temporaire
                    vendredi_objectif['mainreq'] = lun.main_oeuvre_requise
                    for matiere in lun.move_raw_ids:
                        cle = matiere.product_id.id
                        qty = matiere.product_uom_qty
                        unite = matiere.product_uom.name
                        pour = lun.product_id.default_code
                        val1 = {
                            'qty' : qty,
                            'unite' : unite,
                            'pour' : pour,
                        }
                        val ={
                            cle : val1,
                        }
                        vendredi_line.append(val)
            samedi_line = []
            samedidi_objectif = {'produit': '','objectif' : '', 'maintemp' : '','mainreq' : ''}
            if len(samedi_obj) >0:
                for lun in samedi_obj:
                    samedidi_objectif['produit'] = lun.product_id.default_code
                    samedidi_objectif['objectif'] = lun.product_qty
                    samedidi_objectif['maintemp'] = lun.main_oeuvre_temporaire
                    samedidi_objectif['mainreq'] = lun.main_oeuvre_requise
                    for matiere in lun.move_raw_ids:
                        cle = matiere.product_id.id
                        qty = matiere.product_uom_qty
                        unite = matiere.product_uom.name
                        pour = lun.product_id.default_code
                        val1 = {
                            'qty' : qty,
                            'unite' : unite,
                            'pour' : pour,
                        }
                        val ={
                            cle : val1,
                        }
                        samedi_line.append(val)
            
            lines_obj = []
            for mat in mat_obj :
                lundi = 0
                mardi = 0
                um_ach = mat.product_tmpl_id.uom_name
                name = mat.product_tmpl_id.name
                mercredi = 0
                jeudi = 0
                vendredi = 0
                samedi = 0
                total = 0
                unite = mat.product_tmpl_id.uom_name
                for lun in lundi_line:
                    if mat.id in lun.keys():
                        lundi = lun[mat.id]['qty']
                        unite = lun[mat.id]['unite']
                for lun in mardi_line:
                    if mat.id in lun.keys():
                        unite = lun[mat.id]['unite']
                        mardi = lun[mat.id]['qty']
                for lun in mercredi_line:
                    if mat.id in lun.keys():
                        unite = lun[mat.id]['unite']
                        mercredi = lun[mat.id]['qty']
                for lun in jeudi_line:
                    if mat.id in lun.keys():
                        unite = lun[mat.id]['unite']
                        jeudi = lun[mat.id]['qty']
                for lun in vendredi_line:
                    if mat.id in lun.keys():
                        unite = lun[mat.id]['unite']
                        vendredi = lun[mat.id]['qty']
                for lun in samedi_line:
                    if mat.id in lun.keys():
                        unite = lun[mat.id]['unite']
                        samedi = lun[mat.id]['qty']
                total = lundi + mardi + mercredi + jeudi + vendredi + samedi
                val = {
                    'name' : name + ' (en '+  um_ach + ')',
                    'unite_achat' : um_ach,
                    'lundi' : lundi,
                    'mardi' : mardi,
                    'mercredi' : mercredi,
                    'jeudi' : jeudi,
                    'vendredi' : vendredi,
                    'samedi' : samedi,
                    'total' : total,
                    'unite' : unite,
                }

                lines_obj.append(val)
            print(lines_obj)

            # lines = sorted(lines_obj, key=lambda d: d['name']) 
            # lines_obj = lines
                
                        
                        
                        


            date =""
            for ob in plan_obj :
                date = datetime.datetime.strftime(ob.production_date, "%d %B %Y") + ' au '+ datetime.datetime.strftime(ob.production_date_fin, "%d %B %Y")
                exo = datetime.datetime.strftime(ob.production_date, "%B %Y") 

            sheet = workbook.add_worksheet("Analyse couts matieres premieres")
            # set the orientation to landscape
            sheet.set_landscape()
            # set up the margin in inch
            sheet.set_margins(0.5,0.5,0.5,0.5)
            sheet.hide_gridlines(2)
            # set up the column width
            sheet.set_column('A:A', 12)
            sheet.set_column('B:B', 25)
            sheet.set_column('C:I', 12)
            sheet.set_column('J:J', 14)
            sheet.set_row(5, 27)
            sheet.set_row(10, 20)
            sheet.merge_range(0,7,0,9, 'Exercice %s'%(exo), title_style)
            sheet.merge_range(1,7,1,9, 'SERVICE TECHNIQUE', title_style)
            sheet.merge_range(2,7,3,9, 'DÉPARTEMENT PRODUCTION', title_style)
            sheet.merge_range(5,2,5,9, 'PLANNING DE PRODUCTION', title_style21)
            sheet.merge_range(7,0,8,1, 'DÉSIGNATION', header_style)
            sheet.merge_range(7,2,7,8, 'Semaine du %s'%(date), header_style)
            sheet.merge_range(7,9,10,9, 'CONSOMMATION TOTALE DE LA SEMAINE', header_style)
            col = 2
            sheet.write(8,col, "Lundi", header_style)
            sheet.write(8,col + 1, "Mardi", header_style)
            sheet.write(8,col + 2, "Mercredi", header_style)
            sheet.write(8,col + 3, "Jeudi", header_style)
            sheet.write(8,col + 4, "Vendredi", header_style)
            sheet.write(8,col + 5, "Samedi", header_style)
            sheet.write(8,col + 6, "Qte Camion", header_style)

            sheet.write(9,col, lundi_objectif['produit'], header_style)
            sheet.write(9,col + 1, mardi_objectif['produit'], header_style)
            sheet.write(9,col + 2, mercredi_objectif['produit'], header_style)
            sheet.write(9,col + 3, jeudi_objectif['produit'], header_style)
            sheet.write(9,col + 4, vendredi_objectif['produit'], header_style)
            sheet.write(9,col + 5, samedidi_objectif['produit'], header_style)
            sheet.write(9,col + 6, "", header_style)

            sheet.write(10,col, lundi_objectif['objectif'], header_style)
            sheet.write(10,col + 1, mardi_objectif['objectif'], header_style)
            sheet.write(10,col + 2, mercredi_objectif['objectif'], header_style)
            sheet.write(10,col + 3, jeudi_objectif['objectif'], header_style)
            sheet.write(10,col + 4, vendredi_objectif['objectif'], header_style)
            sheet.write(10,col + 5, samedidi_objectif['objectif'], header_style)
            sheet.write(10,col + 6, "", header_style)


            sheet.write('A10', 'Unité de mesure', header_style)
            sheet.write('B10', 'Produits fabriqués', header_style)
            sheet.merge_range(10,0,10,1, 'OBJECTIF DE LA SEMAINE', header_style)

            col = 0
            row = 11
            

            for obj in lines_obj:
                sheet.write(row,col, obj['unite'], text_style1)
                sheet.write(row,col + 1, obj['name']  , text_style1)
                sheet.write(row,col + 2, obj['lundi']  , number_style)
                sheet.write(row,col + 3, obj['mardi']  , number_style)
                sheet.write(row,col + 4, obj['mercredi']  , number_style)
                sheet.write(row,col + 5, obj['jeudi']  , number_style)
                sheet.write(row,col + 6, obj['vendredi']  , number_style)
                sheet.write(row,col + 7, obj['samedi']  , number_style)
                sheet.write(row,col + 8, ''  , number_style)
                sheet.write(row,col + 9, obj['total']  , text_style1)
                row += 1
            sheet.set_row(row, 20)
            sheet.write(row,col, 'ETP (EFFECTIF TEMP PLEIN)', text_style1)
            sheet.write(row,col + 1, "main d'oeuvre requise" , text_style1)
            sheet.write(row,col + 2, lundi_objectif['mainreq']  , number_style)
            sheet.write(row,col + 3, mardi_objectif['mainreq'] , number_style)
            sheet.write(row,col + 4, mercredi_objectif['mainreq']  , number_style)
            sheet.write(row,col + 5, jeudi_objectif['mainreq']  , number_style)
            sheet.write(row,col + 6, vendredi_objectif['mainreq']  , number_style)
            sheet.write(row,col + 7, samedidi_objectif['mainreq']  , number_style)
            sheet.write(row,col + 8, ''  , number_style)
            sheet.write(row,col + 9, ''  , text_style1)
            row += 1

            sheet.set_row(row, 20)
            sheet.write(row,col, 'ETP (EFFECTIF TEMP PLEIN)', text_style1)
            sheet.write(row,col + 1, "main d'oeuvre temporaire requise" , text_style1)
            sheet.write(row,col + 2, lundi_objectif['maintemp']  , number_style)
            sheet.write(row,col + 3, mardi_objectif['maintemp'] , number_style)
            sheet.write(row,col + 4, mercredi_objectif['maintemp']  , number_style)
            sheet.write(row,col + 5, jeudi_objectif['maintemp']  , number_style)
            sheet.write(row,col + 6, vendredi_objectif['maintemp']  , number_style)
            sheet.write(row,col + 7, samedidi_objectif['maintemp']  , number_style)
            sheet.write(row,col + 8, ''  , number_style)
            sheet.write(row,col + 9, ''  , text_style1)
            row += 1

            qte_totale = 0
            for line in lines_obj:
                qte_totale +=line['total']

            sheet.set_row(row, 20)
            sheet.merge_range(row,0,row,1, 'Observations', text_style1)
            sheet.write(row,col + 1, "main d'oeuvre temporaire requise" , text_style1)
            sheet.write(row,col + 2, ''  , number_style)
            sheet.write(row,col + 3, '' , number_style)
            sheet.write(row,col + 4, ''  , number_style)
            sheet.write(row,col + 5, ''  , number_style)
            sheet.write(row,col + 6, ''  , number_style)
            sheet.write(row,col + 7, '' , number_style)
            sheet.write(row,col + 8, ''  , number_style)
            sheet.write(row,col + 9, qte_totale  , text_style1)
            row += 2
            sheet.write(row,col + 8, 'La production',title_style)


            # Mensual report

        else :

            plan_obj = self.env['mrp.plan'].search([('id', '=', data['model_id'])])
            mat_obj = self.env['product.product'].search([('product_tmpl_id.categ_id.name', 'in', ['Matières premières','Matières premières / Briqueterie','Matières premières / Commune', 'Matières premières / Tuilerie'])])
            print(mat_obj,"Liste des matieres 2")
            semaine1_obj = []
            semaine2_obj = []
            semaine3_obj = []
            semaine4_obj = []
            semaine5_obj = []
            semaine1_line = []
            semaine1_objectif = {'produit': '','objectif' : '', 'maintemp' : '','mainreq' : '', 'period' : ''}
            semaine2_line = []
            semaine2_objectif = {'produit': '','objectif' : '', 'maintemp' : '','mainreq' : '', 'period' : ''}
            semaine3_line = []
            semaine3_objectif = {'produit': '','objectif' : '', 'maintemp' : '','mainreq' : '', 'period' : ''}
            semaine4_line = []
            semaine4_objectif = {'produit': '','objectif' : '', 'maintemp' : '','mainreq' : '', 'period' : ''}
            semaine5_line = []
            semaine5_objectif = {'produit': '','objectif' : '', 'maintemp' : '','mainreq' : '', 'period' : ''}
            # recuperer les differentes semaines 
            for obj in plan_obj :
                if len(obj.week_ids) == 1:
                    semaine1_obj = self.env['mrp.production'].search([('id', '=', obj.week_ids[0].production_id.id)])
                    
                    dat1 = datetime.datetime.strftime(obj.week_ids[0].debut_date, "%d") + ' au '+ datetime.datetime.strftime(obj.week_ids[0].fin_date, "%d") + " " + datetime.datetime.strftime(obj.week_ids[0].fin_date, "%b")
                    semaine1_objectif['period'] = dat1
                    semaine1_objectif['maintemp'] = obj.week_ids[0].production_id.main_oeuvre_temporaire
                    semaine1_objectif['mainreq'] = obj.week_ids[0].production_id.main_oeuvre_requise

                elif len(obj.week_ids) == 2:
                    semaine1_obj = self.env['mrp.production'].search([('id', '=', obj.week_ids[0].production_id.id)])
                    semaine2_obj = self.env['mrp.production'].search([('id', '=', obj.week_ids[1].production_id.id)])
                    
                    dat1 = datetime.datetime.strftime(obj.week_ids[0].debut_date, "%d") + ' au '+ datetime.datetime.strftime(obj.week_ids[0].fin_date, "%d") + " " + datetime.datetime.strftime(obj.week_ids[0].fin_date, "%b")
                    dat2 = datetime.datetime.strftime(obj.week_ids[1].debut_date, "%d") + ' au '+ datetime.datetime.strftime(obj.week_ids[1].fin_date, "%d") + " " + datetime.datetime.strftime(obj.week_ids[1].fin_date, "%b")
                    semaine1_objectif['period'] = dat1
                    semaine2_objectif['period'] = dat2
                    semaine1_objectif['maintemp'] = obj.week_ids[0].production_id.main_oeuvre_temporaire
                    semaine1_objectif['mainreq'] = obj.week_ids[0].production_id.main_oeuvre_requise
                    semaine2_objectif['maintemp'] = obj.week_ids[1].production_id.main_oeuvre_temporaire
                    semaine2_objectif['mainreq'] = obj.week_ids[1].production_id.main_oeuvre_requise

                elif len(obj.week_ids) == 3:
                    semaine1_obj = self.env['mrp.production'].search([('id', '=', obj.week_ids[0].production_id.id)])
                    semaine2_obj = self.env['mrp.production'].search([('id', '=', obj.week_ids[1].production_id.id)])
                    semaine3_obj = self.env['mrp.production'].search([('id', '=', obj.week_ids[2].production_id.id)])
                   

                    dat1 = datetime.datetime.strftime(obj.week_ids[0].debut_date, "%d") + ' au '+ datetime.datetime.strftime(obj.week_ids[0].fin_date, "%d") + " " + datetime.datetime.strftime(obj.week_ids[0].fin_date, "%b")
                    dat2 = datetime.datetime.strftime(obj.week_ids[1].debut_date, "%d") + ' au '+ datetime.datetime.strftime(obj.week_ids[1].fin_date, "%d") + " " + datetime.datetime.strftime(obj.week_ids[1].fin_date, "%b")
                    dat3 = datetime.datetime.strftime(obj.week_ids[2].debut_date, "%d") + ' au '+ datetime.datetime.strftime(obj.week_ids[2].fin_date, "%d") + " " + datetime.datetime.strftime(obj.week_ids[2].fin_date, "%b")
                    semaine1_objectif['period'] = dat1
                    semaine2_objectif['period'] = dat2
                    semaine3_objectif['period'] = dat3
                    semaine1_objectif['maintemp'] = obj.week_ids[0].production_id.main_oeuvre_temporaire
                    semaine1_objectif['mainreq'] = obj.week_ids[0].production_id.main_oeuvre_requise
                    semaine2_objectif['maintemp'] = obj.week_ids[1].production_id.main_oeuvre_temporaire
                    semaine2_objectif['mainreq'] = obj.week_ids[1].production_id.main_oeuvre_requise
                    semaine3_objectif['maintemp'] = obj.week_ids[2].production_id.main_oeuvre_temporaire
                    semaine3_objectif['mainreq'] = obj.week_ids[2].production_id.main_oeuvre_requise

                elif len(obj.week_ids) == 4:
                    semaine1_obj = self.env['mrp.production'].search([('id', '=', obj.week_ids[0].production_id.id)])
                    semaine2_obj = self.env['mrp.production'].search([('id', '=', obj.week_ids[1].production_id.id)])
                    semaine3_obj = self.env['mrp.production'].search([('id', '=', obj.week_ids[2].production_id.id)])
                    semaine4_obj = self.env['mrp.production'].search([('id', '=', obj.week_ids[3].production_id.id)])

                    dat1 = datetime.datetime.strftime(obj.week_ids[0].debut_date, "%d") + ' au '+ datetime.datetime.strftime(obj.week_ids[0].fin_date, "%d") + " " + datetime.datetime.strftime(obj.week_ids[0].fin_date, "%b")
                    dat2 = datetime.datetime.strftime(obj.week_ids[1].debut_date, "%d") + ' au '+ datetime.datetime.strftime(obj.week_ids[1].fin_date, "%d") + " " + datetime.datetime.strftime(obj.week_ids[1].fin_date, "%b")
                    dat3 = datetime.datetime.strftime(obj.week_ids[2].debut_date, "%d") + ' au '+ datetime.datetime.strftime(obj.week_ids[2].fin_date, "%d") + " " + datetime.datetime.strftime(obj.week_ids[2].fin_date, "%b")
                    dat4 = datetime.datetime.strftime(obj.week_ids[3].debut_date, "%d") + ' au '+ datetime.datetime.strftime(obj.week_ids[3].fin_date, "%d") + " " + datetime.datetime.strftime(obj.week_ids[3].fin_date, "%b")
                    semaine1_objectif['period'] = dat1
                    semaine2_objectif['period'] = dat2
                    semaine3_objectif['period'] = dat3
                    semaine4_objectif['period'] = dat4
                    semaine1_objectif['maintemp'] = obj.week_ids[0].production_id.main_oeuvre_temporaire
                    semaine1_objectif['mainreq'] = obj.week_ids[0].production_id.main_oeuvre_requise
                    semaine2_objectif['maintemp'] = obj.week_ids[1].production_id.main_oeuvre_temporaire
                    semaine2_objectif['mainreq'] = obj.week_ids[1].production_id.main_oeuvre_requise
                    semaine3_objectif['maintemp'] = obj.week_ids[2].production_id.main_oeuvre_temporaire
                    semaine3_objectif['mainreq'] = obj.week_ids[2].production_id.main_oeuvre_requise
                    semaine4_objectif['maintemp'] = obj.week_ids[3].production_id.main_oeuvre_temporaire
                    semaine4_objectif['mainreq'] = obj.week_ids[3].production_id.main_oeuvre_requise

                elif len(obj.week_ids) == 5:
                    semaine1_obj = self.env['mrp.production'].search([('id', '=', obj.week_ids[0].production_id.id)])
                    semaine2_obj = self.env['mrp.production'].search([('id', '=', obj.week_ids[1].production_id.id)])
                    semaine3_obj = self.env['mrp.production'].search([('id', '=', obj.week_ids[2].production_id.id)])
                    semaine4_obj = self.env['mrp.production'].search([('id', '=', obj.week_ids[3].production_id.id)])
                    semaine5_obj = self.env['mrp.production'].search([('id', '=', obj.week_ids[4].production_id.id)])
                    
                    dat1 = datetime.datetime.strftime(obj.week_ids[0].debut_date, "%d") + ' au '+ datetime.datetime.strftime(obj.week_ids[0].fin_date, "%d") + " " + datetime.datetime.strftime(obj.week_ids[0].fin_date, "%b")
                    dat2 = datetime.datetime.strftime(obj.week_ids[1].debut_date, "%d") + ' au '+ datetime.datetime.strftime(obj.week_ids[1].fin_date, "%d") + " " + datetime.datetime.strftime(obj.week_ids[1].fin_date, "%b")
                    dat3 = datetime.datetime.strftime(obj.week_ids[2].debut_date, "%d") + ' au '+ datetime.datetime.strftime(obj.week_ids[2].fin_date, "%d") + " " + datetime.datetime.strftime(obj.week_ids[2].fin_date, "%b")
                    dat4 = datetime.datetime.strftime(obj.week_ids[3].debut_date, "%d") + ' au '+ datetime.datetime.strftime(obj.week_ids[3].fin_date, "%d") + " " + datetime.datetime.strftime(obj.week_ids[3].fin_date, "%b")
                    dat5 = datetime.datetime.strftime(obj.week_ids[4].debut_date, "%d") + ' au '+ datetime.datetime.strftime(obj.week_ids[4].fin_date, "%d") + " " + datetime.datetime.strftime(obj.week_ids[4].fin_date, "%b")
                    semaine1_objectif['period'] = dat1
                    semaine2_objectif['period'] = dat2
                    semaine3_objectif['period'] = dat3
                    semaine4_objectif['period'] = dat4
                    semaine5_objectif['period'] = dat5
                    semaine1_objectif['maintemp'] = obj.week_ids[0].production_id.main_oeuvre_temporaire
                    semaine1_objectif['mainreq'] = obj.week_ids[0].production_id.main_oeuvre_requise
                    semaine2_objectif['maintemp'] = obj.week_ids[1].production_id.main_oeuvre_temporaire
                    semaine2_objectif['mainreq'] = obj.week_ids[1].production_id.main_oeuvre_requise
                    semaine3_objectif['maintemp'] = obj.week_ids[2].production_id.main_oeuvre_temporaire
                    semaine3_objectif['mainreq'] = obj.week_ids[2].production_id.main_oeuvre_requise
                    semaine4_objectif['maintemp'] = obj.week_ids[3].production_id.main_oeuvre_temporaire
                    semaine4_objectif['mainreq'] = obj.week_ids[3].production_id.main_oeuvre_requise
                    semaine5_objectif['maintemp'] = obj.week_ids[4].production_id.main_oeuvre_temporaire
                    semaine5_objectif['mainreq'] = obj.week_ids[4].production_id.main_oeuvre_requise
            
            
            
            if len(semaine1_obj) > 0 :
                for sem in semaine1_obj:
                    semaine1_objectif['produit'] = sem.product_id.default_code
                    semaine1_objectif['objectif'] = sem.product_qty
                    for matiere in sem.move_raw_ids:
                        cle = matiere.product_id.id
                        qty = matiere.product_uom_qty
                        unite = matiere.product_uom.name
                        pour = sem.product_id.default_code
                        val1 = {
                            'qty' : qty,
                            'unite' : unite,
                            'pour' : pour,
                        }
                        val ={
                            cle : val1,
                        }
                        semaine1_line.append(val)
            
            if len(semaine2_obj) > 0 :
                for sem in semaine2_obj:
                    semaine2_objectif['produit'] = sem.product_id.default_code
                    semaine2_objectif['objectif'] = sem.product_qty
                    for matiere in sem.move_raw_ids:
                        cle = matiere.product_id.id
                        qty = matiere.product_uom_qty
                        unite = matiere.product_uom.name
                        pour = sem.product_id.default_code
                        val1 = {
                            'qty' : qty,
                            'unite' : unite,
                            'pour' : pour,
                        }
                        val ={
                            cle : val1,
                        }
                        semaine2_line.append(val)
            
            if len(semaine3_obj) > 0 :
                for sem in semaine3_obj:
                    semaine3_objectif['produit'] = sem.product_id.default_code
                    semaine3_objectif['objectif'] = sem.product_qty
                    for matiere in sem.move_raw_ids:
                        cle = matiere.product_id.id
                        qty = matiere.product_uom_qty
                        unite = matiere.product_uom.name
                        pour = sem.product_id.default_code
                        val1 = {
                            'qty' : qty,
                            'unite' : unite,
                            'pour' : pour,
                        }
                        val ={
                            cle : val1,
                        }
                        semaine3_line.append(val)
            
            if len(semaine4_obj) > 0 :
                for sem in semaine4_obj:
                    semaine4_objectif['produit'] = sem.product_id.default_code
                    semaine4_objectif['objectif'] = sem.product_qty
                    for matiere in sem.move_raw_ids:
                        cle = matiere.product_id.id
                        qty = matiere.product_uom_qty
                        unite = matiere.product_uom.name
                        pour = sem.product_id.default_code
                        val1 = {
                            'qty' : qty,
                            'unite' : unite,
                            'pour' : pour,
                        }
                        val ={
                            cle : val1,
                        }
                        semaine4_line.append(val)
            
            if len(semaine5_obj) > 0 :
                for sem in semaine5_obj:
                    semaine5_objectif['produit'] = sem.product_id.default_code
                    semaine5_objectif['objectif'] = sem.product_qty
                    for matiere in sem.move_raw_ids:
                        cle = matiere.product_id.id
                        qty = matiere.product_uom_qty
                        unite = matiere.product_uom.name
                        pour = sem.product_id.default_code
                        val1 = {
                            'qty' : qty,
                            'unite' : unite,
                            'pour' : pour,
                        }
                        val ={
                            cle : val1,
                        }
                        semaine5_line.append(val)
            

            lines_obj = []
            for mat in mat_obj :
                sem1 = 0
                sem2 = 0
                um_ach = mat.product_tmpl_id.uom_name
                name = mat.product_tmpl_id.name
                sem3 = 0
                sem4 = 0
                sem5 = 0
                total = 0
                unite = mat.product_tmpl_id.uom_name
                for sem in semaine1_line:
                    if mat.id in sem.keys():
                        sem1 = sem[mat.id]['qty']
                        unite = sem[mat.id]['unite']
                for sem in semaine2_line:
                    if mat.id in sem.keys():
                        sem2 = sem[mat.id]['qty']
                        unite = sem[mat.id]['unite']
                for sem in semaine3_line:
                    if mat.id in sem.keys():
                        sem3 = sem[mat.id]['qty']
                        unite = sem[mat.id]['unite']
                for sem in semaine4_line:
                    if mat.id in sem.keys():
                        sem4 = sem[mat.id]['qty']
                        unite = sem[mat.id]['unite']
                for sem in semaine5_line:
                    if mat.id in sem.keys():
                        sem5 = sem[mat.id]['qty']
                        unite = sem[mat.id]['unite']
                
                total = sem1 + sem2 + sem3 + sem4 + sem5
                val = {
                    'name' : name + ' (en '+  um_ach + ')',
                    'unite_achat' : um_ach,
                    'sem1' : sem1,
                    'sem2' : sem2,
                    'sem3' : sem3,
                    'sem4' : sem4,
                    'sem5' : sem5,
                    'total' : total,
                    'unite' : unite,
                }

                lines_obj.append(val)


            
            date =""
            for ob in plan_obj :
                date = datetime.datetime.strftime(ob.production_date, "%d %B %Y") + ' au '+ datetime.datetime.strftime(ob.production_date_fin, "%d %B %Y")
                exo = datetime.datetime.strftime(ob.production_date, "%B %Y")
        

            sheet = workbook.add_worksheet("Analyse couts matieres premieres")
            # set the orientation to landscape
            sheet.set_landscape()
            # set up the margin in inch
            sheet.set_margins(0.5,0.5,0.5,0.5)
            sheet.hide_gridlines(2)
            # set up the column width
            sheet.set_column('A:A', 12)
            sheet.set_column('B:B', 25)
            sheet.set_column('C:H', 12)
            sheet.set_column('I:I', 14)
            sheet.set_row(5, 27)
            sheet.set_row(10, 20)
            sheet.set_row(11, 20)
            sheet.merge_range(0,6,0,8, 'Exercice %s'%(exo), title_style)
            sheet.merge_range(1,6,1,8, 'SERVICE TECHNIQUE', title_style)
            sheet.merge_range(2,6,3,8, 'DÉPARTEMENT PRODUCTION', title_style)
            sheet.merge_range(5,2,5,8, 'PLANNING DE PRODUCTION', title_style21)
            sheet.merge_range(7,0,9,1, 'DÉSIGNATION', header_style)
            sheet.merge_range(7,2,7,7, 'Période du %s'%(date), header_style)
            sheet.merge_range(7,8,11,8, 'CONSOMMATION TOTALE DU MOIS', header_style)
            col = 2
            sheet.write(8,col, "Semaine1", header_style)
            sheet.write(8,col + 1, "semaine2", header_style)
            sheet.write(8,col + 2, "semaine3", header_style)
            sheet.write(8,col + 3, "semaine4", header_style)
            sheet.write(8,col + 4, "semaine5", header_style)
            sheet.write(8,col + 5, "Qte Camion", header_style)

            sheet.write(9,col, semaine1_objectif['period'], header_style)
            sheet.write(9,col + 1, semaine2_objectif['period'] , header_style)
            sheet.write(9,col + 2, semaine3_objectif['period'] , header_style)
            sheet.write(9,col + 3, semaine4_objectif['period'] , header_style)
            sheet.write(9,col + 4, semaine5_objectif['period'] , header_style)
            sheet.write(9,col + 5, "", header_style)

            sheet.write(10,col, semaine1_objectif['produit'], header_style)
            sheet.write(10,col + 1, semaine2_objectif['produit'], header_style)
            sheet.write(10,col + 2, semaine3_objectif['produit'], header_style)
            sheet.write(10,col + 3, semaine4_objectif['produit'], header_style)
            sheet.write(10,col + 4, semaine5_objectif['produit'], header_style)
            sheet.write(10,col + 5, "", header_style)

            sheet.write(11,col, semaine1_objectif['objectif'], header_style)
            sheet.write(11,col + 1, semaine2_objectif['objectif'], header_style)
            sheet.write(11,col + 2, semaine3_objectif['objectif'], header_style)
            sheet.write(11,col + 3, semaine4_objectif['objectif'], header_style)
            sheet.write(11,col + 4, semaine5_objectif['objectif'], header_style)
            sheet.write(11,col + 5, "", header_style)


            sheet.write('A11', 'Unité de mesure', header_style)
            sheet.write('B11', 'Produits fabriqués', header_style)
            sheet.merge_range(11,0,11,1, 'OBJECTIF DE LA SEMAINE', header_style)

            col = 0
            row = 12

            for obj in lines_obj:
                sheet.write(row,col, obj['unite'], text_style1)
                sheet.write(row,col + 1, obj['name']  , text_style1)
                sheet.write(row,col + 2, obj['sem1']  , number_style)
                sheet.write(row,col + 3, obj['sem2']  , number_style)
                sheet.write(row,col + 4, obj['sem3']  , number_style)
                sheet.write(row,col + 5, obj['sem4']  , number_style)
                sheet.write(row,col + 6, obj['sem5']  , number_style)
                sheet.write(row,col + 7, ''  , number_style)
                sheet.write(row,col + 8, obj['total']  , text_style1)
                row += 1
            sheet.set_row(row, 20)
            sheet.write(row,col, 'ETP (EFFECTIF TEMP PLEIN)', text_style1)
            sheet.write(row,col + 1, "main d'oeuvre requise" , text_style1)
            sheet.write(row,col + 2, semaine1_objectif['mainreq']  , number_style)
            sheet.write(row,col + 3, semaine2_objectif['mainreq'] , number_style)
            sheet.write(row,col + 4, semaine3_objectif['mainreq']  , number_style)
            sheet.write(row,col + 5, semaine4_objectif['mainreq']  , number_style)
            sheet.write(row,col + 6, semaine5_objectif['mainreq']  , number_style)
            sheet.write(row,col + 7, ''  , number_style)
            sheet.write(row,col + 8, ''  , text_style1)
            row += 1

            sheet.set_row(row, 20)
            sheet.write(row,col, 'ETP (EFFECTIF TEMP PLEIN)', text_style1)
            sheet.write(row,col + 1, "main d'oeuvre temporaire requise" , text_style1)
            sheet.write(row,col + 2, semaine1_objectif['maintemp']  , number_style)
            sheet.write(row,col + 3, semaine2_objectif['maintemp'] , number_style)
            sheet.write(row,col + 4, semaine3_objectif['maintemp']  , number_style)
            sheet.write(row,col + 5, semaine4_objectif['maintemp']  , number_style)
            sheet.write(row,col + 6, semaine5_objectif['maintemp']  , number_style)
            sheet.write(row,col + 7, ''  , number_style)
            sheet.write(row,col + 8, ''  , text_style1)
            row += 1

            qte_totale = 0
            for line in lines_obj:
                qte_totale +=line['total']

            sheet.set_row(row, 20)
            sheet.merge_range(row,0,row,1, 'Observations', text_style1)
            sheet.write(row,col + 1, "main d'oeuvre temporaire requise" , text_style1)
            sheet.write(row,col + 2, ''  , number_style)
            sheet.write(row,col + 3, '' , number_style)
            sheet.write(row,col + 4, ''  , number_style)
            sheet.write(row,col + 5, ''  , number_style)
            sheet.write(row,col + 6, ''  , number_style)
            sheet.write(row,col + 7, '' , number_style)
            sheet.write(row,col + 8, qte_totale  , text_style1)
            row += 2
            sheet.write(row,col + 7, 'La production',title_style)
         


        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

        return response
            
