# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request


class HrOrgChartController(http.Controller):
    _managers_level = 5  # FP request

    def _check_department(self, department_id, **kw):
        if not department_id:  # to check
            return None
        department_id = int(department_id)

        if 'allowed_company_ids' in request.env.context:
            cids = request.env.context['allowed_company_ids']
        else:
            cids = [request.env.company.id]

        Department = request.env['hr.department'].with_context(allowed_company_ids=cids)
        # check and raise
        if not Department.check_access_rights('read', raise_exception=False):
            return None
        try:
            Department.browse(department_id).check_access_rule('read')
        except AccessError:
            return None
        else:
            return Department.browse(department_id)

    def _prepare_department_data(self, department):
        parent = department.sudo().parent_id
        return dict(
            id=department.id,
            name=department.name,
            link='/mail/view?model=%s&res_id=%s' % ('hr.department', department.id,),
            parent_id=parent,
            # job_name=job.name or '',
            # job_title=employee.job_title or '',
            direct_sub_count=len(department.child_ids),
            indirect_sub_count=department.child_all_count,
        )

    @http.route('/hr_org_dep_chart/get_redirect_model', type='json', auth='user')
    def get_redirect_model(self):
        
        return 'hr.department'

    @http.route('/hr_org_dep_chart/get_org_dep_chart', type='json', auth='user')
    def get_org_dep_chart(self, department_id, **kw):

        department = self._check_department(department_id, **kw)
        if not department:  # to check
            return {
                'managers': [],
                'children': [],
            }

        # compute employee data for org chart
        ancestors, current = request.env['hr.department'].sudo(), department.sudo()
        while current.parent_id and len(ancestors) < self._managers_level+1:
            ancestors += current.parent_id
            current = current.parent_id

        values = dict(
            self=self._prepare_department_data(department),
            managers=[
                self._prepare_department_data(ancestor)
                for idx, ancestor in enumerate(ancestors)
                if idx < self._managers_level
            ],
            managers_more=len(ancestors) > self._managers_level,
            children=[self._prepare_department_data(child) for child in department.child_ids],
        )
        values['managers'].reverse()
        return values

    @http.route('/hr_org_dep_chart/get_subordinates', type='json', auth='user')
    def get_subordinates(self, department_id, subordinates_type=None, **kw):
        """
        Get department subordinates.
        Possible values for 'subordinates_type':
            - 'indirect'
            - 'direct'
        """
        department = self._check_department(department_id, **kw)
        if not department:  # to check
            return {}

        if subordinates_type == 'direct':
            res = department.child_ids.ids
        elif subordinates_type == 'indirect':
            res = (department.subordinate_ids - department.child_ids).ids
        else:
            res = department.subordinate_ids.ids

        return res
