{
    'name': 'Purchase Reports',
    'version': '13.0.0.3',
    'category': 'Purchase',
    "description": """ Purchase Reports """,
    'author': "IDT",
    'website': 'http://www.infinitedt.com',
    'license': 'AGPL-3',
    'depends': [
        'base', 'stock'
    ],
    'data': [
        'security/groups.xml',
        'views/stock_picking.xml',
        'reports/reports.xml',
        'reports/gate_pass.xml',
        'reports/product_issuance_report.xml',
    ],
    'installable': True,
    'application': True,
}
