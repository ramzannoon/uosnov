{
    'name': 'Check Generation',
    'version': '13.0.0.3',
    'category': 'Account',
    "description": """ Check Generation """,
    'author': "IDT",
    'website': 'http://www.infinitedt.com',
    'license': 'AGPL-3',
    'depends': ['base', 'account'],
    'data': [
        'views/account_payment.xml',
        'reports/account_check_report.xml',
        'reports/reports.xml',
    ],
    'installable': True,
    'application': True,
}
