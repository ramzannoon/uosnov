# See LICENSE file for full copyright and licensing details.

{
    'name': 'Transport Management',
    'version': "13.0.0.6",
    'author': 'IDT',
    'website': 'http://www.infinitedt.com',
    'license': "AGPL-3",
    'category': 'School Management',
    'summary': 'A Module For Transport & Vehicle Management',
    'depends': ['odoocms', 'account', 'fleet'],
    'images': ['static/description/SchoolTransport.png'],
    'data': ['security/transport_security.xml',
             'security/ir.model.access.csv',
             'views/transport_view.xml',
             'views/report_view.xml',
             'views/vehicle.xml',
             'views/participants.xml',
             'data/transport_schedular.xml',
             'wizard/transfer_vehicle.xml',
             'wizard/terminate_reason_view.xml'],
    'demo': ['demo/transport_demo.xml'],
    'installable': True,
    'application': True
}
