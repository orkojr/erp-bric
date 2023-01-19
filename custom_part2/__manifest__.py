{
    'name': "Custom Partner 2",
    'description': 'Partner customiser',
    'author': 'Jordan Kamga Wafo',
    'depends': ['base','crm'],
    'category': 'sale',
    'summary': """Custom Partner""",
    'maintainer': 'Jordan Kamga Wafo',
    'compagny': 'Third',
    'website':'http://www.third.cm',
    'license' : 'LGPL-3',
    'data': [
        'security/custom_crm_security.xml',
        'security/invisible.xml',
        'security/ir.model.access.csv',
        'views/zone_view.xml',
        'views/quartier_view.xml',
        'views/client_view.xml',
    ],
    'application': True,
}