# -*- coding: utf-8 -*-
{
    'name': "Customized CRM",

    'summary': """
        Customized CRM""",

    'description': """
        Customized CRM
    """,

    'author': "IDT",
    'website': 'http://www.infinitedt.com',

    'category': 'crm',
    'version': '13.0.0.16',

    # any module necessary for this one to work correctly
    'depends': ['crm', 'base', 'mail','sales_team','school_transport'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/template.xml',
        'views/crm_lead_views.xml',
        'views/pending_reasons.xml',
        'views/lead_type.xml',
    ],
}
