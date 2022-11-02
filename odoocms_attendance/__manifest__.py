{
    "name": "OdooCMS Attendance",
    'version': '13.0.0.0',
    'license': 'LGPL-3',
    'category': 'OdooCMS',
    'sequence': 3,
    'summary': "Student Attendance Management Module of OdooCMS""",
    'author': 'GlobalXS',
    'company': 'GlobalXS Technology Solutions',
    'website': "http://www.globalxs.co",
    'description': 'An easy and efficient management tool to manage and track student'
                   ' attendance. Enables different types of filtration to generate '
                   'the adequate reports',
    
    'depends': ['odoocms_academic'],
    'data': [
        'security/ir.model.access.csv',
        'security/odoocms_attendance_security.xml',
        'data/sequence.xml',
        'views/menu_view.xml',

        'views/students_attendance.xml',
        'views/attendance_inherit_view.xml',
        'views/res_config_setting_view.xml',
        'views/student_requests.xml',
        # 'views/student_view.xml',
        #
        'wizard/generate_roaster_view.xml',
        'wizard/re_generate_lines_view.xml',
        'wizard/short_attendance_warning_wizard_view.xml',

        'wizard/reports/student_attendance_report_wizard_view.xml',
        'wizard/reports/component_attendance_report_wizard_view.xml',
        'wizard/reports/class_attendance_report_wizard_view.xml',
        'wizard/reports/short_attendance_report_wizard_view.xml',
        'wizard/reports/summary_attendance_report_wizard_view.xml',
        
        'reports/student_attendance_report.xml',
        'reports/component_attendance_report.xml',
        'reports/class_attendance_report.xml',
        
        'reports/short_attendance_report.xml',
        'reports/summary_attendance_report.xml',
        'reports/short_attendance_warning_report.xml',
        'reports/report.xml',
        
    ],
    'images': ['static/description/banner.jpg'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
