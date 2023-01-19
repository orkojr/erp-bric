# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "Purchase Request",
    "author": "THIRD",
    "version": "15",
    "summary": "Use this module to have notification of requirements of "
    "materials and/or external services and keep track of such "
    "requirements.",
    "website": "",
    "category": "Purchase Request Management",
    "depends": ["purchase", "product", "purchase_stock", "hr","fleet","account", "om_account_budget", "account","custom_maintenance"],
    "data": [
        "security/purchase_request.xml",
        "security/ir.model.access.csv",
        "data/purchase_request_sequence.xml",
        "data/purchase_request_data.xml",
        "reports/report_purchase_request.xml",
        "wizard/purchase_request_line_make_purchase_order_view.xml",
        "wizard/purchase_request_line_make_account_move_view.xml",
        "wizard/purchase_request_line_make_account_recu_view.xml",
        "views/request_motif_view.xml",
        "views/purchase_request_view.xml",
        "views/purchase_request_line_view.xml",
        "views/purchase_request_report.xml",
        "views/product_template.xml",
        "views/purchase_order_view.xml",
        "views/stock_move_views.xml",
        "views/stock_picking_views.xml",
        "views/employe_request_view.xml",
        
    ],
    "demo": [],
    "license": "LGPL-3",
    "installable": True,
    "application": True,
}
