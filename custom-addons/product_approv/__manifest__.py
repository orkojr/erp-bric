# -*- coding: utf-8 -*-

{
    'name': 'Réapprovisionnement',
    'version': '15.0.1.0.0',
    'summary': 'Règle de Réapprovisionnement',
    'description': """
        Permet de notifier le  Réapprovisionnement.
        """,
    'category': 'Warehouse Management',
    'author': "Jordan kamga wafo",
    'company': 'Third SARL',
    'maintainer': 'Third SARL',
    'website': "https://www.third.cm",
    'depends': ['hr'],
    'data': [
        'data/approv_cron.xml',
        'views/product_template.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}

