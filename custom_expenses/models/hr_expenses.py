# -*- coding: utf-8 -*-

from email.policy import default
from itertools import product
from odoo import api, fields, models, SUPERUSER_ID, _
import re
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero, float_repr
from odoo.tools.misc import clean_context, format_date
from odoo.addons.account.models.account_move import PAYMENT_STATE_SELECTION


class HrExpense(models.Model):
    _inherit = "hr.expense"
    
    post_depense = fields.Many2one('account.budget.post', 'Poste de depense')
    # state = fields.Selection(selection_add=[('validation', "Validation de la direction"),('done',)],ondelete={'validation' : 'set default'})

    # @api.depends('sheet_id', 'sheet_id.account_move_id', 'sheet_id.state')
    # def _compute_state(self):
    #     for expense in self:
    #         if not expense.sheet_id or expense.sheet_id.state == 'draft':
    #             expense.state = "draft"
    #         elif expense.sheet_id.state == "cancel":
    #             expense.state = "refused"
    #         elif expense.sheet_id.state == "approve" or expense.sheet_id.state == "post":
    #             expense.state = "approved"
    #         elif expense.sheet_id.state == "validation":
    #             expense.state = "validation"
    #         elif not expense.sheet_id.account_move_id:
    #             expense.state = "reported"
    #         else:
    #             expense.state = "done"
    

class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"
    
    
    state = fields.Selection(selection_add=[('validation', "Validation de la direction"),('post',)],ondelete={'validation' : 'set default'})
    
    def validation(self):
        self.state ='validation'
    
    
    def action_sheet_move_create(self):
        samples = self.mapped('expense_line_ids.sample')
        if samples.count(True):
            if samples.count(False):
                raise UserError(_("You can't mix sample expenses and regular ones"))
            self.write({'state': 'post'})
            return

        if any(sheet.state != 'validation' for sheet in self):
            raise UserError(_("You can only generate accounting entry for approved expense(s)."))

        if any(not sheet.journal_id for sheet in self):
            raise UserError(_("Specify expense journal to generate accounting entries."))

        expense_line_ids = self.mapped('expense_line_ids')\
            .filtered(lambda r: not float_is_zero(r.total_amount, precision_rounding=(r.currency_id or self.env.company.currency_id).rounding))
        res = expense_line_ids.with_context(clean_context(self.env.context)).action_move_create()
        for sheet in self.filtered(lambda s: not s.accounting_date):
            sheet.accounting_date = sheet.account_move_id.date
        to_post = self.filtered(lambda sheet: sheet.payment_mode == 'own_account' and sheet.expense_line_ids)
        to_post.write({'state': 'post'})
        (self - to_post).write({'state': 'done'})
        self.activity_update()
        return res

   

    
    
    
    
    
    