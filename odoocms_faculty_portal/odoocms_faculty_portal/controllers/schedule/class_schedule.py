from odoo import http
from odoo.http import request
from datetime import date, datetime, timedelta
from .. import main
import calendar
import pdb
import json


class Facultyclassschedule(http.Controller):
    @http.route(['/faculty/class/schedule'], type='http', auth="user", website=True)
    def timetable(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_web.portal_error", values)
            time_slots = ['08:00', '09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-01:00', '01:00-02:00', '02:00-03:00', '03:00-04:00', '04:00-05:00']
            class_ids = request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id)])
            timetable = request.env['odoocms.timetable.schedule'].sudo().get_timetable(False,faculty_staff, values['term'])
            date = datetime.now()
            month = date.strftime("%B")
            week = date.strftime("%w")
            makeup_classes = http.request.env['odoocms.class.attendance'].sudo().search([('faculty_id', '=', faculty_staff.id), ('date_class', '>=', date.today()), ('makeup_class', '=', 'True')])
            timetabledata = []
            for schedule in timetable:
                for day in timetable[schedule]:
                    data = {
                        'day_code': day['day_code'],
                        'code':  str(day['subject_code'])[:35]+'..' if len(day['subject_code']) > 35 else day['subject_code']  ,
                        'c_code': day['subject_code'],
                        'subject_name': str(day['subject_name'])[:35]+'..' if len(day['subject_name']) > 35 else day['subject_name'] ,
                        'c_sub_name': day['subject_name'],
                        'time_from': day['time_from'],
                        'component': day['component'],
                        'time_to': day['time_to'],
                        'room': day['room'],
                        #'makeup_classes': makeup_classes
                    }
                    timetabledata.append(data)
            values.update({
                'active_menu': 'timetable',
                'class_schedule': timetabledata or False,
                'makeup_classes': makeup_classes,
                'class_ids': class_ids,
                'month': month,
                'week' : week,
            })
            return http.request.render('odoocms_faculty_portal.faculty_portal_timetable',values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_web.portal_error', values)

    @http.route(['/faculty/class/create/schedule'], type='http', auth="user", website=True)
    def customClass(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_web.portal_error", values)
            
            class_ids = request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id),('term_id','=',values['config_term'])])
            rooms = request.env['odoocms.room'].sudo().search([])
            values.update({
                'active_menu': 'timetable',
                'faculty_staff': faculty_staff,
                'class_ids': class_ids or False,
                'rooms': rooms,
            })
            return http.request.render('odoocms_faculty_portal.faculty_portal_custom_class_schedule', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_web.portal_error', values)

    @http.route(['/faculty/class/save/schedule'],type='http', method=['POST'], auth="user", website=True, csrf=False)
    def customClassSave(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_web.portal_error", values)

            from_minutes = float(kw.get('fromtime')[-2:])
            from_hours = kw.get('fromtime')[:-3]
            from_time = float(from_hours) + (float(from_minutes) / 60)
            to_minutes = float(kw.get('totime')[-2:])
            to_hours = kw.get('totime')[:-3]
            to_time = float(to_hours) + (float(to_minutes) / 60)
            att_data = {
                'term_id': values['config_term'],
                'class_id': int(kw.get('class_name')),
                'faculty_id': faculty_staff.id,
                'date_schedule': date.today(),
                'date_class': datetime.strptime(kw.get('classdate').replace(".", "/"), '%d/%m/%Y'),
                'time_from': from_time,
                'time_to': to_time,
                'makeup_class': True
            }
            att = http.request.env['odoocms.class.attendance'].sudo().create(att_data)
            att.create_attendance_lines()
            data = {
                'status_is': 'Success',
            }
            data = json.dumps(data)
            return data
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': '/faculty/class/save/schedule',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            data = {
                'status_is': 'Error',
                'error_message': e.args[0] or False,
            }
        data = json.dumps(data)
        return data