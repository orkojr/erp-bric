{
    'name': "Custom CRM",
    'description': 'CRM customiser',
    'author': 'Jordan Kamga Wafo',
    'depends': ['crm',],
    'category': 'sale',
    'summary': """Custom CRM""",
    'maintainer': 'Jordan Kamga Wafo',
    'compagny': 'Third',
    'website':'http://www.third.cm',
    'license' : 'LGPL-3',
    'data': [
        # 'security/custom_crm_security.xml',
        # 'security/ir.model.access.csv',
        'views/zone_view.xml',
        'views/quartier_view.xml',
        'views/client_view.xml',
        'reports/report.xml',
    ],
    'application': True,
}