# -*- coding: utf-8 -*-
# Copyright 2016, 2018 Mapolgroups

{
    "name": "Mapol MRP Planning",
    "summary": "MRP Planning",
    "version": "12.1",
    "category": "Tools",
    'author' : 'Mapol Business Solution Pvt Ltd',
    'website' : 'http://www.mapolbs.com/',
    "description": """
        This module helps to plan the production.
    """,
    "license": "LGPL-3",
    "installable": True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/icon.png'],
    "depends": [
        'base','stock','product','mrp','stock_request','project',
    ],
    "data": [
        'security/mrp_plan_security.xml',
        'security/ir.model.access.csv',
        'data/mail.xml',
        'view/mrp_plan_line_view.xml',
        'view/mrp_plan_view.xml',
        
        'report/mrp_plan_report_views_main.xml',
        'report/mrp_plan_templates.xml',
    ],
}
