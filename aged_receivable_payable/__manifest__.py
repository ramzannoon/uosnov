# -*- coding: utf-8 -*-
{
    'name': "Aged Receivable Payable Report",
    'summary': """Aged Receivable Payable Report""",
    'author': "IDT",
    'website': 'http://www.infinitedt.com',
    'category': 'Accounts',
    'version': '13.0.0.0',
    'depends': ['base', 'web', 'product', 'account_accountant', 'report_xlsx'],
    'data': [
        'views/aged_receivable_payable.xml',
        'views/aged_receivable_payable_xlsx.xml',
        'views/module_report.xml',
    ]
}
