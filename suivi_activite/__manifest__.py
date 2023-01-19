{
    'name': "Suivi Activite ",
    'description': 'Suivi Activite de l\'entreprise',
    'author': 'Third',
    'depends': [
        'base',
        'account',
    ],
    'category': 'stock',
    'summary': """Suivi Activite""",
    'maintainer': 'Third',
    'compagny': 'Third',
    'website':'http://www.third.cm',
    'license' : 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'wizard/report_suivi.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'suivi_activite/static/src/js/action_manager.js',
        ],
    },
    'application': True,
    
}