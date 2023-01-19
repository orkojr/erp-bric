# -*- coding: utf-8 -*-
import time
from datetime import date, datetime
import pytz
import json
import datetime
import io
from odoo import api, fields, models, _
from odoo.tools import date_utils
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class StockReport(models.TransientModel):
    _name = "report.stock.history"
    _description = "Current Stock History"

    warehouse = fields.Many2many('stock.warehouse', 'wh_wiz_rel1', 'wh', 'wiz', string='Warehouse', required=True)
    category = fields.Many2many('product.category', 'categ_wiz_rel1', 'categ', 'wiz', string='Warehouse', domain="[('name', 'in', ['Produits finis','Briquetterie','Tuilerie','Prefa'])]")
    date_between = fields.Datetime(
        string='Date de debut',
        default=fields.Datetime.now
    )
    
    date_end = fields.Datetime(
        string='Date de fin',
        default=fields.Datetime.now,
    )

    
    select_period = fields.Selection(
        string='Periode Rapport',
        selection=[('current', 'Date courant'), ('periode', 'Pour une periode')],
        default='current'
    )
    
     

    def export_xls(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'warehouse': self.warehouse.ids,
            'category': self.category.ids,
            'date_deb': self.date_between.strftime("%m/%d/%Y %H:%M:%S"),
            'date_fin': self.date_end.strftime("%m/%d/%Y %H:%M:%S"),
            'select_periode':self.select_period,

        }
        
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'report.stock.history',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'ETAT DE STOCK DES PRODUITS FINIS',
                     },
            'report_type': 'stock_xlsx'
        }
        

    def get_date(self, data):
        return {
            'date_deb':data.date_deb,
            'date_fin':data.date_fin
        }

    def get_warehouse(self, data):
        wh = data.warehouse.mapped('id')
        obj = self.env['stock.warehouse'].search([('id', 'in', wh)])
        l1 = []
        l2 = []
        for j in obj:
            l1.append(j.name)
            l2.append(j.id)
        return l1, l2

    def get_lines(self, data, warehouse, deb, fin, select_period):
        lines = []
        categ_id = data.mapped('id')
        if categ_id:
            categ_products = self.env['product.product'].search([('categ_id', 'in', categ_id), ('product_tmpl_id.detailed_type', '=', 'product')])

        else:
            categ_products = self.env['product.product'].search([('product_tmpl_id.detailed_type', '=', 'product'),('categ_id.name', 'in', ['Produits finis','Tuilerie','Briquetterie','Prefa'])])
        product_ids = tuple([pro_id.id for pro_id in categ_products])
        sale_query = """
               SELECT sum(s_o_l.product_uom_qty) AS product_uom_qty, s_o_l.product_id FROM sale_order_line AS s_o_l
               JOIN sale_order AS s_o ON s_o_l.order_id = s_o.id
               WHERE s_o.state IN ('sale','done')
               AND s_o.warehouse_id = %s
               AND s_o_l.product_id in %s group by s_o_l.product_id"""
        purchase_query = """
               SELECT sum(p_o_l.product_qty) AS product_qty, p_o_l.product_id FROM purchase_order_line AS p_o_l
               JOIN purchase_order AS p_o ON p_o_l.order_id = p_o.id
               INNER JOIN stock_picking_type AS s_p_t ON p_o.picking_type_id = s_p_t.id
               WHERE p_o.state IN ('purchase','done')
               AND s_p_t.warehouse_id = %s AND p_o_l.product_id in %s group by p_o_l.product_id"""

               
        if select_period=='periode': 
            produite_jr = """SELECT m.product_id, sum(m.product_qty) AS qte_prod FROM  mrp_production AS m
                JOIN stock_warehouse AS wh ON wh.lot_stock_id = m.location_dest_id 
                WHERE m.create_date BETWEEN %s AND %s AND wh.id=%s AND state='done' group by m.product_id"""
            paramprod = deb,fin,warehouse
            

            livree = """select sml.product_id,  sum(sml.qty_done) as livree from stock_move_line sml 
                left join stock_picking sp on sp.id=sml.picking_id 
                left join stock_warehouse wh on wh.lot_stock_id=sml.location_id 
                where sp.state='done' and sp.date BETWEEN %s and %s and wh.id=%s 
                group by sml.product_id"""
            parampliv = deb,fin,warehouse

            casse_livraison = """SELECT DISTINCT s.product_id,  sum(s.casse_livr) AS casse
                FROM stock_move as s 
                JOIN stock_warehouse as wh on wh.lot_stock_id=s.location_id
                WHERE s.is_done = true  and s.date BETWEEN %s and %s  and wh.id =%s
                group by ( s.product_id)"""

            
            casse_prod = """SELECT sc.product_id, sum(sc.scrap_qty) AS scrap_qty FROM stock_scrap AS sc 
                JOIN mrp_production as p ON sc.product_id = p.product_id 
                INNER JOIN stock_warehouse AS wh ON wh.lot_stock_id = p.location_dest_id 
                WHERE sc.state IN ('done', 'Done') AND p.state ='done' 
                AND date_done BETWEEN %s AND %s AND wh.id=%s GROUP BY sc.product_id"""
            # params1 = deb,fin

        else:

            produite_jr = """SELECT m.product_id, sum(m.product_qty) AS qte_prod FROM  mrp_production AS m
                JOIN stock_warehouse AS wh ON wh.lot_stock_id = m.location_dest_id 
                WHERE DATE(m.create_date)=CURRENT_DATE AND wh.id=%s AND state='done' group by m.product_id"""%(warehouse)
            paramprod = (0, 0)
            parampliv = (0, 0)

            casse_prod = """SELECT sc.product_id, sum(sc.scrap_qty) AS scrap_qty FROM stock_scrap AS sc 
                JOIN mrp_production as p ON sc.product_id = p.product_id 
                INNER JOIN stock_warehouse AS wh ON wh.lot_stock_id = p.location_dest_id
                WHERE sc.state IN ('done', 'Done') AND p.state ='done' 
                AND DATE(date_done)=CURRENT_DATE AND wh.id=%s GROUP BY sc.product_id"""%(warehouse)
        

            livree = """select sml.product_id,  sum(sml.qty_done) as livree 
                from stock_move_line sml 
                left join stock_picking sp on sp.id=sml.picking_id 
                left join stock_warehouse wh on wh.lot_stock_id=sml.location_id 
                where sp.state='done' and DATE(sp.date)=CURRENT_DATE and wh.id=%s  
                group by sml.product_id"""%(warehouse)
            

            casse_livraison = """SELECT DISTINCT s.product_id,  sum(s.casse_livr) AS casse
                FROM stock_move as s 
                JOIN stock_warehouse as wh on wh.lot_stock_id=s.location_id
                WHERE s.is_done = true and wh.id =%s and DATE(s.date)=CURRENT_DATE  
                group by ( s.product_id)"""%(warehouse)
        


        params = warehouse, product_ids if product_ids else (0, 0)


        livre_obj=[]
        #quantite livre entre deux dates
        casse_obj = []
        prod_obj =[]

        if select_period=='periode':
            self._cr.execute(livree, parampliv)
            livre_obj = self._cr.dictfetchall()

            self._cr.execute(casse_livraison, parampliv)
            casse_obj = self._cr.dictfetchall()

            #quantite produite entre deux dates
            self._cr.execute(produite_jr, paramprod)
            prod_obj = self._cr.dictfetchall()
        else:
            self._cr.execute(livree)
            livre_obj = self._cr.dictfetchall()

            self._cr.execute(casse_livraison)
            casse_obj = self._cr.dictfetchall()

            # quantite produite entre deux dates
            self._cr.execute(produite_jr)
            prod_obj = self._cr.dictfetchall()
        

        liv_list_obj = []
        liv_casse_list_obj = []
        list_prod_obj=[]



        # permet d'initialiser la quantite livree a zero
        for obj in categ_products:
            liv_list_obj.append({'product_id':obj.id, 'livree': 0})
            liv_casse_list_obj.append({'product_id': obj.id, 'casse': 0})
        
        #permet de recuperer les quantites livrees
        for obj in liv_list_obj:
            for liv in livre_obj:
                if liv['product_id'] == obj['product_id']:
                    obj['livree'] = liv['livree']

        #permet de recuperer les casses de livraison
        for obj in liv_casse_list_obj:
            for casse in casse_obj:
                if casse['product_id'] == obj['product_id']:
                    obj['casse'] = casse['casse']
        
        # #casse de production entre deux dates 
        self._cr.execute(casse_prod, paramprod)
        prod_casse_obj = self._cr.dictfetchall()

        self._cr.execute(sale_query, params)
        sol_query_obj = self._cr.dictfetchall()

        self._cr.execute(purchase_query, params)
        pol_query_obj = self._cr.dictfetchall()

        
        for obj in categ_products:
            sale_value = 0
            livre_val = 0
            casse_liv_val = 0
            prod_val = 0
            prod_casse_val = 0
            purchase_value = 0
            for sol_product in sol_query_obj:
                if sol_product['product_id'] == obj.id:
                    sale_value = sol_product['product_uom_qty']

            for liv_prod in liv_list_obj:
                if liv_prod['product_id'] == obj.id :
                    livre_val = liv_prod['livree']

            for liv_prod in liv_casse_list_obj:
                if liv_prod['product_id'] == obj.id :
                    casse_liv_val = liv_prod['casse'] if liv_prod['casse'] else 0

            for pro_prod in prod_obj:
                if pro_prod['product_id'] == obj.id:
                    prod_val = pro_prod['qte_prod']

            for pol_product in pol_query_obj:
                if pol_product['product_id'] == obj.id:
                    purchase_value = pol_product['product_qty']

            for prod_casse in prod_casse_obj:
                if prod_casse['product_id'] == obj.id:
                    prod_casse_val = prod_casse['scrap_qty']
            
            date_stock = deb.strftime('%Y-%m-%d %H:%M:%S')
            #converti la une chaine en une date (datetime)
            cust_date =datetime.datetime.strptime(date_stock, '%Y-%m-%d %H:%M:%S')
            #modifie l'heure d'une datetime
            date_stock = datetime.datetime(cust_date.year, cust_date.month, cust_date.day, 0, 0, 0)
            cust_date = date_stock.strftime('%Y-%m-%d %H:%M:%S')
            

            virtual_available = obj.with_context({'warehouse': warehouse ,'to_date': cust_date}).virtual_available
            outgoing_qty = obj.with_context({'warehouse': warehouse ,'to_date': cust_date}).outgoing_qty
            incoming_qty = obj.with_context({'warehouse': warehouse ,'to_date': cust_date}).incoming_qty
            available_qty = virtual_available + outgoing_qty - incoming_qty
            value = available_qty * obj.standard_price
            stocktheorik = available_qty+prod_val - prod_casse_val
            stock_final_reel = stocktheorik - livre_val - casse_liv_val
            vals = {
                'sku': obj.default_code,
                'name': obj.name,
                'category': obj.categ_id.name,
                'cost_price': obj.standard_price,
                'available': available_qty,
                'virtual': virtual_available,
                'incoming': incoming_qty,
                'outgoing': outgoing_qty,
                'net_on_hand': obj.with_context({'warehouse': warehouse,'to_date': date_stock}).qty_available,
                'total_value': value,
                'sale_value': sale_value,
                'purchase_value': purchase_value,
                'qte_prod': prod_val,
                'qte_livre': livre_val,
                'casse_prod': prod_casse_val,
                'stock_theorik': stocktheorik,
                'casse_livr': casse_liv_val,
                'stock_reel' : stock_final_reel,
            }
            lines.append(vals)
        return lines

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        lines = self.browse(data['ids'])
        d = lines.category
        get_warehouse = self.get_warehouse(lines)
        count = len(get_warehouse[0]) *  19
        comp = self.env.user.company_id.name
        sheet = workbook.add_worksheet('Stock Info')
        format0 = workbook.add_format({'font_size': 20, 'align': 'center', 'bold': True, 'font_name': 'Times', 'bold': True, 'left': 1, 'right': 1, 'bottom': 1, 'top': 1})
        format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True, 'font_name': 'Times', 'left': 1, 'right': 1, 'bottom': 1, 'top': 1})
        format111 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True, 'font_name': 'Times',})
        format11 = workbook.add_format({'font_size': 12, 'align': 'center', 'bold': True, 'font_name': 'Times', })
        format12 = workbook.add_format({'font_size': 14, 'align': 'center', 'bold': True, 'font_name': 'Times', })
        format21 = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True, 'font_name': 'Times', 'bold': True, 'left': 1, 'right': 1, 'bottom': 1, 'top': 1})
        format3 = workbook.add_format({'bottom': True, 'top': True, 'font_size': 13, 'font_name': 'Times', 'bold': True, 'left': 1, 'right': 1, 'bottom': 1, 'top': 1})
        format4 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold': True, 'font_name': 'Times', 'bold': True, 'left': 1, 'right': 1, 'bottom': 1, 'top': 1})
        format41 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold': True, 'font_name': 'Times', 'bold': True, })
        font_size_8 = workbook.add_format({'font_size': 10, 'align': 'center', 'font_name': 'Times',  'left': 1, 'right': 1, 'bottom': 1, 'top': 1})
        font_size_8_l = workbook.add_format({'font_size': 10, 'align': 'left', 'font_name': 'Times',  'left': 1, 'right': 1, 'bottom': 1, 'top': 1})
        font_size_8_r = workbook.add_format({'font_size': 10, 'align': 'right', 'font_name': 'Times', 'font_name': 'Times', 'bold': True, 'left': 1, 'right': 1, 'bottom': 1, 'top': 1})
        red_mark = workbook.add_format({'font_size': 8, 'bg_color': 'red', 'font_name': 'Times', 'bold': True, 'left': 1, 'right': 1, 'bottom': 1, 'top': 1})
        justify = workbook.add_format({'font_size': 12, 'font_name': 'Times', 'bold': True, 'left': 1, 'right': 1, 'bottom': 1, 'top': 1})
        sheet.set_margins(0.5, 0.5, 0.5, 0.5)
        format3.set_align('center')
        justify.set_align('justify')
        format1.set_align('center')
        red_mark.set_align('center')
        sheet.merge_range(1, 7, 2, 10, 'Product Stock Info', format0)
        sheet.merge_range(3, 7, 3, 10, comp, format1)
        w_house = ', '
        cat = ', '
        c = []
        d1 = d.mapped('id')
        if d1:
            for i in d1:
                c.append(self.env['product.category'].browse(i).name)
            cat = cat.join(c)
            sheet.merge_range(4, 0, 4, 1, 'Category(s) : ', format4)
            sheet.merge_range(4, 2, 4, 3 + len(d1), cat, format4)
        sheet.merge_range(5, 0, 5, 1, 'Warehouse(s) : ', format41)
        w_house = w_house.join(get_warehouse[0])
        sheet.merge_range(5, 2, 5, 3 + len(get_warehouse[0]), w_house, format41)
        user = self.env['res.users'].browse(self.env.uid)
        tz = pytz.timezone(user.tz if user.tz else 'UTC')
        times = pytz.utc.localize(datetime.datetime.now()).astimezone(tz)
        sheet.merge_range('A8:D8', 'Date rapport: ' + str(times.strftime("%Y-%m-%d %H:%M %p")), format111)
        sheet.merge_range(7, 4, 7, 21, 'Entrepots', format12)
        sheet.merge_range('A9:F9', 'Product Information', format11)
        w_col_no1 = 4
        prod_colh = 0
        w_col_col = 8
        for i in get_warehouse[0]:
            # sheet.merge_range(w_col_col, w_col_no1, w_col_col, 19, i, format11)
            for j in get_warehouse[1]:
                get_line = self.get_lines(d, j, lines.date_between,lines.date_end, lines.select_period)
                w_col_col =w_col_col + len(get_line) -len(get_warehouse[0])
            sheet.merge_range(9, prod_colh, 10, prod_colh + 1,'Code Produit', format21)
            sheet.merge_range(9, prod_colh + 2, 10, prod_colh + 3, 'Designation', format21)
            sheet.merge_range(9, prod_colh + 4, 10, prod_colh + 5, 'Categorie', format21)
            sheet.merge_range(9, prod_colh + 6, 10, prod_colh + 7, 'Stock initial', format21)
            sheet.merge_range(9, prod_colh +8, 10, prod_colh + 9, 'Production Brute', format21)
            sheet.merge_range(9, prod_colh + 10, 10, prod_colh + 11, 'Casses production', format21)
            sheet.merge_range(9, prod_colh + 12, 10, prod_colh + 13, 'Stock final theorique', format21)
            sheet.merge_range(9, prod_colh + 14, 10, prod_colh + 15, 'Quantite Livree', format21)
            sheet.merge_range(9, prod_colh + 16, 10, prod_colh + 17, 'Casses Livraison', format21)
            sheet.merge_range(9, prod_colh + 18, 10, prod_colh +19, 'Stock final Reel', format21)
            sheet.merge_range(9, prod_colh + 20, 10, prod_colh + 21, 'Observation', format21)
            prod_colh = prod_colh
       
        prod_row = 11
        prod_col = 0
        for i in get_warehouse[1]:
            get_line = self.get_lines(d, i, lines.date_between,lines.date_end, lines.select_period)
            for each in get_line:
                sheet.merge_range(prod_row, prod_col, prod_row, prod_col + 1,each['sku'], font_size_8_l)
                sheet.merge_range(prod_row, prod_col + 2, prod_row, prod_col + 3, each['name'], font_size_8_l)
                sheet.merge_range(prod_row, prod_col + 4, prod_row, prod_col + 5, each['category'], font_size_8_l)
                if each['available'] < 0:
                    sheet.merge_range(prod_row, prod_col + 6, prod_row, prod_col + 7, each['available'], red_mark)
                else:
                    sheet.merge_range(prod_row, prod_col + 6, prod_row, prod_col + 7, each['available'], font_size_8)
                if each['qte_prod'] < 0:
                    sheet.merge_range(prod_row, prod_col + 8, prod_row, prod_col + 9, each['qte_prod'], red_mark)
                else:
                    sheet.merge_range(prod_row, prod_col + 8, prod_row, prod_col + 9, each['qte_prod'], font_size_8)
                if each['casse_prod'] < 0:
                    sheet.merge_range(prod_row, prod_col + 10, prod_row, prod_col + 11, each['casse_prod'], red_mark)
                else:
                    sheet.merge_range(prod_row, prod_col + 10, prod_row, prod_col + 11, each['casse_prod'], font_size_8)
                if each['stock_theorik'] < 0:
                    sheet.merge_range(prod_row, prod_col + 12, prod_row, prod_col + 13, each['stock_theorik'], red_mark)
                else:
                    sheet.merge_range(prod_row, prod_col + 12, prod_row, prod_col + 13, each['stock_theorik'], font_size_8)
                if each['qte_livre'] < 0:
                    sheet.merge_range(prod_row, prod_col + 14, prod_row, prod_col + 15, each['qte_livre'], red_mark)
                else:
                    sheet.merge_range(prod_row, prod_col + 14, prod_row, prod_col + 15, each['qte_livre'], font_size_8)
                if each['casse_livr'] < 0:
                    sheet.merge_range(prod_row, prod_col + 16, prod_row, prod_col + 17, each['casse_livr'], red_mark)
                else:
                    sheet.merge_range(prod_row, prod_col + 16, prod_row, prod_col + 17, each['casse_livr'], font_size_8)
                if each['stock_reel'] < 0:
                    sheet.merge_range(prod_row, prod_col + 18, prod_row, prod_col + 19, each['stock_reel'], red_mark)
                else:
                    sheet.merge_range(prod_row, prod_col + 18, prod_row, prod_col + 19, each['stock_reel'], font_size_8)
                sheet.merge_range(prod_row, prod_col + 20, prod_row, prod_col + 21, '', font_size_8)
                prod_row = prod_row + 1
    
            prod_row = prod_row + len(get_warehouse[1]) 
            prod_col = prod_col
        
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
