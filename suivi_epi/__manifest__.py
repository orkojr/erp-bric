{
    'name': "Suivi EPI",
    'description': 'Suivi EPI',
    'author': 'Third',
    'depends': [
        'hr',
        'hr_skills',
        'hr_recrutement_access',
    ],
    'category': 'stock',
    'summary': """Suivi EPI""",
    'maintainer': 'Third',
    'compagny': 'Third',
    'website':'http://www.third.cm',
    'license' : 'LGPL-3',
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        # 'data/activity.xml',
        'data/cron.xml',
        'views/epi_views.xml',
        'views/epi_line_views.xml',
        'views/epi_poste_views.xml',
        'views/hr_employee_inherit_views.xml',
        
    ],
    'assets': {
        'web.assets_backend': [
            'suivi_epi/static/src/js/action_manager.js',
        ],
    },
    'application': True,
    
}