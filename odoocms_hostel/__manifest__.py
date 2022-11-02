{
    'name': 'OdooCMS Hostel',
    'version': '13.0.0.6',
    'summary': """Module For HOSTEL Management""",
    'description': 'Module For HOSTEL Management In University/School',
    'category': 'IDT',
    'sequence': 3,
    'author': 'IDT',
    'company': 'IDT',
    'website': 'http://www.infinitedt.com',
    'depends': ['base', 'mail', 'website', 'odoocms', 'odoocms_fee'],
    'data': [
        'data/data.xml',
        'security/odoocms_hostel_security.xml',
        'security/odoocms_hostel_rules.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'menus/odoocms_hostel_menu.xml',

        'views/odoocms_hostel_general_view.xml',
        'views/odoocms_hostel_room_view.xml',
        'views/odoocms_student_view.xml',


        'views/odoocms_hostel_type_view.xml',
        'views/odoocms_hostel_floor_view.xml',
        'views/odoocms_hostel_view.xml',
        'views/odoocms_hostel_warden_view.xml',

        'views/odoocms_student_hostel_history_view.xml',
        'views/odoocms_student_hostel_swap_view.xml',
        'views/odoocms_faculty_hostel_swap_view.xml',

        'views/odoocms_student_hostel_multi_swap_view.xml',

        'views/odoocms_faculty_view.xml',
        'views/odoocms_faculty_hostel_history_view.xml',
        'views/odoocms_hostel_faculty_special_info_view.xml',

        'wizard/reassignment_students_import_wiz_view.xml',
        'views/odoocms_student_hostel_reassignment_view.xml',
        'views/odoocms_hostel_admission_applications_view.xml',
        'views/odoocms_hostel_visitor_relations_view.xml',
        'views/odoocms_hostel_student_special_info_view.xml',
        'views/odoocms_hostel_extra_facilities_view.xml',

        'wizard/odoocms_hostel_data_import_view.xml',
        'wizard/odoocms_student_hostel_shift_wiz_view.xml',
        'wizard/odoocms_hostel_rooms_deallocation_wiz_view.xml',
        'wizard/odoocms_room_generate_wiz_view.xml',
        'wizard/odoocms_hostel_room_mapping_wiz_view.xml',
        'wizard/odoocms_student_room_assignment_wiz_view.xml',
        'wizard/odoocms_student_room_vacant_wiz_view.xml',

        'wizard/odoocms_student_hostel_data_import_view.xml',
        'wizard/odoocms_hostel_room_bulk_vacant_view.xml',

        'wizard/odoocms_faculty_hostel_shift_wiz_view.xml',
        'wizard/odoocms_faculty_room_assignment_wiz_view.xml',
        'wizard/odoocms_faculty_room_vacant_wiz_view.xml',

        'reports/hostel_summary_report.xml',
        'reports/hostel_student_report.xml',
        'reports/odoocms_students_room_swap_report.xml',
        'reports/odoocms_students_room_shift_report.xml',
        'reports/student_hostel_reassignment_report_view.xml',
        'reports/odoocms_hostel_students_detail_report.xml',

        'data/odoocms_hostel_data.xml',

    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
