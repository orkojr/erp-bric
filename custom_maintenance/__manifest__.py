{
    'name': "Custom Maintenance",
    'description': 'Custom Maintenance',
    'author': 'Jordan Kamga Wafo',
    'depends': [
        'base',
        'stock',
        'maintenance',
        'purchase',
        
    ],
    'summary': """Custom Maintenance""",
    'maintainer': 'Third',
    'compagny': 'Third',
    'website':'http://www.third.cm',
    'license' : 'LGPL-3',
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/maintenance_cron.xml',
        'views/equipement.xml',
        'views/ordre_maintenance.xml',
        'views/point_controle_view.xml',
    ],
    'application': True,
}