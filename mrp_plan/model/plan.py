from math import prod
from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import ValidationError
import calendar


class StockMovePlan(models.Model):
    _name = "stock.move.plan"
    _description = "Stock Move Plan"
    _order = 'sequence, id'


    name = fields.Char('Description', required=True)
    sequence = fields.Integer('Sequence', default=10)
    # priority = fields.Selection(
    #     PROCUREMENT_PRIORITIES, 'Priority', default='0',
    #     compute="_compute_priority", store=True)
    date = fields.Datetime(
        'Date Scheduled', default=fields.Datetime.now, index=True, required=True,
        help="Scheduled date until move is done, then date of actual move processing")
    date_deadline = fields.Datetime(
        "Deadline", readonly=True,
        help="Date Promise to the customer on the top level document (SO/PO)")
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company,
        index=True, required=True)
    product_id = fields.Many2one(
        'product.product', 'Matiere Premiere',
        check_company=True,
        domain="[('type', 'in', ['product', 'consu'])]", index=True, required=True)
    description_picking = fields.Text('Description of Picking')
    product_qty = fields.Float(
        'Real Quantity', compute='_compute_product_qty', inverse='_set_product_qty',
        digits=0, store=True, compute_sudo=True,
        help='Quantity in the default UoM of the product')
    product_uom_qty = fields.Float(
        'Demand',
        digits='Product Unit of Measure',
        default=1.0,
        help="This is the quantity of products from an inventory "
             "point of view. For moves in the state 'done', this is the "
             "quantity of products that were actually moved. For other "
             "moves, this is the quantity of product that is planned to "
             "be moved. Lowering this quantity does not generate a "
             "backorder. Changing this quantity on assigned moves affects "
             "the product reservation, and should be done with care.")
    product_uom = fields.Many2one('uom.uom', "UoM")

    raw_material_production_plan_id = fields.Many2one('mrp.plan', 'Production Order for components', check_company=True, index=True)
    raw_material_production_plan_line_id = fields.Many2one('mrp.plan.line', 'Production Order for components', check_company=True, index=True)
    bom_line_id = fields.Many2one('mrp.bom.line', 'BoM Line', check_company=True)

    # TDE FIXME: make it stored, otherwise group will not work

    @api.model
    def create(self,vals):
        vals['name'] = 'New'
        return super(StockMovePlan,self).create(vals)

    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_product_qty(self):
        for move in self:
            move.product_qty = move.product_uom._compute_quantity(
                move.product_uom_qty, move.product_id.uom_id, rounding_method='HALF-UP')

    @api.depends('bom_line_id')
    def _compute_description_bom_line(self):
        bom_line_description = {}
        for bom in self.bom_line_id.bom_id:
            if bom.type != 'phantom':
                continue
            line_ids = bom.bom_line_ids.ids
            total = len(line_ids)
            name = bom.display_name
            for i, line_id in enumerate(line_ids):
                bom_line_description[line_id] = '%s - %d/%d' % (name, i+1, total)

        for move in self:
            move.description_bom_line = bom_line_description.get(move.bom_line_id.id)

class Planning(models.Model):
    _name = 'mrp.plan'
    _description = 'MRP Planning'
    
    
    def change_color_on_kanban(self):
        for record in self:
            color = 0
            if record.state == 'draft':
                color = 4
            elif record.state == 'approve':
                color = 10
            elif record.state == 'cancel':
                color = 9
            record.color = color
            
    
    
    name = fields.Char('Name',readonly=True)
