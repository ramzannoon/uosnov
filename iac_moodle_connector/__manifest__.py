# -*- coding: utf-8 -*-
{
    'name': "iac_moodle_connector",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '13.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','odoocms','odoocms_registration'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/iac_server_actions.xml',
        'views/inherit_iac_models.xml',
        'views/views.xml',
        'wizards/wizard_message.xml',
        'views/templates.xml',
        'views/inherit_search_view.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
