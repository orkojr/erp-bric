{
    'name': "Custom Stock Report",
    'description': 'Report pour la journee',
    'author': 'Jordan Kamga Wafo',
    'depends': [
        'base',
        'stock',
        'sale',
        'mrp',
        'custom_sml',
        'purchase',
    ],
    'category': 'Warehouse',
    'summary': """Custom Srock report""",
    'maintainer': 'Jordan Kamga Wafo',
    'compagny': 'Third',
    'website':'http://www.third.cm',
    'license' : 'LGPL-3',
    'data': [
        'security/etat_stock_security.xml',
        'security/ir.model.access.csv',
        'views/wizard_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'custom_report/static/src/js/action_manager.js',
        ],
    },
    'application': True,
}