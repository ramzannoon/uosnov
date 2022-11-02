# -*- coding: utf-8 -*-
{
    'name': "OdooCMS Employee Portal",
    'summary': """Employee Web Portal""",
    'description': """Web Portal for Employee""",
    'author': "Infinite Scaleup ",
    'company': 'Student Portal',
    'website': "https://www.employee.com",
    'category': 'Employee Portal',
    'version': '13.0.0.4',
    'sequence': '1',
    'application': 'true',
    'depends': ['base', 'custom_payroll', 'ohrms_loan', 'hr', 'website', 'stock', 'hr_payroll',
                'hr_holidays', 'http_routing', 'auth_signup', 'web', 'mail', 'helpdesk_mgmt', 'material_purchase_requisitions'],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_portal_login.xml',
        'views/leaves_portal_templates.xml',
        'views/customer_partner_form.xml',
        # 'views/generic_menu_request.xml',
        'views/travel_requests.xml',
        'views/travel_request_form.xml',

        'views/general_request.xml',
        'views/general_leave_form.xml',
        'views/loan_request.xml',
        'views/tickets_heldesk.xml',
        'views/tickets_helpdesk_emp.xml',
        'reports/student_leaving_report.xml',

        'wizards/action_server_employee_portal.xml',

        'reports/reports.xml',
        'reports/notice_report.xml',
    ],
}
