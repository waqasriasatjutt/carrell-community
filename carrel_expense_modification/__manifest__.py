{
    'name': 'Carrel Expense Modification',
    'version': '1.0',
    'author': 'Carrel Expense Modification',
    'category': 'Sales/Sales',
    'description': """
""",
    'website': 'https://www.Carrel Transportation.com',
    "price": "0.00",
    "currency": "EUR",
    "license": "Other proprietary",
    'summary': "Carrel Expense Modification",
    'depends': ['base', 'hr_expense', 'hr', 'stock'],
    'data': [
        'data/ir_sequence_data.xml',
        'data/ir.model.access.csv',
        'views/hr_expense.xml',
        'views/custom_expense.xml',
        'views/asset.xml',
    ],
    'qweb': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
