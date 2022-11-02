# -*- coding: utf-8 -*-
{
    'name': "OdooCMS Faculty Portal",
    'summary': """
        Faculty Web Portal""",
    'description': """
        Faculty Web Portal
    """,
    'author': "Sulman Shaukat &amp; Farooq",
    'company': 'AARSOL & NUST (Joint Venture)',
    'website': "https://www.aarsol.com",
    'category': 'OdooCMS',
    'version': '1.0',
    'sequence': '1',
    'application':'true',
    'depends': ['website','odoocms','cms_notifications','cms_surveys'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        #'views/assets.xml',
        # 'views/assets.xml',
        #'views/templates.xml',
        'views/component/components.xml',
        'views/layout/layout_page.xml',
        'views/profile/user_profile_head.xml',
        'views/profile/user_profile.xml',
        #'views/footer.xml',
        'views/result/result_create_table.xml',
        'views/result/faculty_result_view.xml',
        'views/result/result.xml',
        'views/attendance/class_attendance.xml',
        'views/class_table.xml',
        #'views/faculty_financials.xml',
        'views/auth/faculty_password_reset.xml',
        # 'views/summary_attendance.xml',
        'views/notification/notifications.xml',
        'views/schedule/time_table.xml',
        'views/dashboard/faculty_dashboard.xml',
        'views/dashboard/external_dashboard.xml',
        'views/survey/survey_feedback.xml',

    ],
}