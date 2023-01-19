# -*- coding: utf-8 -*-

{
    'name': 'Activity',
    'version': '15.0.1.0.0',
    'summary': 'Notifier les recepyions',
    'description': """
        Permet de notifier le responsable de production 
          Sur les receptions a effectuer.
        """,
    'category': 'stock',
    'author': "Jordan KAMGA WAFO",
    'company': 'Third SARL',
    'maintainer': 'Third SARL',
    'website': "https://www.third.cm",
    'depends': [
        'mrp', 'stock', 
    ],
    'data': [
        'data/reception_cron.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

