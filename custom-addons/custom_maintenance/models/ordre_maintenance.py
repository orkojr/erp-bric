# -*- coding: utf-8 -*-

from email.policy import default
from odoo import api, fields, models


class MaintenanceComposant(models.Model):
    _inherit = "maintenance.request"
    _description = 'Ordre de Maintenance'
    
    
    line_request_ids = fields.One2many(string='Maintenance Request', comodel_name='maintenance.request.line', inverse_name='request_id')
    cout_total = fields.Float(string='Cout Total', compute='_compute_cout_total', store=True, default=0.0)
    causes = fields.Char(string='Causes ou Utilité', placeholder='Causes')
    observations = fields.Html(string='Observations', placeholder='observations')
    mise_en_marche = fields.Date(string='Date Mise en marche')
    main_doeuvre = fields.Float(string='Montant main d\'oeuvre', default=0.0)
    bon_commande_id = fields.Many2one(string='Numero bon de Commande', comodel_name='purchase.order', ondelete='cascade')
    debut = fields.Datetime(string='Date de debut') 
    chekpoint_ids = fields.One2many(string='Points de controle', comodel_name='maintenance.checkpoint.line', inverse_name='request_id')
    executant_id = fields.Many2one(string='Employé exécutant',comodel_name='hr.employee', required=True)
    
    


    @api.onchange('equipment_id')
    def onchange_chekpoint_ids(self):
        self.chekpoint_ids = self.equipment_id.checkpoint_ids
        
    # @api.model
    # def _notification_task(self):
    #     request = self.search([('done', '=', False)])
    #     if len(request)>0 :
    #         return True

    
    @api.depends('line_request_ids.cout', 'main_doeuvre')
    def _compute_cout_total(self):
        for main in self:
            cout_t = 0.0
            for line in main.line_request_ids:
                cout_t += line.cout
            self.cout_total = cout_t + main.main_doeuvre

    
    

class MaintenanceComposantLine(models.Model):
    _name = "maintenance.request.line"
    _description = 'Ordre de Maintenance line'
    
    
    cout = fields.Float(string='Cout', compute='cout_compute', store=True, default=0.0)
    request_id = fields.Many2one(string='Request', comodel_name='maintenance.request', ondelete='cascade')
    quantite_piece = fields.Integer(string='Quantite utilisee', default=0)
    product_id = fields.Many2one(string='Pièces', comodel_name='product.product', ondelete='restrict')
    prix_unitaire = fields.Float(string='Prix Unitaire', default=0.0)

    
    @api.depends('prix_unitaire', 'quantite_piece')
    def cout_compute(self):
        for line in self:
            line.cout = line.prix_unitaire*line.quantite_piece

    
    
    