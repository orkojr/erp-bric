# -*- coding: utf-8 -*-

{
    'name': 'Employee Tasks',
    'version': '15.0.1.0.0',
    'summary': 'Tâches de l\' employé',
    'description': """
        Permet de définir et Lister les Tâches de l'employée.
        """,
    'category': 'Generic Modules/Human Resources',
    'author': "Jordan kamga wafo",
    'company': 'Third SARL',
    'maintainer': 'Third SARL',
    'website': "https://www.third.cm",
    'depends': ['hr','project'],
    'data': [
        'views/hr_timesheet.xml',
        'views/hr_employee.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}

