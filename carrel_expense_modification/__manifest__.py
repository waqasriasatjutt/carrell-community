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
        'views/sub_categ.xml',
        'views/partner.xml',
        'views/asset.xml',
    ],
    'qweb': [
    ],
    'test': [
    ],
    'assets': {
        'web.assets_backend': [
            'carrel_expense_modification/static/src/css/custom_styles.css',
        ],
    },

    'installable': True,
    'auto_install': False,
}