#     location_dest_id = fields.Many2one('stock.location','Destination Loaction')
    product_id = fields.Many2one('product.product','Product',domain="[('bom_ids','!=',False)]") 
    plan_date = fields.Datetime('Date de planification',default=datetime.today())
    production_date = fields.Datetime('Date Debut')
    production_date_fin = fields.Datetime('Date Fin')
    
    plan_qty = fields.Float('Quantite')
    uom_id = fields.Many2one('uom.uom','Product Uom')
    bom_id = fields.Many2one('mrp.bom','Bom',domain="[('product_tmpl_id','=',product_id)]")
    user_id = fields.Many2one('res.users','Responsable', default=lambda self: self.env.user,)
    state = fields.Selection([('draft','Draft'),('approve','Approve'),('cancel','Cancel')],copy=False,default="draft")
    production_id = fields.Many2one('mrp.production','Production',readonly=True)
    color = fields.Integer('Color Index', compute="change_color_on_kanban")
    progress = fields.Integer('Progression de la production',default=0,compute="onchange_widget")
    max_progress = fields.Integer(default=100)
    move_raw_ids = fields.One2many('stock.move', 'raw_material_production_id', 'Components',copy=False)
    move_raw_plan_ids = fields.One2many('stock.move.plan', 'raw_material_production_plan_id', 'Components',copy=False)
    line_plan_ids = fields.One2many('mrp.plan.line', 'production_plan_line_id', 'Planification hebdomadaire',copy=False)
    plan_raw_ids = fields.One2many('mrp.production', 'plan_production_id', 'Planning',copy=False)
    company_id = fields.Many2one(
        'res.company', 'Company', default=lambda self: self.env.company,
        index=True, required=True)
    type = fields.Selection([('mois','Mensuelle'),('heb','Hebdomadaire')],copy=False,default="heb")
    @api.depends('production_id')
    def onchange_widget(self):
        for rec in self:
            if rec.production_id:
                if rec.production_id.state == 'draft':
                    rec.progress = 0                
                elif rec.production_id.state == 'confirmed':
                    rec.progress = 25
                elif rec.production_id.state == 'planned':
                    rec.progress = 50
                elif rec.production_id.state == 'progress':
                    rec.progress = 75
                elif rec.production_id.state == 'done':
                    rec.progress = 100
                elif rec.production_id.state == 'cancel':
                    rec.progress = 0
            else:
                rec.progress = 0
    
    @api.model
    def create(self,vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('mrp.plan') or _('New')
        return super(Planning,self).create(vals)  
    
    @api.onchange('product_id')
    def onchange_bom(self):
        if self.product_id:
            print(self.product_id)
            product_id = self.env['product.template'].search([('name','=',self.product_id.name)],limit=1)
            print(product_id)
            bom = self.env['mrp.bom'].search([('product_tmpl_id','=',product_id.id)],limit=1)
            self.bom_id = bom
            self.uom_id = self.product_id.uom_id.id
            self.plan_qty = 1
    
    """ @api.onchange('product_id', 'picking_type_id', 'company_id')
    def _onchange_product_id(self):
    
        if not self.product_id:
            self.bom_id = False
        elif not self.bom_id or self.bom_id.product_tmpl_id != self.product_tmpl_id or (self.bom_id.product_id and self.bom_id.product_id != self.product_id):
            bom = self.env['mrp.bom']._bom_find(self.product_id, picking_type=self.picking_type_id, company_id=self.company_id.id, bom_type='normal')[self.product_id]
            if bom:
                self.bom_id = bom.id
                self.product_qty = self.bom_id.product_qty
                self.product_uom_id = self.bom_id.product_uom_id.id
            else:
                self.bom_id = False
                self.product_uom_id = self.product_id.uom_id.id """

                
    @api.onchange('production_date')
    def onchange_date(self):
        if self.production_date and self.plan_date:
            if self.production_date < self.plan_date:
                raise ValidationError('Production Date should be greater than Plan Date...!!')
    
    
    def action_production_forecast(self):
        self.ensure_one()
        action = self.product_id.action_product_forecast_report()
        action['context'] = {
            'active_id': self.product_id.id,
            'active_model': 'product.product',
            'move_to_match_ids': self.move_finished_ids.filtered(lambda m: m.product_id == self.product_id).ids
        }
        warehouse = self.picking_type_id.warehouse_id
        if warehouse:
            action['context']['warehouse'] = warehouse.id
        return action

#     def confirm(self):
#         if self.state:
#             self.ensure_one()
#             template = self.env['ir.model.data'].get_object('mrp_plan', 'email_template_mrp_plan')
#             self.env['mail.template'].browse(template.id).send_mail(self.id,force_send=True)
#             self.state = 'confirm'
        
    def cancel(self):
        if self.state:
            self.state = 'cancel'
    
    def get_plan_lines(self, article):
        lines = []
        sum =0
        print('Articles concernes',article.product_id.name)
        for line in self.plan_raw_ids:
            prod=self.env["mrp.plan.line"].search(
                [
                    ("product_id", "=", article.product_id.id),
                    ("production_order_id", "=", line.id),
                ]
                
            )
            print('PLAN concernes',prod)
           
            if not prod:
                vals = {
                    
                    'qty': 0,
                    'mrp': line.id,
                    'sum': sum
                    
                }
                lines.append(vals)
            else:
                sum =0
                vals = {
                    
                    'qty': prod.product_uom_qty,
                    'mrp': line.id,
                    'sum': prod.product_uom_qty + sum
                }
                lines.append(vals)
                sum = prod.product_uom_qty + sum   
        print('Etape de marche',lines)       
        return lines

    def approve(self):
     
        components = {} 
        id_component = []  
        for line in self.plan_raw_ids:
        
            if line.move_raw_ids:
                for prod in line.move_raw_ids:
            
                    if prod.product_id.id not in id_component:
                        id_component.append(prod.product_id)
                    
                    plan_prod = {
                            'production_plan_line_id':self.id,
                            'production_order_id':line.id,
                            'product_id':prod.product_id.id,
                            'product_uom_qty':prod.product_uom_qty,
                            'product_uom_id':prod.product_uom.id,
                                                   
                        }
                    move = self.env['mrp.plan.line'].create(plan_prod)
                        
        for comp in id_component:
            components = {
                    'product_id':comp.id,
                    'raw_material_production_plan_id':self.id,
                    'product_uom':comp.uom_id.id,
                    
                }
            move = self.env['stock.move.plan'].create(components)
            print ('essai',move)
               
        self.state = 'approve'
            
            
    def manufacture_order(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'res_id': self.production_id.id,
            'view_type': 'form',
            'view_mode': 'form',
#             'context': self.env.context,
            'target': 'current',
        }
        
     
class Production(models.Model):
    _inherit = 'mrp.production'

    """ @api.model
    def _get_default_jour(self):
        if self.env.context.get('default_date_planned_start'):
            born = datetime.datetime.strptime(self.env.context.get('default_date_planned_start'), '%d %m %Y').weekday() 
            return (calendar.day_name[born]) 
            
        return True """

    planned_date = fields.Char('Planned Date')
    project1_id = fields.Many2one('project.project','Unite de production')
    tache_raw_ids = fields.One2many('project.task', 'production_id', 'Tache')
    planned_id = fields.Many2one('mrp.plan','Production Plan')
    main_oeuvre_requise = fields.Float('Main oeuvre requise')
    main_oeuvre_temporaire = fields.Float('Main oeuvre Temporaire')
    plan_production_id = fields.Many2one('mrp.plan','Production Plan')
    plan_request_id = fields.Many2one('stock.request','Requete de stock')
    jour = fields.Char('Jour') 
    request_id = fields.Many2one(string='Ordre de production',comodel_name='stock.request',ondelete='restrict',)


    def duplicate_line(self, default=None):
        default = default or {}
        return super(Production, self).copy(default)
    
    
    
    @api.onchange('qty_producing')
    def _onchange_qty_producing(self):
        
        if self.request_id:
            
            request = self.env['stock.request'].search([('id', '=', self.request_id.id)])
            id_req = None
            for req in request:
                id_req = req.id
            productions1 = self.env['mrp.production'].search([('request_id', '=', id_req),('state', 'in',['progress','to_close'])])
            productions2 = self.env['mrp.production'].search([('request_id', '=', id_req),('state', 'in',['done'])])
            qty_done = 0
            qty_in_progress = 0
            ids = []
            
            rebut = 0
            
            if productions1:
                for pro in productions1:
                    ids.append(pro.id)
                    qty_in_progress += pro.qty_producing
            
            if productions2:
                for pro in productions2:
                    ids.append(pro.id)
                    qty_done += pro.qty_producing
            
            rebuts = self.env['mrp.unbuild'].search([('state', 'in', ['done']),('mo_id', 'in', ids)])
            rebuts1 = self.env['stock.scrap'].search([('state', 'in', ['done']),('production_id', 'in', ids)])
            for reb in rebuts :
                rebut += reb.product_qty
            for reb in rebuts1 :
                rebut += reb.scrap_qty
            if request:
                for req in request:
                    if req.product_id == self.product_id :
                        req.write({
                            'qty_in_progress' : qty_in_progress,
                            'qty_done' : qty_done,
                            'qty_cancelled': rebut,
                        })
                
    
    @api.onchange('state')
    def _onchange_state(self):
        
        if self.request_id:
            print("Bonjour le monde 1111111111")
            
            request = self.env['stock.request'].search([('id', '=', self.request_id.id)])
            id_req = None
            for req in request:
                id_req = req.id
            productions1 = self.env['mrp.production'].search([('request_id', '=', id_req),('state', 'in',['progress','to_close'])])
            productions2 = self.env['mrp.production'].search([('request_id', '=', id_req),('state', 'in',['done'])])
            qty_done = 0
            qty_in_progress = 0
            ids = []
            
            rebut = 0
            
            if productions1:
                for pro in productions1:
                    ids.append(pro.id)
                    qty_in_progress += pro.qty_producing
            
            if productions2:
                for pro in productions2:
                    ids.append(pro.id)
                    qty_done += pro.qty_producing
            
            rebuts = self.env['mrp.unbuild'].search([('state', 'in', ['done']),('mo_id', 'in', ids)])
            rebuts1 = self.env['stock.scrap'].search([('state', 'in', ['done']),('production_id', 'in', ids)])
            for reb in rebuts :
                rebut += reb.product_qty
            for reb in rebuts1 :
                rebut += reb.scrap_qty
            if request:
                for req in request:
                    if req.product_id == self.product_id :
                        req.write({
                            'qty_in_progress' : qty_in_progress,
                            'qty_done' : qty_done,
                            'qty_cancelled': rebut,
                        })
                
    
     
        
    @api.onchange('project1_id')
    def _onchange_project(self):
        if self.project1_id:
           
            task_line = self.env['project.task'].search([('project_id', '=', self.project1_id.id)])
            self.tache_raw_ids = task_line
        if not self.project1_id :
            self.tache_raw_ids = False
    @api.onchange('date_planned_start')
    def _onchange_date_planned_start(self):
        if self.date_planned_start:
            date = self.date_planned_start.date()
            """ print (date)
            day, month, year = (int(i) for i in date.split(' '))     
            born = datetime.date(year, month, day)  """
            date1 = date.strftime("%d %m %Y")
            self.jour = calendar.day_name[datetime.strptime(date1, '%d %m %Y').weekday()]
            
            #self.jour = calendar.day_name[datetime.strptime(date, '%d %m %Y').weekday()]
            

class ProjectTask(models.Model):
    _inherit = "project.task"

    production_id = fields.Many2one(comodel_name='mrp.production', string="Production")    
    #employee_id = fields.Many2one('hr.employee', string="Ressource")
    employee_id = fields.Many2many('hr.employee', 'task_id_employ_id_rel','task_id','employ_id',
        string='Ressource') 

class ProjectProject(models.Model):
    _inherit = "project.project"

    type_interne = fields.Selection([('technique','Technique'),('prod','Production'),('crm','Activites commerciales')],copy=False,default="technique")
    
    
    
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    
    
    prod_capacity = fields.Integer(string='Capacité de production', help="Capacité de production par jour")
    

    