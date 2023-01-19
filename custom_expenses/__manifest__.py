{
    'name': "Custom Expense",
    'description': 'Custom Expense',
    'author': 'THIRD',
    'depends': [
        'base',
        'hr_expense',
        
    ],
    'summary': """Custom Hr Expenses""",
    'maintainer': 'Third',
    'compagny': 'Third',
    'website':'http://www.third.cm',
    'license' : 'LGPL-3',
    'data': [
        # 'security/security.xml',
        # 'security/ir.model.access.csv',        
        'views/hr_expenses.xml',
       
    ],
    'application': True,
}