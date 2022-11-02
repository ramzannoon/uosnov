{
    "name": "OdooCMS Exam",
    'version': '13.0.0.3',
    'license': 'LGPL-3',
    'category': 'OdooCMS',
    'sequence': 3,
    'summary': "Exam Management Module of OdooCMS""",
    'author': "IDT",
    'company': 'IDT',
    'website': 'http://www.infinitedt.com',
    'description': '''An easy way to handle the examinations in an educational system with better reports and
    exam valuation and exam result facilities''',

    'depends': ['odoocms_academic'],
    'data': [
        'security/odoocms_exam_security.xml',
        'security/ir.model.access.csv',

        'data/exam_data.xml',
        'data/sequence.xml',

        'menu/exam_menu_view.xml',

        'views/grade_gpa_view.xml',
        'views/grade_gpa_marks_view.xml',

        'views/class_view.xml',
        'views/student_view.xml',
        'views/requests.xml',
        'views/degree_transcript_requests.xml',
        'views/exam_disposals_view.xml',

        'views/examination.xml',
        # # 'views/exam_valuation.xml',

        'views/datesheet_view.xml',

        'views/res_config_setting_view.xml',

        # 'wizard/assign_grades_wiz_view.xml',
        # 'wizard/datesheet_wiz_view.xml',
        # 'wizard/datesheet_semester_wiz_view.xml',
        # 'wizard/grade_change_wiz_view.xml',
        # 'wizard/credits_change_wiz_view.xml',
        # 'wizard/grade_import_view.xml',
        # 'wizard/assign_subject_remarks_wiz_view.xml',
        # 'wizard/assign_semester_remarks_wiz_view.xml',

        'wizard/exam_disposal_wiz_view.xml',
        'wizard/exam_submit_fbs_wiz_view.xml',
        'wizard/re_calculate_result_view.xml',
        'wizard/revert_result_view.xml',

        'wizard/report/student_provisional_certificate_wiz_view.xml',
        # 'wizard/report/odoocms_transcript_wizard_view.xml',

        'wizard/report/gpa_wise_student_wiz_view.xml',
        'wizard/report/grade_wise_course_wiz_view.xml',
        # 'wizard/report/semester_result_export_view.xml',
        'wizard/report/gpa_warning_wizard_view.xml',
        'wizard/report/student_exam_slip_wiz_view.xml',
        'wizard/report/student_term_dmc_wiz_view.xml',
        'wizard/report/class_result_wiz_view.xml',
        'wizard/report/grade_change_report_wiz_view.xml',
        'wizard/report/student_provisional_result_wiz_view.xml',
        'wizard/report/batch_term_result_notification_wiz_view.xml',
        'wizard/report/student_term_result_letter_wiz_view.xml',
        'wizard/report/academic_deficiency_report_wiz_view.xml',
        'wizard/report/top_five_student_wiz_view.xml',
        # 'wizard/update_recheking_result.xml',
        
        
        'wizard/report/student_data_wiz_view.xml',
        #
        'reports/report.xml',

        'reports/student_provisional_certificate_report.xml',
        'reports/gpa_wise_student_report.xml',
        'reports/grade_wise_course_report.xml',
        'reports/gpa_warning_report.xml',
        'reports/student_exam_slip_report.xml',
        'reports/student_term_dmc_report.xml',
        'reports/class_result_report.xml',
        'reports/grade_change_report.xml',
        'reports/student_provisional_result_report.xml',
        'reports/batch_term_result_notification_report.xml',
        'reports/student_term_result_letter.xml',
        'reports/academic_deficiency_report.xml',
        'reports/top_five_student_report.xml',
        
        'reports/student_data.xml',

        # 'reports/datesheet_report.xml',
        # 'reports/datesheet_semester_report.xml',

    ],
    'images': ['static/description/banner.jpg'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
