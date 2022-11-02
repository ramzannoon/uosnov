
{
    "name": "OdooCMS Timetable",
    'version': '12.0',
    'license': 'LGPL-3',
    'category': 'OdooCMS',
    'sequence': 3,
    'summary': "Timetable Management Module of OdooCMS""",
    'author': 'GlobalXS',
    'company': 'GlobalXS Technology Solutions',
    'website': "http://www.globalxs.co",
    'depends': ['odoocms_registration'],
    'data': [
        'security/ir.model.access.csv',
        'views/timetable_menu_view.xml',
        
         'views/time_pattern.xml',
         'views/date_pattern.xml',
         # 'views/res_config_setting_view.xml',

         # 'views/timetable_view.xml',
         'views/timetable_schedule_view.xml',

        # 'wizard/sync_unitime_view.xml',
        # 'wizard/student_time_table_wiz_view.xml',
        #
        # 'reports/report.xml',
        # 'reports/student_time_table_report.xml',

        

    ],

    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
