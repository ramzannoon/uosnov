from odoo import http
from odoo.http import request
from datetime import date, datetime, timedelta
from .. import main
import pdb

class Studentclassschedule(http.Controller):
    @http.route(['/student/class/schedule'], type='http', auth="user", website=True)
    def studenttimetable(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)

            # survey_input_ids = http.request.env['survey.user_input'].sudo().search([('partner_id', '=', values['partner'].id)])
            # if survey_input_ids:
            #     for survey in survey_input_ids:
            #         if (survey.state == 'new' or survey.state == 'skip') and survey.survey_id.state == 'open':
            #             return request.redirect('/student/qa/feedback')
            timetable = request.env['odoocms.timetable.schedule'].sudo().get_timetable(student,False,False)
            #pp faculty_id._fields   to view all fields
            date = datetime.now()
            month = date.strftime("%B")
            week = date.strftime("%w")
            timetabledata = []
            for schedule in timetable:
                for day in timetable[schedule]:
                    data = {
                        'day_code': day['day_code'],
                        'subject':  str(day['subject_code'])[:35]+'..' if len(day['subject_code']) > 35 else day['subject_code'],
                        'subject_name': str(day['subject_name'])[:35]+'..' if len(day['subject_name']) > 35 else day['subject_name'] ,
                        'component': day['component'],
                        'time_from': day['time_from'],
                        'time_to': day['time_to'],
                        'room': day['room']
                    }
                    timetabledata.append(data)
            roasters = http.request.env['odoocms.class.attendance'].sudo().search([('date_class', '>=', date.today()), ('makeup_class', '=', 'True')])
            makeup_classes = []
            for roaster in roasters:
                classes = roaster.attendance_lines.filtered(lambda l: l.student_id.id == student.id)
                if classes:
                    makeup_classes.append(classes)
            
            values.update({
                'active_menu': 'timetable',
                'class_schedule': timetabledata or False,
                'makeup_classes': makeup_classes or False,
                'month': month,
                'week' : week,
            })
            return http.request.render('odoocms_student_portal.student_portal_timetable',values)
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Class Schedule',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)