# -*- coding: utf-8 -*-
{
    'name': "Custom Payroll",

    'summary': """
        This Module Contains Main Custom Functionalities of LTS Payroll""",

    'description': """
        This Module Contains Main Custom Functionalities of LTS Payroll
    """,

    'author': "IDT",
    'website': 'http://www.infinitedt.com',

    'category': 'All',
    'version': '13.0.0.10',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_payroll', 'hr_contract', 'hr'],

    # always loaded
    'data': [
        'data/security.xml',
        'security/ir.model.access.csv',
        'reports/medical_data.xml',
        'reports/print_employee_details.xml',
        'reports/report.xml',
        'views/employees.xml',
        'views/payroll_views.xml',
        'views/employee_type.xml',
        'views/contract_views.xml',
    ],

}
