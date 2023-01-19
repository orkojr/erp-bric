{
    'name': "Suivi achat produit",
    'description': 'Suivi achat produit',
    'author': 'Jordan Kamga Wafo',
    'depends': [
        'base',
        'stock',
        'sale',
        'purchase',
        'account',
        'custom_report',
    ],
    'category': 'stock',
    'summary': """Suivi achat produit""",
    'maintainer': 'Jordan Kamga Wafo',
    'compagny': 'Third',
    'website':'http://www.third.cm',
    'license' : 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'wizard/report_suivi_achat.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'suivi_achat/static/src/js/action_manager.js',
        ],
    },
    'application': True,
    
}