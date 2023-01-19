{
    'name': "Mrp Repport",
    'description': 'Mrp Repport',
    'author': 'Third',
    'depends': [
        'base',
        'mrp_plan',
        
    ],
    'category': 'stock',
    'summary': """Mrp Repport""",
    'maintainer': 'Third',
    'compagny': 'Third',
    'website':'http://www.third.cm',
    'license' : 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_production_inherit_view.xml',
        'views/mensuel_plan_view.xml',
        'views/mrp_plan_inherit.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'planning_repport/static/src/js/action_manager.js',
        ],
    },
    'application': True,
    
}