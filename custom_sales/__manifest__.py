{
    'name': "Custom Sales",
    'description': 'Custom Sales',
    'author': 'Third',
    'depends': [
        'sale',
    ],
    'category': 'stock',
    'summary': """Custom Sales""",
    'maintainer': 'Third',
    'compagny': 'Third',
    'website':'http://www.third.cm',
    'license' : 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'views/apporteur.xml',
        'views/menu.xml',
        
    ],
   
    'application': True,
    
}