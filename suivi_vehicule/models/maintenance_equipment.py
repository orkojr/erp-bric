# -*- coding: utf-8 -*-
from email.policy import default
import time
from datetime import datetime, timedelta
import datetime
from odoo import fields, models, api, _
from odoo import exceptions
from odoo.exceptions import UserError, ValidationError



class ProductProduct(models.Model):
    _inherit = 'product.template'

    duree = fields.Integer(string='Durée de vie',)
    
    


class MaintenanceEquipmentPieceLine(models.Model):
    _name = 'maintenance.piece.line'
    _description = "Piece Equipement"
    

    
    


    piece_id = fields.Many2one(string='Pièce',comodel_name='product.product',ondelete='restrict',required=True,)
    mise_en_marche = fields.Datetime(string='Date de mise en marche',required=True,)
    progress = fields.Integer(string='Utilisation(%)', compute='_compute_progress',store=True)
    equipment_id = fields.Many2one(string='Equipement',comodel_name='maintenance.equipment',ondelete='restrict',)
    request_id = fields.Many2one(string='Maintenace Request', comodel_name='maintenance.request', ondelete='restrict')
    
    
    
    
    @api.depends('piece_id')
    def _compute_progress(self):
        today = datetime.date.today()
        for record in self:
            prog = 0
            duree = 0
            mrp = self.env['mrp.production'].search([('date_planned_start', '>=',record.mise_en_marche),('date_planned_start', '<=', today)])
            if len(mrp) > 0:
                print("Nous y somme Mr Orko")
                for mr in mrp:
                    if mr.equipment_id.id == record.equipment_id.id:
                        prog += mr.duree_production
            if record.piece_id.duree > 0:
                print("Nous y somme Mr Orko Yessess,", prog)
                
                duree = (prog/record.piece_id.duree)*100
            record.progress = duree
                            


    @api.depends('mise_en_marche')
    def _compute_progress(self):
        today = datetime.date.today()
        for record in self:
            prog = 0
            duree = 0
            mrp = self.env['mrp.production'].search([('date_planned_start', '>=',record.mise_en_marche),('date_planned_start', '<=', today)])
            if len(mrp) > 0:
                print("Nous y somme Mr Orko")
                for mr in mrp:
                    if mr.equipment_id.id == record.equipment_id.id:
                        prog += mr.duree_production
            if record.piece_id.duree > 0:
                print("Nous y somme Mr Orko Yessess,", prog)
                
                duree = (prog/record.piece_id.duree)*100
            record.progress = duree
    
    
    @api.model                   
    def utilisation(self):
        
        today = datetime.date.today()
        
        maint = self.env['maintenance.piece.line'].search([])
        if len(maint) :
            for rec in maint:
                prog = 0
                duree = 0
                mrp = self.env['mrp.production'].search([('date_planned_start', '>=',rec.mise_en_marche),('date_planned_start', '<=', today)])
                if len(mrp) > 0:
                    for mr in mrp:
                        if mr.equipment_id.id == rec.equipment_id.id:
                            prog += mr.duree_production
                if rec.piece_id.duree > 0:
                    print("Nous y somme Mr Orko Yessess,", prog)
            
                duree = (prog/rec.piece_id.duree)*100
                rec.progress = duree
       

class MaintenaceEquipment(models.Model):
    _inherit='maintenance.equipment'
    
    
    piece_ids = fields.One2many(string='Pieces',comodel_name='maintenance.piece.line',inverse_name='equipment_id',)
    secteur = fields.Selection(string='Secteur',selection=[('briqueterie', 'Briqueterie'), ('tuilerie', 'Tuilerie'),('parc_info', 'Parc informatique'), ('autres', 'Autres')],default='briqueterie')
    
    def _prepare_maintenance_request_vals(self, date):
        self.ensure_one()
        return {
            'name': _('Preventive Maintenance - %s', self.name),
            'request_date': date,
            'schedule_date': date,
            'category_id': self.category_id.id,
            'equipment_id': self.id,
            'maintenance_type': 'preventive',
            'owner_user_id': self.owner_user_id.id,
            'user_id': self.technician_user_id.id,
            'maintenance_team_id': self.maintenance_team_id.id,
            'duration': self.maintenance_duration,
            'company_id': self.company_id.id or self.env.company.id,
            'chekpoint_ids': self.checkpoint_ids,
            'piece_ids' : self.piece_ids,
        }



    @api.model
    def create_activity(self):
        equipments = self.env['maintenance.equipment'].search([])
        
        users = self.env.ref('maintenance.group_equipment_manager').users
        for eq in equipments:
            length = len(eq.piece_ids)

            if length > 0 :
                today = datetime.date.today()
                for line in eq.piece_ids:
                    if line.progress >=80:
                        for user in users:
                            data = {
                            'res_id': eq.id,
                            'res_model_id': self.env['ir.model'].search([('model', '=', 'maintenance.equipment')]).id,
                            'user_id': user.id,
                            'summary': 'CHanger la piece',
                            'note' :f"Pensez a changer la piece  {line.piece_id.product_tmpl_id.name}",
                            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                            'date_deadline': today
                            }
                            self.env['mail.activity'].create(data)


class MaintenaceRequest(models.Model):
    _inherit='maintenance.request'
    
    
    piece_ids = fields.One2many(string='Pieces',comodel_name='maintenance.piece.line',inverse_name='request_id',)
    
    
    
class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    equipment_id = fields.Many2one(string='Equipement',comodel_name='maintenance.equipment',ondelete='restrict',)
    duree_production = fields.Float(string='Durée Production',)
    
    
    
    
    
    #     compute='_compute_equipment_id' )
    
    # @api.depends('depends')
    # def _compute_equipment_id(self):
    #     for record in self:
    #         record.equipment_id = something
    
    
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id.categ_id.name in ['Briquetterie',  'Tuilerie']:
            eq = self.env['maintenance.equipment'].search([('secteur', 'in', ['briqueterie', 'tuilerie'])])
            if len(eq) > 0:
                for e in eq:
                    if e.secteur == 'briqueterie' and self.product_id.categ_id.name == 'Briquetterie':
                        self.equipment_id = e.id
                    elif e.secteur == 'tuilerie' and self.product_id.categ_id.name == 'Tuilerie':
                        self.equipment_id = e.id
                    else :
                        self.equipment_id = None
    
    
    