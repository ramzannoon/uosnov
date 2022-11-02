{
    'name': 'Exam Setup',
    'version': '13.0.0.0.1',
    'summary': '''Setup for examination,''',
    'description': '',
    'category': 'OdooCMS',
    'sequence': '1',
    'author': 'IDT',
    'company': 'IDT',
    'website': 'http://www.infinitedt.com',
    'license': 'AGPL-3',
    'depends': ['odoocms', 'odoocms_exam', 'mail'],
    'data': [
        'security/odoocms_exam_setup_security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/menu_exam_setup.xml',
        'wizard/datesheet_report_wiz_view.xml',
        'wizard/sitting_type_wiz_view.xml',
        'wizard/sitting_plan_report_wiz_view.xml',
        'wizard/center_student_report_wiz_view.xml',
        'views/view_exam_center.xml',
        'views/view_exam_staff.xml',
        'views/view_exam_sitting_plan.xml',
        'reports/report.xml',
        'reports/datesheet_report.xml',
        'reports/sitting_plan_report.xml',
        'reports/center_student_report.xml',

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
