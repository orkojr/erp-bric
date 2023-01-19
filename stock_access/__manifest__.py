{
    'name': "Stock Access",
    'description': 'Stock Access',
    'author': 'Third',
    'depends': [
        'base',
        'stock',
    ],
    'category': 'stock',
    'summary': """Stock Access""",
    'maintainer': 'Third',
    'compagny': 'Third',
    'website':'http://www.third.cm',
    'license' : 'LGPL-3',
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/stock_access_view.xml',
        'views/stock_picking_view.xml',
    ],
    
    'application': True,
    
}