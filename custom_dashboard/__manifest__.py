{
    'name': "Custom Dashboard",
    'description': 'Tableau de bord customiser',
    'author': 'Jordan Kamga Wafo',
    'depends': ['point_of_sale',],
    'category': 'sale',
    'summary': """Dashboard""",
    'maintainer': 'Jordan Kamga Wafo',
    'compagny': 'orkojkdev',
    'website':'http://orkojkdev.com',
    'license' : 'LGPL-3',
    'data': [
        'views/dashboard_action.xml',
    ],
    'qweb': ['static/src/xml/dashboard.xml '],
    'images': [],
    'application': True,
}