# -*- coding: utf-8 -*-

{
    'name': 'HR Department Organizational Chart',
    'version': '15.0.1.0.0',
    'summary': 'HR Department organizational chart',
    'description': 'HR Department organizational chart',
    'author': 'Jordan Kamga Wafo',
    'company': 'Third',
    'maintainer': 'Third',
    'category': 'Generic Modules/Human Resources',
    'website': "https://www.third.cm",
    'depends': ['hr'],
    'data': [
        'views/show_department_chart.xml',
        'views/assets.xml',
    ],
    'qweb': ['static/src/xml/chart_view.xml'],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}