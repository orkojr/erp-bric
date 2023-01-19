# -*- coding: utf-8 -*-

{
    'name': 'Avances sur salaire',
    'version': '15.0.1.0.0',
    'summary': 'Plannification Avances sur salaire',
    'description': """
        Permet de notifier les responsables des avances
          salaire et annuler les demandes non traitées.
        """,
    'category': 'Generic Modules/Human Resources',
    'author': "Jordan KAMGA WAFO",
    'company': 'Third SARL',
    'maintainer': 'Third SARL',
    'website': "https://www.third.cm",
    'depends': [
        'hr', 'account', 
        'hr_contract',
        'ohrms_salary_advance',
    ],
    'data': [
        'data/avance_cron.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}

