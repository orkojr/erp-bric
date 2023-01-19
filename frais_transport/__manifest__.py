{
    'name': "Frais de Transport",
    'description': 'Frais de Transport',
    'depends': [
        'base',
        'stock',
        'custom_part2',
        'fleet',
    ],
    'category': 'stock',
    'summary': """Frais de Transport""",
    'compagny': 'Third',
    'website':'http://www.third.cm',
    'license' : 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/frais_transport.xml',
        # 'wizard/frais.xml',
    ],
    'application': True,
    
}