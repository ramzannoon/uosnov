{
    'name': 'Student Project Management',
    'version': '13.0.0.0',
    'summary': '''Project management is a process that includes planning,
     putting the project plan into action.''',
    'description': '',
    'category': 'OdooCMS',
    'sequence': '1',
    'author': 'IDT',
    'company': 'IDT',
    'website': 'http://www.infinitedt.com',
    'license': 'AGPL-3',
    'depends': ['odoocms', 'mail', 'cms_notifications', 'odoocms_faculty_portal', 'odoocms_web', 'odoocms_student_portal'],
    'data': [

        'security/odoocms_spm_security.xml',
        'security/ir.model.access.csv',
        'data/cron.xml',
        'data/data.xml',
        'views/menu_spm.xml',
        'views/sequence.xml',
        'views/view_spm.xml',
        'views/view_spm_milestone.xml',
        'views/view_spm_faculty_portal.xml',
        'views/view_spm_student_portal.xml'
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'external_dependencies': {
        'python': [
        ],
    }
}
