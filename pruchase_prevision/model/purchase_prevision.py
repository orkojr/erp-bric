from math import prod
from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import ValidationError
import calendar


class Prevision(models.Model):
    _name = 'purchase.prevision'
    _description = 'Purchase previsions'
    

    
    
    
    name = fields.Char('Name',readonly=True)
    planning_date = fields.Date('Date Debut')
    planning_date_fin = fields.Date('Date Fin')

    
    total_price = fields.Float(
        string='Montant total',
        compute="_compute_montant",
    )
    
    
    
    line_prevision_ids = fields.One2many(
        string='Previsions',
        comodel_name='purchase.prevision.line',
        inverse_name='prevision_id',
    )


    @api.depends('line_prevision_ids')
    def _compute_montant(self):
        for record in self:
            price = 0.0
            for prix in record.line_prevision_ids:
                price += prix.montant
            record.total_price = price
    
    @api.model
    def create(self,vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('purchase.prevision') or _('New')
        return super(Prevision,self).create(vals)
    

    @api.onchange('planning_date_fin')
    def onchange_date(self):
        if self.planning_date and self.planning_date_fin:
            if self.planning_date_fin < self.planning_date:
                raise ValidationError('the end date must be greater than the start date...!!')
    
    
    