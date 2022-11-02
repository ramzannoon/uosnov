
{
    'name': 'Asset Adjustments',
    'version': '13.0.0.0',
    'category': 'Account',
    "description": """ Asset Adjustments """,
    'author': "IDT",
    'website': 'http://www.infinitedt.com',
    'license': 'AGPL-3',
    'depends': [
        'base', 'account_asset',
    ],
    'data': [
        'views/account_asset_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}
