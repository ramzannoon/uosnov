from odoo import http
from odoo.http import request
from datetime import date, datetime, timedelta
from . import main
import pdb
import json


class Facultyclassschedule(http.Controller):
    @http.route(['/faculty/class/schedule'], type='http', auth="user", website=True)
    def timetable(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
            time_slots = ['08:00', '09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-01:00', '01:00-02:00', '02:00-03:00', '03:00-04:00', '04:00-05:00']
            class_ids = request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id)])
            timetable = request.env['odoocms.timetable.schedule'].sudo().get_timetable(False,faculty_staff)

            date = datetime.now()
            month = date.strftime("%B")
            week = date.strftime("%w")

            timetabledata = []
            for schedule in timetable:
                for day in timetable[schedule]:
                    data = {
                        'day_code': day['day_code'],
                        'subject':  str(day['subject_code'])[:15]+'..',
                        'subject_name': str(day['subject_name'])[:30]+'..',
                        'time_from': day['time_from'],
                        'component': day['component'],
                        'time_to': day['time_to'],
                        'room': day['room']
                    }
                    timetabledata.append(data)
             
            values.update({
                'active_menu': 'timetable',
                'class_schedule': timetabledata or False,
                'class_ids': class_ids,
                'month': month,
                'week' : week,
            })

            return http.request.render('odoocms_faculty_portal.faculty_portal_timetable',values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)

    @http.route(['/faculty/class/create/schedule'], type='http', auth="user", website=True)
    def customClass(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
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
            return http.request.render('odoocms_faculty_portal.faculty_error', values)

    @http.route(['/faculty/class/save/schedule'],type='http', auth="user", method=['POST'], website=True, csrf=False)
    def customClassSave(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
                
            att_data = {
                'term_id': values['config_term'],
                'class_id': int(kw.get('class_name')),
                'faculty_id': faculty_staff.id,
                'date_schedule': date.today(),
                'date_class': datetime.strptime(kw.get('classdate').replace(".", "/"), '%d/%m/%Y'),
                'time_from': float(kw.get('fromtime').replace(":", "")),
                'time_to': float(kw.get('totime').replace(":", "")),
            }
            att = http.request.env['odoocms.class.attendance'].sudo().create(att_data)
            att.create_attendance_lines()
            data = {}
        except Exception as e:
            data = {
                'status_is': "Error",
                'message': e.args[0],
                'color': '#FF0000'
            }

        data = json.dumps(data)
        return data

