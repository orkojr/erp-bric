# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models


class CommissionInput(models.Model):
    _inherit = 'hr.payslip'

    def get_inputs(self, contract_ids, date_from, date_to):
        """This Compute the other inputs to employee payslip.
                           """
        res = super(CommissionInput, self).get_inputs(contract_ids, date_from, date_to)
        contract_obj = self.env['hr.contract']
        emp_id = contract_obj.browse(contract_ids[0].id).employee_id
        adv_salary = self.env['sale.apporteur'].search([('employe_id', '=', emp_id.id)])
        print('Commission:',adv_salary)
        for adv_obj in adv_salary:
            """ current_date = date_from.month
            date = adv_obj.validation_date
            existing_date = date.month
            if current_date == existing_date: """
                
            state = adv_obj.state
            amount = adv_obj.cout
            for result in res:
                print('Commission:',result)
                if state == 'valide' and adv_obj.is_paid == False and result.get('code') == 'COM':
                    
                    result['amount'] = amount
        return res