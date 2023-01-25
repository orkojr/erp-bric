{
    'name': "Custom Sales",
    'description': 'Custom Sales',
    'author': 'Third',
    'depends': [
        'sale',
        'purchase_request',
        'suivi_epi',
    ],
    'category': 'stock',
    'summary': """Custom Sales""",
    'maintainer': 'Third',
    'compagny': 'Third',
    'website':'http://www.third.cm',
    'license' : 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_view.xml',
        'views/apporteur.xml',
        'views/menu.xml',
        'views/hr_employee_inherit.xml',
        
    ],
   
    'application': True,
    
}