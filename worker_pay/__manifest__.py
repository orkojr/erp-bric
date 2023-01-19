# -*- coding:utf-8 -*-

{
    'name': 'Worker payment',
    'category': 'Generic Modules/Human Resources',
    'sequence': 1,
    'author': 'Third',
    'summary': 'Worker payment For Odoo 15 Community Edition',
    'description': "Worker payment, Worker payment Odoo 15, Odoo Community Payroll",
    'license': 'LGPL-3',
    'depends': [
        'mail',
        'hr_contract',
        'hr_holidays',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/worker_payment_view.xml',
    ],
    'application': True,
}
