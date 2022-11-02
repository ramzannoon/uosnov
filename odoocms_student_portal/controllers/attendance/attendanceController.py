import pdb
from datetime import date
from .. import main
from odoo import http
from odoo.http import request


class StudentAttendance(http.Controller):
    @http.route(['/student/attendance'], type='http', auth="user", website=True)
    def home(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)

            # survey_input_ids = http.request.env['survey.user_input'].sudo().search([('partner_id', '=', values['partner'].id)])
            # if survey_input_ids:
            #     for survey in survey_input_ids:
            #         if (survey.state == 'new' or survey.state == 'skip') and survey.survey_id.state == 'open':
            #             return request.redirect('/student/qa/feedback')
            
            student_subjects = http.request.env['odoocms.student.course'].sudo().search([
                ('student_id', '=', student.id), ('term_id', '=', values['term'].id)])

            color = ['md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400']

            values.update({
                #'term': student.term_id.name,
                'student_subjects': student_subjects,
                'color':color,
            })
            return http.request.render('odoocms_student_portal.student_attendance_class',values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/attendancedetail/id/<int:id>'], type='http', auth="user", website=True)
    def attendancedetail(self, id=0, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            #attendance_req_per = http.request.env['ir.config_parameter'].sudo().get_param('odoocms_attendance.attendance_req_per')
            #attendance_req_per = eval(attendance_req_per) or 75
            #odoocms.class.primary
            student_course = http.request.env['odoocms.student.course'].sudo().search([('student_id', '=', student.id), ('primary_class_id', '=', id)])

            if id != 0:
                attendance_classlist=[]
                attendance_class_single=[]

                student_subjects = http.request.env['odoocms.student.course.component'].sudo().search([('student_course_id', '=', student_course.id)])
                if len(student_subjects) >1 :
                    for sub in student_subjects:
                        attendance_class = request.env['odoocms.class.attendance.line'].sudo().search([('student_course_component_id', '=', sub.id),('state','in',('done','lock'))])
                        attendance_class = attendance_class.filtered(lambda l: l.student_id == student)
                        attendance_classlist.append(attendance_class)
                if len(student_subjects) <= 1 :
                    for sub in student_subjects:
                        attendance_class_single = request.env['odoocms.class.attendance.line'].sudo().search([('student_course_component_id', '=', sub.id),('state','in',('done','lock'))])
                        attendance_class_single = attendance_class_single.filtered(lambda l: l.student_id == student)

                # student_course.component_ids[0].class_id
                # student_course.component_ids[0].attendance_percentage
                # student_course.component_ids[0].student_course_component_id
                #student_course.component_ids[1].class_id.registration_component_ids
                if not student_course or len(student_course) == 0:
                    values = {
                        'header': 'Error!',
                        'message': 'Attendance not added yet!',
                        'error_message': 'Attendance not added yet!',
                    }
                    return request.render("odoocms_student_portal.student_error", values)
                # if not attendance_class or len(attendance_class) == 0:
                #     values = {
                #         'header': 'Error!',
                #         'message': 'Attendance not added yet!',
                #
                #     }
                #
                #     return request.render("odoocms_student_portal.student_error", values)
                
                values.update({
                    'student_course': student_course,
                    'attendance_classlist': student_subjects,
                    'attendance_classes': attendance_classlist,
                    'attendance_class': attendance_class_single or False,
                    'present': len(attendance_class_single.filtered(lambda l: l.present == True)) or False if len(attendance_class_single) > 0 else False,
                    'present2': len(attendance_classlist[0].filtered(lambda l: l.present == True)) or False if len(attendance_classlist) > 0 else False,
                    'present3': len(attendance_classlist[1].filtered(lambda l: l.present == True)) or False if len(attendance_classlist) > 0 else False,
                    'total_att_single': len(attendance_class_single) or False if len(attendance_class_single) > 0 else False,
                    'total_att_2': len(attendance_classlist[0]) or False if len(attendance_classlist) > 0 else False,
                    'total_att_3': len(attendance_classlist[1]) or False if len(attendance_classlist) > 0 else False,
                    # 'total_att': len(attendance_class),
                    # 'percentage': student_subjects.attendance_percentage,
                    # 'attendance_req_per': attendance_req_per,

                })
            return http.request.render('odoocms_student_portal.student_attendance_class_detail', values)
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'attendance',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)