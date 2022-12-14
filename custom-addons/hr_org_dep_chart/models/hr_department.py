# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api


class Department(models.Model):
    _inherit = ["hr.department"]

    subordinate_ids = fields.One2many('hr.department', string='Subordinates', compute='_compute_subordinates', help="Direct and indirect subordinates",
                                      compute_sudo=True)

    child_all_count = fields.Integer(
        'Indirect Subordinates Count',
        compute='_compute_subordinates', recursive=True, store=False,
        compute_sudo=True)

    def _get_subordinates(self, parents=None):
        """
        Helper function to compute subordinates_ids.
        Get all subordinates (direct and indirect) of an department.
        An department can be a manager of his own manager (recursive hierarchy; e.g. the CEO is manager of everyone but is also
        member of the RD department, managed by the CTO itself managed by the CEO).
        In that case, the manager in not counted as a subordinate if it's in the 'parents' set.
        """
        if not parents:
            parents = self.env[self._name]

        indirect_subordinates = self.env[self._name]
        parents |= self
        direct_subordinates = self.child_ids - parents
        for child in direct_subordinates:
            child_subordinate = child._get_subordinates(parents=parents)
            indirect_subordinates |= child_subordinate
        return indirect_subordinates | direct_subordinates


    @api.depends('child_ids', 'child_ids.child_all_count')
    def _compute_subordinates(self):
        for department in self:
            department.subordinate_ids = department._get_subordinates()
            department.child_all_count = len(department.subordinate_ids)
