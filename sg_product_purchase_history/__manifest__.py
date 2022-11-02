# -*- encoding: utf-8 -*-
{
    'name': "Product Purchase History",
    'category': "Purchase",
    'version': "13.0.0.0",
    'summary': """Purchase History on product from""",
    'description': """Purchase details on product from view.""",
    'author': 'IDT',
    'website': 'http://www.infinitedt.com',
    'depends': ['purchase'],
    'data': [
        'views/product_view.xml',
    ],
    'installable': True,
    'application': False,
    'sequence': 1,
}
