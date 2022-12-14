from math import prod
from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import ValidationError
import calendar


class PurchasePrevisionLine(models.Model):
    _name = "purchase.prevision.line"
    _description = "Purchase prevision line"
    _order = 'id'
    _rec_name = "name"


     
    
    name = fields.Char('Name')
    
    date = fields.Date(
        string='Date',
        required=True,
    )

    day = fields.Char(
        string='Jour',
        required=True,
    )
    

    montant = fields.Float(
        string='Montant journee',
        compute="_compute_montant",
    )


    
    prevision_id = fields.Many2one(
        string='Prevision',
        comodel_name='purchase.prevision',
        ondelete='cascade',
    )
    

    
    article_liste_ids = fields.One2many(
        string='article_liste',
        comodel_name='prevision.article',
        inverse_name='prevision_line_id',
    )

    @api.model
    def create(self,vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('purchase.prevision.line') or _('New')
        return super(PurchasePrevisionLine,self).create(vals)

    
    
    @api.depends('article_liste_ids')
    def _compute_montant(self):
        for record in self:
            price = 0.0
            for prix in record.article_liste_ids:
                price += prix.total_value
            record.montant = price

    
    @api.onchange('date')
    def _onchange_date_start(self):
        if self.date:
            """ print (date)
            day, month, year = (int(i) for i in date.split(' '))     
            born = datetime.date(year, month, day)  """
            date11 = self.date.strftime("%d %m %Y")
            self.day = calendar.day_name[datetime.strptime(date11, '%d %m %Y').weekday()]
            
    
    
    
    
    
    
    
   

class PrevisionArticle(models.Model):
    _name = "prevision.article"
    _description = "Presion article"
    _order = 'id'
    _rec_name = "product_id"


    
    product_id = fields.Many2one('product.product', 'Article', required=True)
    
    analytic_account_id = fields.Many2one(
        string='Compte analytique',
        comodel_name='account.analytic.account',
        ondelete='cascade',
    )
    
        
    product_qty = fields.Float(
        'Quantity', default=1.0,
        digits='Product Unit of Measure', required=True)
    product_uom_qty = fields.Float(
        'Quantity', default=1.0,
        digits='Product Unit of Measure', required=True)
    product_uom_id = fields.Many2one(
        'uom.uom', 'Product Unit of Measure',      
        required=True,
        help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control")
    unit_value = fields.Float(
        string='Valeur unitaire',
        default=0.0,
    )
    total_value = fields.Float(
        string='Valeur totale',
        compute='_compute_total_value',
    )
    
    
    prevision_line_id = fields.Many2one(
        string='Prevision',
        comodel_name='purchase.prevision.line',
        ondelete='cascade',
    )


    @api.depends('unit_value','product_qty')
    def _compute_total_value(self):
        for record in self:
            record.total_value = record.product_qty*record.unit_value
    
    
    
