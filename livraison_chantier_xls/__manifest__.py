{
    'name': "Livraison chantier Report",
    'description': 'Livraison chantier',
    'author': 'Jordan Kamga Wafo',
    'depends': [
        'base',
        'stock',
        'sale',
        'purchase',
        'project',
    ],
    'category': 'stock',
    'summary': """Livraison chantier""",
    'maintainer': 'Jordan Kamga Wafo',
    'compagny': 'Third',
    'website':'http://www.third.cm',
    'license' : 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'wizard/report_liv_chant.xml',
        'views/stock_picking_inherit.xml',
        'views/sale_order_inherit.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'livraison_chantier_xls/static/src/js/action_manager.js',
        ],
    },
}