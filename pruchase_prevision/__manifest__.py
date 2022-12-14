# -*- coding: utf-8 -*-
# Copyright 2016, 2018 Mapolgroups

{
    "name": "Purchase Previsions",
    "summary": "Purchase Previsions",
    "category": "purchase",
    'author' : 'Third',
    "description": """
        This module helps to purchase .
    """,
    "license": "LGPL-3",
    "installable": True,
    'application': True,
    'auto_install': False,
    "depends": [
        'base','stock','product','mrp','stock_request', 'account','purchase'
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/purchase_prevision.xml',
        'data/mail.xml',
        'view/prevision_view.xml',
        'view/prevision_line_view.xml',
    ],
}
