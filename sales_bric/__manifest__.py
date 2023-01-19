# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Gestion ordre de chargement',
    'version': '1.0',
    'category': 'Hidden',
    'description': """
This module adds a shortcut on one or several opportunity cases in the CRM.
===========================================================================

This shortcut allows you to generate a sales order based on the selected case.
If different cases are open (a list), it generates one sales order by case.
The case is then closed and linked to the generated sales order.

We suggest you to install this module, if you installed both the sale and the crm
modules.
    """,
    'depends': ['sale_management', 'crm'],
    'data': [
        
        'views/sale_order_views.xml',
        'report/sale_report.xml',
        'report/sale_report_templates.xml',

    ],
    'auto_install': True,

    'license': 'LGPL-3',
}
