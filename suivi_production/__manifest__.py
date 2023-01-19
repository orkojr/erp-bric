{
    'name': "Suivi Production",
    'description': 'Suivi Production',
    'author': 'Jordan Kamga Wafo',
    'depends': [
        'base',
        'stock',
        'mrp',
    ],
    'category': 'stock',
    'summary': """Suivi Production""",
    'maintainer': 'Jordan Kamga Wafo',
    'compagny': 'Third',
    'website':'http://www.third.cm',
    'license' : 'LGPL-3',
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'suivi_production/static/src/js/action_manager.js',
        ],
    },
    'application': True,
    
}