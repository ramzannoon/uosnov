from odoo import http
from odoo.http import request
from datetime import date, datetime, timedelta
import pdb


class FacultyAttendance(http.Controller):
    @http.route(['/faculty/class/attendance/page'], type='http', auth="user", website=True)
    def classattendancepage(self, id=0, date_begin=None, date_end=None, sortby=None, **kw):
        company = request.env.user.company_id
        partner = request.env.user.partner_id

        faculty_staff = http.request.env['odoocms.faculty.staff'].sudo().search([('user_partner_id', '=', partner.id)])
        term_ids = http.request.env['odoocms.academic.term'].sudo().search([])
        classes = []
        terms = []
        roaster = []

        for term in term_ids:
            class_id = http.request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id), ('term_id', '=', term.id)])
            if len(class_id)>0:
                for term_class in class_id:
                    attendance_roaster = http.request.env['odoocms.class.attendance'].sudo().search([('class_id','=',term_class.id),('date_class', '<', date.today()),('state', 'in', ('draft', 'done','lock')),('term_id','=',term.id)])
                    if len(attendance_roaster)>0:
                        for att in attendance_roaster:
                            roaster.append({'roaster_id':att.id,'date':att.date_class,'status':att.state,'time_from':att.time_from,'time_to':att.time_to})

                            classes.append({ 'class_name':term_class.name,'class_code':term_class.code,'term_class_id':term_class.id, 'data': roaster})
                            roaster=[]

                terms.append({'name': term.name, 'data':classes})
                classes=[]
        data = terms


        # terms = []
        # classes = []
        # roaster = []
        # for term in term_ids:
        #     class_id = http.request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id), ('term_id', '=', term.id)])
        #
        #     for term_class in class_id:
        #
        #         attendance_roaster = http.request.env['odoocms.class.attendance'].sudo().search([('class_id', '=', term_class.id), ('date_class', '<', date.today())])
        #         for att in attendance_roaster:
        #             roaster.append({'roaster_id': att.id, 'date': att.date_class, 'status': att.state, 'time_from': att.time_from, 'time_to': att.time_to})
        #             classes.append({'class_name': term_class.name, 'class_code': term_class.code, 'term_class_id': term_class.id, 'data': roaster})
        #
        #     terms.append({'name': term.name, 'data': classes})
        # data = terms

        today_classes = http.request.env['odoocms.class.attendance'].sudo().sudo().search([('faculty_id', '=', faculty_staff.id),('date_class','=',date.today())])
        makeup_classes = http.request.env['odoocms.class.attendance'].sudo().sudo().search([('faculty_id', '=', faculty_staff.id),('date_class','>',date.today())])
        #term = http.request.env['odoocms.academic.term'].sudo().search([('faculty_id', '=', faculty_staff.id)])
        #classes = http.request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id)])
        #pre_classes = http.request.env['odoocms.class.attendance'].sudo().search([('faculty_id', '=', faculty_staff.id), ('date_class', '<', date.today()), ('state', 'in', ('draft', 'done','lock'))])
        color = ['md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                 'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400']
        values = {
            'faculty_staff': faculty_staff,
            'today_classes': today_classes or False,
            #'pre_classes': pre_classes,
            # 'rechecking_requests':rechecking_requests,
            'rechecking_requests': False,
            'partner': partner,
            'name': partner.name,
            'prev_classes': data or False,
            'makeup_classes': makeup_classes or False,
            # These are for breadcrumbs
            'active_menu': 'attendance',
            'company': company,
            'color': color
        }
        return request.render("odoocms_faculty_portal.faculty_portal_attendance_classes", values)

    class FacultyAttendance(http.Controller):
        @http.route(['/faculty/class/previous/attendance/classes/id/<int:id>'], type='http', auth="user", website=True)
        def classattendancepage(self, id=0, date_begin=None, date_end=None, sortby=None, **kw):
            company = request.env.user.company_id
            partner = request.env.user.partner_id
            faculty_staff = http.request.env['odoocms.faculty.staff'].sudo().search([('user_partner_id', '=', partner.id)])
            pre_classes = http.request.env['odoocms.class.attendance'].sudo().sudo().search([('faculty_id', '=', faculty_staff.id), ('date_class', '<', date.today()), ('state', 'in', ('draft', 'done'))])
            values = {
                'faculty_staff': faculty_staff,
                'pre_classes': pre_classes,
                # 'rechecking_requests':rechecking_requests,
                'rechecking_requests': False,
                'partner': partner,
                'name': partner.name,
                # These are for breadcrumbs
                'active_menu': 'attendance',
                'company' : company
            }
            return request.render("odoocms_faculty_portal.faculty_portal_previous_attendance_classes", values)

    @http.route(['/faculty/class/attendance/sheet/id/<int:id>'], type='http', auth="user", website=True)
    def dailyattendance2(self, id=0, date_begin=None, date_end=None, sortby=None, **kw):
        company = request.env.user.company_id
        partner = http.request.env.user.partner_id
        faculty_staff = request.env['odoocms.faculty.staff'].sudo().search([('user_partner_id', '=', partner.id)])
        class_ids = request.env['odoocms.class.attendance'].sudo().search([('faculty_id', '=', faculty_staff.id)])
        absent_reason = request.env['odoocms.attendance.absent.reason'].sudo().search([])
        # pdb.set_trace()
        if id != 0:
            domain = [
                ('id', '=', id),
                # ('faculty_id', '=', faculty_staff.id),
                # ('date_class', '=', date.today())
                # ('term_id', '=', values['config_term']),
            ]
            attendance_sheet = request.env['odoocms.class.attendance'].sudo().search(domain)

            if not attendance_sheet:
                values = {
                    'header': 'Error!',
                    'message': 'Nothing Found!',
                }
                return request.render("odoocms_faculty_portal.faculty_error", values)
            attl = []
            for att in attendance_sheet:
                attl.append({'list': att.id})

            #   attendance_sheet.attendance_lines.came_late

            values = {
                'active_menu': 'attendance',
                'faculty_staff': faculty_staff,
                'attendance_sheet': attendance_sheet,
                'company': company,
                'absent_reason': absent_reason,

            }
        # company = request.env.user.company_id
        # partner = http.request.env.user.partner_id
        # faculty_staff = request.env['odoocms.faculty.staff'].sudo().search([('user_partner_id', '=', partner.id)])
        # class_ids = request.env['odoocms.class.attendance'].sudo().search([('faculty_id', '=', faculty_staff.id)])
        # if id != 0:
        #     domain = [
        #         ('id', '=', id),
        #         ('faculty_id', '=', faculty_staff.id),
        #         ('date_class', '=', date.today())
        #         # ('term_id', '=', values['config_term']),
        #     ]
        #     attendance_sheet = request.env['odoocms.class.attendance'].sudo().search(domain)
        #     if not attendance_sheet:
        #         values = {
        #             'header': 'Error!',
        #             'message': 'Nothing Found!',
        #         }
        #         return request.render("odoocms_faculty_portal.faculty_error", values)
        #     values = {
        #             'active_menu':'attendance',
        #             'faculty_staff': faculty_staff,
        #             'attendance_sheet': attendance_sheet,
        #             'company' : company
        #
        #         }
            return request.render("odoocms_faculty_portal.faculty_portal_daily_attendance", values)
    # previous classes roaster
    @http.route(['/faculty/previousclass/attendance/sheet/id/<int:id>'], type='http', auth="user", website=True)
    def dailyattendance(self, id=0, date_begin=None, date_end=None, sortby=None, **kw):
        company = request.env.user.company_id
        partner = http.request.env.user.partner_id
        faculty_staff = request.env['odoocms.faculty.staff'].sudo().search([('user_partner_id', '=', partner.id)])
        class_ids = request.env['odoocms.class.attendance'].sudo().search([('faculty_id', '=', faculty_staff.id)])
        absent_reason = request.env['odoocms.attendance.absent.reason'].sudo().search([])

        if id != 0:
            domain = [
                ('id', '=', id),
                ('faculty_id', '=', faculty_staff.id),
                # ('date_class', '=', date.today())
                # ('term_id', '=', values['config_term']),
            ]
            attendance_sheet = request.env['odoocms.class.attendance'].sudo().search(domain)
            if not attendance_sheet:
                values = {
                    'header': 'Error!',
                    'error_message': 'Nothing Found!',
                }
                return request.render("odoocms_faculty_portal.faculty_error", values)
            attl=[]
            for att in  attendance_sheet:
                attl.append({'list': att.id})

             #   attendance_sheet.attendance_lines.came_late

            values = {
                'active_menu': 'attendance',
                'faculty_staff': faculty_staff,
                'attendance_sheet': attendance_sheet,
                'company' : company,
                'absent_reason':absent_reason,

            }
            return request.render("odoocms_faculty_portal.faculty_portal_daily_attendance", values)
    @http.route(['/faculty/class/attendance/sheet/save'], type='http', method=['POST'], auth="user", website=True, csrf=False)
    def dailyattendanceSheetSave(self, id=0, date_begin=None, date_end=None, sortby=None, **kw):
        try:
            partner = http.request.env.user.partner_id
            faculty_staff = request.env['odoocms.faculty.staff'].sudo().search([('user_partner_id', '=', partner.id)])
            if not faculty_staff:
                return http.request.render('odoocms_faculty_portal.faculty_error')
            attendance_sheet = request.env['odoocms.class.attendance'].sudo().search([('id','=',int(kw.get('attendance_sheet','0'))),('faculty_id', '=', faculty_staff.id)])

            if not attendance_sheet:
                return 'Error'
            for attendance_line in attendance_sheet.attendance_lines:
                key = 'student_att_ch2_'+ str(attendance_line.id)
                remarks = 'student_remarks_'+ str(attendance_line.id)
                earlyleft = 'left_early_'+ str(attendance_line.id)
                camelate = 'came_late_'+ str(attendance_line.id)
                reason = 'student_reason_'+ str(attendance_line.id)
                if kw.get(key,False):
                    attendance_line.present = True if kw.get(key,'False') == 'True' else False
                    attendance_line.came_late = True if kw.get(camelate, 'False') == 'on' else False
                    attendance_line.left_early = True if kw.get(earlyleft, 'False') == 'on' else False
                    attendance_line.remarks = kw.get(remarks)
                if kw.get(reason,False):
                    attendance_line.reason_id = int(kw.get(reason))
            attendance_sheet.attendance_marked()
            return request.redirect('/faculty/previousclass/attendance/sheet/id/' + kw.get('attendance_sheet','0'))
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)