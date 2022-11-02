from odoo import http
from odoo.http import request
from datetime import date, datetime, timedelta
from .. import main
import calendar
import pdb


class FacultyAttendance(http.Controller):
    @http.route(['/faculty/class/attendance/page'], type='http', auth="user", website=True, csrf=True)
    def class_attendance_page(self, id=0, date_begin=None, date_end=None, sortby=None, **kw):
        values, success, faculty_staff = main.prepare_portal_values(request)
        if not success:
            return request.render("odoocms_web.portal_error", values)
        config_term = http.request.env['ir.config_parameter'].sudo().get_param('odoocms.attendance_visible')
        if config_term == 'False':
                values.update({
                    'error_head': 'Access Denied',
                    'error_message': 'Access to page is restricted by admin. The attendance is locked',
                 })
                return request.render("odoocms_web.portal_error", values)
        term_ids = http.request.env['odoocms.academic.term'].sudo().search([])
        term_ids = term_ids.sorted(key=lambda r: r.id, reverse=True)
        faculty_classes = http.request.env['odoocms.class'].sudo()
        terms = []
        for term in term_ids:
            faculty_classes_primary = http.request.env['odoocms.class.faculty'].sudo().search([
                ('faculty_staff_id', '=', faculty_staff.id), ('term_id', '=', term.id), ('role_id.code', '=', 'Primary')
            ])
            faculty_classes_secondary = http.request.env['odoocms.class.faculty'].sudo().search([
                ('faculty_staff_id', '=', faculty_staff.id), ('term_id', '=', term.id), ('role_id.code', '=', 'Secondary'), ('class_id.allow_secondary_staff', '=', True)
            ])
            # class_ids= http.request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id), ('term_id', '=', term.id)])
            class_ids = (faculty_classes_primary + faculty_classes_secondary).mapped('class_id')
            faculty_classes += class_ids
            
            if len(class_ids) > 0:
                classes = []
                for term_class in class_ids:
                    attendance_roaster = http.request.env['odoocms.class.attendance'].sudo().search([
                        ('class_id','=',term_class.id),('date_class', '<', date.today()),('state', 'in', ('draft', 'done','lock')),('term_id','=',term.id)
                    ])
                    attendance_roaster = attendance_roaster.sorted(key=lambda r: r.date_class, reverse=True)
                    roaster = []
                    for att in attendance_roaster:

                        roaster.append({'roaster_id':att.id,'date':att.date_class, 'day': calendar.day_name[att.date_class.weekday()], 'status':att.state, 'marked': att.att_marked ,'makeup_class': att.makeup_class, 'time_from':att.time_from,'time_to':att.time_to})
                    classes.append({ 'class_name':term_class.name,'class_code':term_class.code,'term_class_id':term_class.id, 'data': roaster})
                terms.append({'name': term.name, 'data':classes})

        data = terms
        today_classes = http.request.env['odoocms.class.attendance'].sudo().search([('class_id', 'in', faculty_classes.ids), ('date_class', '=', date.today())])

        # total_roasters = http.request.env['odoocms.class.attendance'].sudo().search([('faculty_id', '=', faculty_staff.id), ('term_id', '=', values['config_term'])])
        makeup_classes = http.request.env['odoocms.class.attendance'].sudo().search([('class_id', 'in', faculty_classes.ids), ('date_class', '>=', date.today()), ('makeup_class', '=', 'True')])

        # summary
        summary=[]
        class_ids = http.request.env['odoocms.class'].sudo().search([('id', 'in', faculty_classes.ids), ('term_id', '=', values['config_term'])])
        if len(class_ids) > 0:
            classes = []
            for term_class in class_ids:
                attendance_roaster = http.request.env['odoocms.class.attendance'].sudo().search([
                    ('class_id', '=', term_class.id), ('date_class', '<', date.today()), ('state', 'in', ('draft', 'done', 'lock')), ('term_id', '=', values['config_term'])
                ])
                attendance_roaster = attendance_roaster.sorted(key=lambda r: r.date_class, reverse=True)
                roaster = []
                for att in attendance_roaster:
                    roaster.append({'roaster_id': att.id, 'date': att.date_class, 'day': calendar.day_name[att.date_class.weekday()], 'status': att.state, 'marked': att.att_marked, 'time_from': att.time_from, 'time_to': att.time_to})
                classes.append({'class_name': term_class.name, 'class_code': term_class.code, 'term_class_id': term_class.id, 'data': roaster})
            summary.append({'name': term.name, 'data': classes})

        values.update({
            'today_classes': today_classes or False,
            'rechecking_requests': False,
            'prev_classes': data or False,
            'makeup_classes': makeup_classes or False,
            # These are for breadcrumbs
            'active_menu': 'attendance',

        })
        return request.render("odoocms_faculty_portal.faculty_portal_attendance_classes", values)

    @http.route(['/faculty/class/attendance/sheet/id/<int:id>'], type='http', auth="user", website=True)
    def daily_attendance_sheet(self, id=0, date_begin=None, date_end=None, sortby=None, **kw):

        values, success, faculty_staff = main.prepare_portal_values(request)

        if not success:
            return request.render("odoocms_web.portal_error", values)
        
        absent_reason = request.env['odoocms.attendance.absent.reason'].sudo().search([])
        if id != 0:
            domain = [
                ('id', '=', id),
            ]
            attendance_sheet = request.env['odoocms.class.attendance'].sudo().search(domain)
            if attendance_sheet and attendance_sheet.faculty_id.id != faculty_staff.id:
                if faculty_staff.id not in attendance_sheet.class_id.faculty_ids.mapped('faculty_staff_id').ids:
                    attendance_sheet = False
                    
            if not attendance_sheet:
                values = {
                    'header': 'Error!',
                    'error_message': 'Attendance sheet not found!',
                }
                return request.render("odoocms_web.portal_error", values)

            values.update({
                'active_menu': 'attendance',
                'attendance_sheet': attendance_sheet,
                'absent_reason': absent_reason,
            })
            return request.render("odoocms_faculty_portal.faculty_portal_daily_attendance", values)
    
    # previous classes roaster Not in use
    @http.route(['/faculty/previousclass/attendance/sheet/id/<int:id>'], type='http', auth="user", website=True)
    def daily_attendance(self, id=0, date_begin=None, date_end=None, sortby=None, **kw):
        values, success, faculty_staff = main.prepare_portal_values(request)
        if not success:
            return request.render("odoocms_web.portal_error", values)

        # Absent reasons implementation
        absent_reason = request.env['odoocms.attendance.absent.reason'].sudo().search([])

        # Next and previous button implementation
        term_ids = http.request.env['odoocms.academic.term'].sudo().search([])
        term_ids = term_ids.sorted(key=lambda r: r.id, reverse=True)
        faculty_classes = http.request.env['odoocms.class'].sudo()
        terms = []
        roster=[]
        for term in term_ids:
            faculty_classes_primary = http.request.env['odoocms.class.faculty'].sudo().search([
                ('faculty_staff_id', '=', faculty_staff.id), ('term_id', '=', term.id), ('role_id.code', '=', 'Primary')
            ])
            faculty_classes_secondary = http.request.env['odoocms.class.faculty'].sudo().search([
                ('faculty_staff_id', '=', faculty_staff.id), ('term_id', '=', term.id), ('role_id.code', 'in', ('Primary', 'Secondary')), ('class_id.allow_secondary_staff', '=', True)
            ])
            # class_ids= http.request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id), ('term_id', '=', term.id)])
            class_ids = (faculty_classes_primary + faculty_classes_secondary).mapped('class_id')
            faculty_classes += class_ids
            
            class_ids = http.request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id), ('term_id', '=', term.id)])
            if len(class_ids) > 0:
                classes = []
                for term_class in class_ids:
                    attendance_roaster = http.request.env['odoocms.class.attendance'].sudo().search([
                        ('class_id', '=', term_class.id), ('date_class', '<', date.today()), ('state', 'in', ('draft', 'done', 'lock')), ('term_id', '=', term.id)
                    ])
                    attendance_roaster = attendance_roaster.sorted(key=lambda r: r.date_class, reverse=True)

                    roaster = []
                    for att in attendance_roaster:
                        roster.append(att)
        data = roster

        # Next and previous button implementation End

        if id != 0:
            domain = [
                ('id', '=', id),
            ]
            attendance_sheet = request.env['odoocms.class.attendance'].sudo().search(domain)
            if attendance_sheet and attendance_sheet.faculty_id.id != faculty_staff.id:
                if faculty_staff.id not in attendance_sheet.class_id.faculty_ids.mapped('faculty_staff_id').ids:
                    attendance_sheet = False
                    
            if not attendance_sheet:
                values = {
                    'header': 'Error!',
                    'error_message': 'Nothing Found!',
                }
                return request.render("odoocms_web.portal_error", values)

            values.update({
                'active_menu': 'attendance',
                'attendance_sheet': attendance_sheet,
                'absent_reason':absent_reason,
                'rosters': data,
            })
            return request.render("odoocms_faculty_portal.faculty_portal_daily_attendance", values)
    
    @http.route(['/faculty/class/attendance/sheet/save'], type='http', method=['POST','GET'], auth="user", website=True, csrf=False)
    def daily_attendance_sheet_save(self, id=0, date_begin=None, date_end=None, sortby=None, **kw):
        try:

            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_web.portal_error", values)
            absent_reason = request.env['odoocms.attendance.absent.reason'].sudo().search([])
            attendance_sheet = request.env['odoocms.class.attendance'].sudo().search([('id', '=', int(kw.get('attendance_sheet', '0')))])
            if attendance_sheet and attendance_sheet.faculty_id.id != faculty_staff.id:
                if faculty_staff.id not in attendance_sheet.class_id.faculty_ids.mapped('faculty_staff_id').ids:
                    attendance_sheet = False

            if not attendance_sheet:
                values = {
                    'error_message': 'Attendance sheet not found.',
                }
                return request.render("odoocms_web.portal_error", values)

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

                if kw.get(reason):
                    ab_reason = kw.get(reason)
                    for reason in absent_reason:
                        if reason.code == ab_reason if ab_reason != '' else False:
                            attendance_line.reason_id = reason.id or False
                elif kw.get(reason) == '':
                    for reason in absent_reason:
                        if reason.code == '02':
                            attendance_line.reason_id = reason.id
                else:
                    attendance_line.reason_id =  False
            attendance_sheet.attendance_marked()
            return request.redirect('/faculty/previousclass/attendance/sheet/id/' + kw.get('attendance_sheet','0'))
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_web.portal_error', values)