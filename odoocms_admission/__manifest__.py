# -*- coding: utf-8 -*-

{
    'name': "OdooCMS Admission",
    'version': '13.0.0.32',
    'license': 'LGPL-3',
    'category': 'OdooCMS',
    'sequence': 3,
    'summary': "Admission Module of Educational""",
    'author': 'IDT',
    'company': 'IDT',
    'website': 'http://www.infinitedt.com',
    'depends': ['odoocms', 'mail', 'crm', 'odoocms_fee'],  # 'utm','website_mail','website_partner','mail','website_form','website'
    'data': [
        # 'data/batch_entry_test_temp.xml',
        'data/application_email.xml',
        'data/offered_program_ind.xml',
        'data/batch_interview_temp.xml',
        'data/verification_reject.xml',
        'data/batch_entry_test_temp_ind.xml',
        'data/batch_interview_temp_ind.xml',
        'data/batch_offered_program.xml',
        'data/application_submission_temp.xml',
        'security/odoocms_admission_security.xml',
        'security/ir.model.access.csv',



        'views/sequence.xml',
        'menus/odoocms_admission_menu.xml',

        # 'wizard/application_reject_view.xml',
        'wizard/non_subsidized_form_wizard_view.xml',
        'wizard/odoocms_merit_register_wizard_view.xml',
        'wizard/odoocms_merit_status_view.xml',
        # 'wizard/odoocms_close_register_wizard_view.xml',
        'wizard/odoocms_due_date_wizard_view.xml',
        'wizard/generate_lead.xml',
        'wizard/send_email.xml',

        'wizard/report/odoocms_preference_wizard_view.xml',
        # 'wizard/report/odoocms_meritlist_report_wizard_view.xml',
        'wizard/report/odoocms_merit_interview_wizard_view.xml',
        'wizard/report/odoocms_final_merit_list_wizard_view.xml',

        'views/admission_register_view.xml',
        'views/odoocms_admission_quota.xml',
        'views/odoocms_application_view.xml',
        'views/mass_action_application.xml',
        'views/documents_view.xml',
        'views/odoocms_merit_list.xml',
        'views/odoocms_admission_common.xml',
        'views/student_view.xml',
        'views/batch_entry_test.xml',
        'views/batch_interview.xml',
        'views/batch_offered_program.xml',
        'views/odoocms_opening_date.xml',
        'views/lead_calls.xml',
        'views/odoocms_sc_application_view.xml',
        # 'views/test_schedule.xml'

        # 'reports/student_preference_report.xml',
        # 'reports/non_subsidized_form_report.xml',
        'reports/student_meritlist_report.xml',
        'reports/student_merit_interview_report.xml',
        'reports/student_final_merit_list_report.xml',
        'reports/admission_register_report.xml',
        'reports/report.xml',

        # 'views/admission_template.xml',
        # 'views/portal_templates.xml',

    ],
    'demo': [
        # 'demo/admission_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
