# -*- coding: utf-8 -*-

{
    'name': 'Employee Objectifs',
    'version': '15.0.1.0.0',
    'summary': 'objectifs de l\'employée',
    'description': """
        Permet de Lister les objectifs de l'employée.
        """,
    'category': 'Generic Modules/Human Resources',
    'author': "Jordan kamga wafo",
    'company': 'Third SARL',
    'maintainer': 'Third SARL',
    'website': "https://www.third.cm",
    'depends': ['hr'],
    'data': [
        'data/objectif_cron.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/objectif_views.xml',
        'views/hr_employee.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}

