{
    'name': "Purchase Couts",
    'description': 'Purchase Couts',
    'author': 'Third',
    'depends': [
        'base',
        'stock',
        'sale',
        'purchase',
        'account',
        'custom_report',
    ],
    'category': 'stock',
    'summary': """Purchase Couts""",
    'maintainer': 'Third',
    'compagny': 'Third',
    'website':'http://www.third.cm',
    'license' : 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_approv_view.xml',
        'wizard/purchase_cout_wizard.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'purchase_cout/static/src/js/action_manager.js',
        ],
    },
    'application': True,
    
}