# -*- coding: utf-8 -*-

{
    'name': 'Suivi Vehicule',
    'version': '15.0.1.0.0',
    'summary': 'Suivi  Vehicule',
    'description': """
        Suivi  Vehicule lors des demandes internes.
        """,
    'category': 'Warehouse Management',
    'author': "Jordan kamga wafo",
    'company': 'Third SARL',
    'maintainer': 'Third SARL',
    'website': "https://www.third.cm",
    'depends': ['stock', 'maintenance'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template.xml',
        'views/maintenance_views.xml',
        # 'data/cron.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}

