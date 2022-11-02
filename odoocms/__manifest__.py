
{
    'name': 'OdooCMS Core',
    'version': '13.0.0.17',
    'summary': """Core Module for UMS""",
    'description': 'Core Module of Educational Institutes (University Level)',
    'category': 'OdooCMS',
    'sequence': 1,
    'author': 'IDT',
    'company': 'IDT',
    'website': 'http://www.infinitedt.com',
    'depends': ['base', 'mail','hr','website','aarsol_common'],

    'depends': ['base', 'mail','hr','website','aarsol_common'],
    'data': [
        'security/odoocms_security.xml',
        'security/ir.model.access.csv',
        
        'data/pre_data.xml',
        # 'data/odoocms.campus.csv',
        # 'data/odoocms.institute.csv',
        # 'data/odoocms.program.csv',
        'data/data.xml',
        
        
        'views/res_config_setting_view.xml',
        'views/odoocms_menu.xml',
        'views/assets.xml',
        'views/sequence.xml',
        'views/error_reporting_view.xml',
        'views/base_view.xml',

        'views/course_type.xml',

        'views/campus_view.xml',
        'views/institute_view.xml',
        'views/department_view.xml', # discipline views in department file
        'views/career_view.xml',

        'views/program_view.xml', # Specialization views in Program file
        'views/term_view.xml', # Session views in Term File

        'views/course_view.xml',
        'views/course_history_view.xml',
        'views/study_scheme_view.xml',

        'views/student_view.xml',
        'views/student_history_view.xml',
        'views/faculty_staff_view.xml',
        'views/public_holidays_view.xml',
        'views/odoocms_components.xml',
        'views/short_course_view.xml',

        # 'views/transcript_history_view.xml',

        # 'wizard/change_student_state_view.xml',
        'wizard/change_student_tag_view.xml',
        'wizard/student_comments_view.xml',
        'wizard/create_user.xml',
        'wizard/change_reg_to_reg.xml',
        'wizard/change_state.xml',

        'reports/report.xml',
        'reports/student_provisional_certificate_report.xml',
        'reports/student_id_card.xml',

        'reports/student_data.xml',

    ],
    'qweb': [
        "static/src/xml/base.xml",
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
