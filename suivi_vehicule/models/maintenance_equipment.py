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
    en_marche = fields.Boolean(string='En Marche',default=True,)
    progress = fields.Integer(string='Utilisation(%)', compute='_compute_progress',store=True)
    equipment_id = fields.Many2one(string='Equipement',comodel_name='maintenance.equipment',ondelete='restrict',)
    request_id = fields.Many2one(string='Maintenace Request', comodel_name='maintenance.request', ondelete='restrict')
    
    
    
    
    @api.depends('piece_id','en_marche')
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
                            
    
    
    
class MaintenaceEquipment(models.Model):
    _inherit='maintenance.equipment'
    
    
    piece_ids = fields.One2many(string='Pieces',comodel_name='maintenance.piece.line',inverse_name='equipment_id',)
    secteur = fields.Selection(string='Secteur',selection=[('valor1', 'valor1'), ('valor2', 'valor2')])
    
    
    



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
        if self.product_id.categ_id.name in ['Briquetterie', 'Produits Finis', 'Tuilerie']:
            eq = self.env['maintenance.equipment'].search([('secteur', '=', 'unite_production')])
            if len(eq) > 0:
                for e in eq:
                    self.equipment_id = e.id
    
    
    
    @api.onchange('duree_production')
    def _onchange_duree_production(self):
        if self.equipment_id:
            eq = self.env['maintenance.equipment'].search([('id', '=', self.equipment_id.id)])
            if len(eq) >0:
                duree = 0
                mrp = self.env['mrp.production'].search([('equipment_id', '=', self.equipment_id.id)])
                if len(mrp) > 0 :
                    for mr in mrp:
                        duree += mrp.duree_production
                for e in eq:
                    for line in e.piece_ids:
                        utilisation = (duree / line.duree)*100
                        line.progress = utilisation
    
    
        
    
    
    
   
