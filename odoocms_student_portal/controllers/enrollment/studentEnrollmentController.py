import pdb
from datetime import date
import json
from odoo import http
from odoo.http import request
from .. import main

class StudentCourses(http.Controller):
    @http.route(['/student/enrolled/courses'], type='http', auth="user", website=True)
    def EnrollCourses(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)

            # survey_input_ids = http.request.env['survey.user_input'].sudo().search([('partner_id', '=', values['partner'].id)])
            # if survey_input_ids:
            #     for survey in survey_input_ids:
            #         if (survey.state == 'new' or survey.state == 'skip') and survey.survey_id.state == 'open':
            #             return request.redirect('/student/qa/feedback')

            color = ['md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                      'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400']

            values.update({
                 'color':color,
            })
            return http.request.render('odoocms_student_portal.student_enrolled_courses', values)
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Enrolled Courses',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/enrollment/cards'], type='http', auth="user", website=True)
    def course_enrollment_cards(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)

            course_registration = http.request.env['odoocms.course.registration'].sudo().search([
                ('student_id', '=', student.id), ('term_id', '=', values['term']['id']),
                ('source', '=', 'portal'), ('state', 'in', ('draft', 'submit'))])

            classes = student.get_portal_classes(values['term'],course_registration)
            enrollment_status = student.batch_id.can_apply('enrollment')


            values.update({
                'classes': classes,
                'course_registration': course_registration,
                'cart': course_registration,
                'enrollment_status': enrollment_status,
            })

            return http.request.render('odoocms_student_portal.student_enrollment_cards', values)
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Enrollment Cards',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/enrollment/cart/save'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def course_enrollment_cards_cart_save(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)

            class_id = int(kw.get('id'))
            course_type = kw.get('course_type')
            course = request.env['odoocms.class.primary'].sudo().browse(class_id)

            registration = http.request.env['odoocms.course.registration'].sudo()
            reg = registration.search([
                ('student_id', '=', student.id), ('term_id', '=', values['term'].id),
                ('source','=','portal'),('state', 'in', ('draft', 'submit'))])

            if not reg:
                reg_data = {
                    'student_id': student.id,
                    'term_id':  values['term'].id,
                    'source': 'portal',
                    'state': 'draft',
                }
                reg = registration.sudo().create(reg_data)
            reg.add_course(course, course_type)
            
            data = {
                'status_is': "Success",
                'message': 'Successfully Added'
            }
            data = json.dumps(data)
            return data
        except Exception as e:
            error_cap = {
                #'student_id': student.id,
                'name': 'Enrollment Cards Save',
                'description': str(e.args[0])[:20] or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(error_cap)
            data = {
                'status_is': "Error",
                'message': str(e.args[0])[:20],
                'color': '#FF0000'
            }
            data = json.dumps(data)
            return data

    @http.route(['/student/enrollment/cart/cancel'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def request_enrollment_cart_cancel(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            req_id = int(kw.get('id'))
            registration = http.request.env['odoocms.course.registration'].sudo()
            reg = registration.search([
                ('student_id', '=', student.id), ('term_id', '=', values['term'].id),
                ('source', '=', 'portal'), ('state', 'in', ('draft', 'submit'))])
            
            line = reg.line_ids.filtered(lambda l: l.id == req_id)
            if line:
                line.sudo().unlink()
            data = {
                'status_is': "Success",
                'color': '#FF0000'
            }
            data = json.dumps(data)
            return data
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Enrollment Card Cancel',
                'description': str(e.args[0]) or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            data = {
                'status_is': "Error",
                'message': e.args[0],
                'color': '#FF0000'
            }
            data = json.dumps(data)
            return data

    @http.route(['/student/enrollment/cart'], type='http', auth="user", website=True)
    def course_enrollment_cart(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)

            course_registration = http.request.env['odoocms.course.registration'].sudo().search([
                ('student_id', '=', student.id), ('term_id','=', values['term'].id),
                ('source', '=', 'portal'), ('state', 'in', ('draft', 'submit'))])

            enrollment_status = student.batch_id.can_apply('enrollment')
            Requested_credits= 0
            registered_credits = 0
            for class_credits in course_registration.line_ids:
                Requested_credits =   Requested_credits + class_credits.credits
            for reg_credits in course_registration.registered_course_ids:
                registered_credits = registered_credits + reg_credits.credits
            registration_load =   http.request.env['odoocms.student.registration.load'].sudo().search([('career_id','=',student.career_id.id)])
            course_registration.action_self_enroll_draft()
            values.update({

                'course_registration': course_registration,
                'enrollment_status': enrollment_status,
                'Total_credits_requested': Requested_credits,
                'registered_credits': registered_credits,
                'percent': round((registered_credits/registration_load.max)*100,2),
                'registration_load':registration_load
            })
            return http.request.render('odoocms_student_portal.student_enrollment_cart', values)
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Enrollment Cart',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/enrollment/confirm'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def course_enrollment_cart_confirm(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)

            if not success:
                return request.render("odoocms_student_portal.student_error", values)


            course_registration = http.request.env['odoocms.course.registration'].sudo().search([
                ('student_id', '=', student.id), ('term_id', '=', values['term'].id),
                ('source', '=', 'portal'), ('state', 'in', ('draft', 'submit'))]).sudo().action_submit()

            #enrollment_status = student.batch_id.can_apply('enrollment')

            data={
                'status_is':'',
            }
            data = json.dumps(data)
            return data
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Enrollment Cart Confirm',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            data = {
                'status_is': "Error",
                'message': str(e.args[0])[:20],
                'color': '#FF0000'
            }
            data = json.dumps(data)
            return data


