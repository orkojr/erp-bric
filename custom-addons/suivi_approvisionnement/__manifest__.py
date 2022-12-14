{
    'name': "Suivi approvisionnement produit",
    'description': 'Suivi approvisionnement produit',
    'author': 'Jordan Kamga Wafo',
    'depends': [
        'base',
        'stock',
        'sale',
        'purchase',
        'mrp',
        'account',
        'custom_report',
        'suivi_production',
    ],
    'category': 'stock',
    'summary': """Suivi approvisionnement produit""",
    'maintainer': 'Jordan Kamga Wafo',
    'compagny': 'Third',
    'website':'http://www.third.cm',
    'license' : 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'wizard/report_suivi.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'suivi_approvisionnement/static/src/js/action_manager.js',
        ],
    },
    'application': True,
    
}