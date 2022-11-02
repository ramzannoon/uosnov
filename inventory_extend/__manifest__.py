
{
    'name': 'Inventory Extend',
    'version': '13.0.0.0',
    'description': "Inventory Extend",
    'summary': "Inventory Extend",
    'category': 'Inventory',
    'author': 'IDT',
    'website': 'http://www.infinitedt.com',
    'depends': ['base', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_product.xml',
        'views/product_template.xml',
        'views/brand_brand_view.xml',
    ],

    'license': "AGPL-3",
    'installable': True,
    'auto_install': False,
}
