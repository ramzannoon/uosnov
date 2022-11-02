import json
import pdb
from datetime import date
import datetime
from odoo import http
from odoo.http import request
from .. import main

class studentrequests(http.Controller):
    @http.route(['/student/project/request'], type='http', auth="user", website=True)
    def studentprojectRequest(self, **kw):
    
        values, success, student = main.prepare_portal_values(request)
        if not success:
            return request.render("odoocms_student_portal.student_error", values)
        
        student_project = request.env['odoocms.student.project'].sudo().search([('student_ids', '=', student.id)])
        
        values.update({
            'projects': student_project,
        })
        return http.request.render('odoocms_student_portal.student_project_request', values)

    @http.route(['/student/retest'], type='http', auth="user", website=True)
    def retestRequest(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)

            requests = http.request.env['odoocms.student.course.retest'].sudo().search([('student_id', '=', student.id)])

            values.update({
                'retest_request': requests,
            })
            return http.request.render('odoocms_student_portal.student_retest_request', values)
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'retest',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/retest/req/save'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def retestRequestSave(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)

            reg_id = int(kw.get('retest_course'))
            reason = kw.get('reason')

            data = {
                'student_id': student.id,
                'reason': reason,
                'registration_id': reg_id,
                'state': 'submit',
            }
            request.env['odoocms.student.course.retest'].sudo().create(data)
            return request.redirect('/student/retest')
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Retest save',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/retest/req/cancel'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def retestRequestCancel(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            id = kw.get('id')
            request.env['odoocms.student.course.retest'].sudo().search([('student_id', '=', student.id), ('id', '=', id)]).unlink()
            data = {
                'student_id': student.id,
            }
            
        except Exception as e:
            data = {
                'message': e or False
            }
        data = json.dumps(data)
        return data

    @http.route(['/student/igrade'], type='http', auth="user", website=True)
    def igradeRequest(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)

            requests = http.request.env['odoocms.student.course.incomplete'].sudo().search([('student_id', '=', student.id)])

            values.update({
                'igrade_request':requests,
            })
            return http.request.render('odoocms_student_portal.student_igrade_request', values)
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Igrade',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/igrade/req/save'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def igradeRequestSave(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            reg_id = int(kw.get('igrade_course'))
            reason = kw.get('reason')
            registration = request.env['odoocms.student.course'].sudo().browse(reg_id)
            data = {
                'student_id': student.id,
                'reason': reason,
                'registration_id': reg_id,
                'term_id': registration.term_id.id,
                'state': 'submit',
            }
            request.env['odoocms.student.course.incomplete'].sudo().create(data)
            return request.redirect('/student/igrade')
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Igrade Save',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)
    
    @http.route(['/student/igrade/req/cancel'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def iGradeCancel(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            id = kw.get('id')
            request.env['odoocms.student.course.incomplete'].sudo().search([('student_id', '=', student.id), ('id', '=', id)]).unlink()
            data = {
                'student_id': student.id,
            }
            
        except Exception as e:
            data = {
                'message': e or False
            }
        data = json.dumps(data)
        return data

    @http.route(['/student/degree'], type='http', auth="user", website=True)
    def studentDegReq(self):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            requests = http.request.env['odoocms.student.degree'].sudo().search([('student_id', '=', student.id)])
            
            values.update({
                'degree_request': requests,
                'name': student.name,
            })
            return http.request.render('odoocms_student_portal.student_degree_request', values)
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Final Degree',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/degree/save'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def degreeRequestSave(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)

            data = {
                'student_id': student.id,
                'state': 'submit',
            }
            request.env['odoocms.student.degree'].sudo().create(data)
            return request.redirect('/student/degree')
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Final Degree Save',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/degree/req/cancel'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def degreeRequestCancel(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            id = kw.get('id')
            request.env['odoocms.student.degree'].sudo().search([('student_id', '=', student.id),('id','=',id)]).unlink()
            data = {
                'status_is': '',
            }
            
        except Exception as e:
            data = {
                'message': e or False
            }
        data = json.dumps(data)
        return data

    @http.route(['/student/transcript'], type='http', auth="user", website=True)
    def transcriptRequest(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            requests = http.request.env['odoocms.student.transcript'].sudo().search([('student_id', '=', student.id)])
            term_ids = http.request.env['odoocms.student.term'].sudo().search([('student_id', '=', student.id)])

            values.update({
                'transcript_request': requests,
                'name': student.name,
                'term_ids': term_ids
            })
            return http.request.render('odoocms_student_portal.student_transcript_request', values)
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Transcript',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/transcript/req/save'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def transcriptRequestSave(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            data = {
                'student_id': student.id,
                'state': 'submit',
            }
            request.env['odoocms.student.transcript'].sudo().create(data)
            return request.redirect('/student/transcript')
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Transcript Save',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/transcript/req/cancel'],  type='http', auth="user", website=True, method=['POST'], csrf=False)
    def transcriptRequestCancel(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            id = kw.get('id')
            request.env['odoocms.student.transcript'].sudo().search([('student_id', '=', student.id),('id','=',id)]).unlink()
            data = {
                'student_id': student.id,
            }
            
        except Exception as e:
            data = {
                'message': e or False
            }
        data = json.dumps(data)
        return data

    @http.route(['/student/coursedrop'], type='http', auth="user", website=True)
    def courseDropRequest(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)

            classes = student.get_possible_classes(student.term_id,portal=True)
            drop_ids = request.env['odoocms.student.course.drop'].sudo().search([('student_id', '=', student.id), ('state', 'in', ('draft', 'submit'))])

            registration_ids = http.request.env['odoocms.student.course'].sudo().search([('student_id', '=', student.id), ('state', 'in', ('current','draft'))])
            drop_reason = http.request.env['odoocms.drop.reason'].sudo().search([])

            # registered_class_ids = rec.student_id.enrolled_course_ids.filtered(
            #     lambda l: l.term_id.id == rec.term_id.id).mapped('primary_class_id')
            result =[]

            if drop_ids:
                for rec in drop_ids:
                    if not result:
                        #result = registration_ids.filtered(lambda crs: crs.id != rec.registration_id.id)
                        result = http.request.env['odoocms.student.course'].sudo().search([('student_id', '=', student.id), ('state', 'in', ('current', 'draft')),('id','!=',rec.registration_id.id)])
                    else:
                        result = result.filtered(lambda crs: crs.id != rec.registration_id.id)

            if not registration_ids:
                print('errors')
            
            values.update({
                'classes': classes or False,
                'registration_ids': result if result else registration_ids,
                'droprequests' : drop_ids or False,
                'reasons': drop_reason,
            })
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Course Drop',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values={
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error',values)
        return http.request.render('odoocms_student_portal.student_coursedrop_request',values)

    @http.route(['/student/coursedrop/save'], type='http', auth="user", website=True, method=['GET','POST'], csrf=False)
    def courseDropRequestSave(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
    
            course_id = int(kw.get('drop_course'))
            reason = int(kw.get('drop_reason'))
            desc = kw.get('drop_description')
            
            data = {
                'student_id': student.id,
                'registration_id': course_id,
                'description': desc,
                'reason_id': reason,
                'state': 'submit',
            }
            request.env['odoocms.student.course.drop'].sudo().create(data)
            return request.redirect('/student/coursedrop')
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Course Drop Save',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/coursedrop/cancel'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def courseDropRequestCancel(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            req_id = int(kw.get('id'))
            drop_id = request.env['odoocms.student.course.drop'].sudo().search([('student_id','=',student.id ),('id','=',req_id)])
            drop_id.unlink()

            data = {}
            
        except Exception as e:
            data = {
                'status_is': "Error",
                'message': e.args[0],
                'color': '#FF0000'
            }
        data = json.dumps(data)
        return data

    @http.route(['/student/termdefer'], type='http', auth="user", website=True)
    def termdeferRequest(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            terms = request.env['odoocms.academic.term'].sudo().search([])
            requests = request.env['odoocms.student.term.defer'].sudo().search([('student_id', '=', student.id)])

            values.update({
                'student_requests': requests,
                'all_terms': terms,
            })
            return http.request.render('odoocms_student_portal.student_termdefer_request', values)
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Term Defer',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/term/defer/request/save'], type='http', method=['POST'],  auth="user",website=True,csrf=False)
    def StudenttermdeferRequestSave(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            reason = kw.get('reason')
            term_id = int(kw.get('dropDown_term'))

            requestsTermDefer = request.env['odoocms.student.term.defer'].sudo().search([])

            insertvalues = {
                'student_id': student.id,
                'reason': reason,
                'term_id': term_id,
                'state': 'submit',
            }
            requestsTermDefer.sudo().create(insertvalues)
            return request.redirect('/student/termdefer')
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Term Defer Save',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/term/defer/request/cancel'], type='http', method=['POST'], auth="user", website=True, csrf=False)
    def StudenttermdeferRequestCancel(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            reqid = kw.get('id')
            requestsTermDefer = request.env['odoocms.student.term.defer'].sudo().search([('student_id', '=', student.id), ('id', '=', reqid)])
            requestsTermDefer.sudo().unlink()
            data = {}
            
        except Exception as e:
            data = {
                'status_is': "Error",
                'message': e.args[0],
                'color': '#FF0000'
            }
        data = json.dumps(data)
        return data


    @http.route(['/student/semester/resume'], type='http', auth="user", website=True)
    def semesterresumeRequest(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            requestsTermResume = request.env['odoocms.student.term.resume'].sudo().search([('student_id', '=', student.id)])

            values.update({
                'student_requests': requestsTermResume,

            })
            return http.request.render('odoocms_student_portal.student_term_resume_request', values)
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Semester Resume',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/term/resume/save'], type='http', method=['POST'],  auth="user",website=True,csrf=False)
    def semesterresumeRequestSave(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            requestsTermResume = request.env['odoocms.student.term.resume'].sudo().search([])
            insertvalues = {
                'student_id': student.id,
                'state': 'submit',
            }
            requestsTermResume.sudo().create(insertvalues)
            values.update({
                'requestsTermResume': requestsTermResume,
            })
            return request.redirect('/student/semester/resume')
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Term Resume Save',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/term/resume/request/cancel'], type='http', method=['POST'], auth="user", website=True, csrf=False)
    def StudenttermresumeRequestCancel(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            reqid = kw.get('id')
            requestsTermResume = request.env['odoocms.student.term.resume'].sudo().search([('student_id', '=', student.id), ('id', '=', reqid)])
            requestsTermResume.sudo().unlink()

            data = {}
            
        except Exception as e:
            data = {
                'status_is': "Error",
                'message': e.args[0],
                'color': '#FF0000'
            }
        data = json.dumps(data)
        return data

    @http.route(['/student/leave'], type='http', auth="user", website=True)
    def leaveRequest(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
           
            return http.request.render('odoocms_student_portal.student_leave_request', values)
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Leave',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/profileupdate'], type='http', auth="user", website=True)
    def profileupdate(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            return http.request.render('odoocms_student_portal.student_profileupdate_request', values)
        except:
            return http.request.render('odoocms_student_portal.student_error')

    @http.route(['/student/enrollment'], type='http', auth="user", website=True)
    def course_enrollment(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            classes = student.get_possible_classes(student.term_id,portal=True)
            course_registration = http.request.env['odoocms.course.registration'].sudo().search([('student_id', '=', student.id), ('state', 'in', ('draft', 'submit'))])
            enrollment_status = student.batch_id.can_apply('enrollment')
            
            values.update({
                'classes': classes,
                'course_registration': course_registration,
                'enrollment_status': enrollment_status,
            })
            return http.request.render('odoocms_student_portal.student_enrollment', values)
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Enrollment',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/request/enrollment/save'], type='http', auth="user", website=True, method=['GET', 'POST'], csrf=False)
    def request_enrollment_save(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            comp_class_ids = request.httprequest.form.getlist('comp_class_ids')
            elec_class_ids = request.httprequest.form.getlist('elec_class_ids')
            additional_class_ids = request.httprequest.form.getlist('additional_class_ids')
            repeat_class_ids = request.httprequest.form.getlist('repeat_class_ids')
            alternate_class_ids = request.httprequest.form.getlist('alternate_class_ids')
            minor_class_ids = request.httprequest.form.getlist('minor_class_ids')


            course_registration = http.request.env['odoocms.course.registration'].sudo().search([('student_id', '=', student.id), ('term_id', '=', student.term_id.id), ('state', 'in', ('draft', 'submit'))])
            values = {}
            if comp_class_ids and len(comp_class_ids) > 0:
                comp_class_ids = request.env['odoocms.class.primary'].sudo().search([('id','in',list(map(int, comp_class_ids)))])
                comp_class_ids += course_registration.compulsory_course_ids
                if comp_class_ids:
                    values['compulsory_course_ids'] = [(6, 0, comp_class_ids.ids)]

            if elec_class_ids and len(elec_class_ids) > 0:
                elec_class_ids = request.env['odoocms.class.primary'].sudo().search([('id','in',list(map(int, elec_class_ids)))])
                elec_class_ids += course_registration.elective_course_ids
                if elec_class_ids:
                    values['elective_course_ids'] = [(6, 0, elec_class_ids.ids)]

            if additional_class_ids and len(additional_class_ids) > 0:
                additional_class_ids = request.env['odoocms.class.primary'].sudo().search([('id','in',list(map(int, additional_class_ids)))])
                additional_class_ids += course_registration.additional_course_ids
                if additional_class_ids:
                    values['additional_course_ids'] = [(6, 0, additional_class_ids.ids)]

            if repeat_class_ids and len(repeat_class_ids) > 0:
                repeat_class_ids = request.env['odoocms.class.primary'].sudo().search([('id','in',list(map(int, repeat_class_ids)))])
                repeat_class_ids += course_registration.repeat_course_ids
                if repeat_class_ids:
                    values['repeat_course_ids'] = [(6, 0, repeat_class_ids.ids)]


            if alternate_class_ids and len(alternate_class_ids) > 0:
                alternate_class_ids = request.env['odoocms.class.primary'].sudo().search([('id', 'in', list(map(int, alternate_class_ids)))])
                alternate_class_ids += course_registration.alternate_course_ids
                if alternate_class_ids:
                    values['alternate_course_ids'] = [(6, 0, alternate_class_ids.ids)]


            if minor_class_ids and len(minor_class_ids) > 0:
                minor_class_ids = request.env['odoocms.class.primary'].sudo().search([('id', 'in', list(map(int, minor_class_ids)))])
                minor_class_ids += course_registration.minor_course_ids
                if minor_class_ids:
                    values['minor_course_ids'] = [(6, 0, minor_class_ids.ids)]

            if course_registration:
                course_registration.sudo().write(values)
            else:
                values['student_id'] = student.id
                values['term_id'] = student.term_id.id
                values['state'] = 'submit'
                course_registration.sudo().create(values)
            return request.redirect('/student/enrollment')
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Enrollment Save',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/enrollment/cancel'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def request_enrollment_cancel(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            req_id = int(kw.get('id'))
            course_type = kw.get('course_type')
            course_id = int(kw.get('course'))
            
            student_registration = request.env['odoocms.course.registration'].sudo().search([('student_id', '=', student.id), ('id', '=', req_id)])

            if course_type == 'compulsory':
                rec = student_registration.compulsory_course_ids.filtered(lambda l: l.id == course_id)
                if rec:
                    student_registration.write({'compulsory_course_ids': [(3, rec.id)]})
            elif course_type == 'elective':
                rec = student_registration.elective_course_ids.filtered(lambda l: l.id == course_id)
                if rec:
                    student_registration.write({'elective_course_ids': [(3, rec.id)]})
            elif course_type == 'additional':
                rec = student_registration.additional_course_ids.filtered(lambda l: l.id == course_id)
                if rec:
                    student_registration.write({'additional_course_ids': [(3, rec.id)]})
            elif course_type == 'repeat':
                rec = student_registration.repeat_course_ids.filtered(lambda l: l.id == course_id)
                if rec:
                    student_registration.write({'repeat_course_ids': [(3, rec.id)]})
            elif course_type == 'alternate':
                rec = student_registration.alternate_course_ids.filtered(lambda l: l.id == course_id)
                if rec:
                    student_registration.write({'alternate_course_ids': [(3, rec.id)]})
            elif course_type == 'minor':
                rec = student_registration.minor_course_ids.filtered(lambda l: l.id == course_id)
                if rec:
                    student_registration.write({'minor_course_ids': [(3, rec.id)]})
            data = {}
            
        except Exception as e:
            data = {
                'status_is': "Error",
                'message': e.args[0],
                'color': '#FF0000'
            }
        data = json.dumps(data)
        return data

    @http.route(['/student/request/alternate/course'], type='http', auth="user", website=True, method=['GET'])
    def course_enrollment_alternate(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            alternate_course_requests = request.env['odoocms.student.course.alternate'].sudo().search([('student_id', '=', student.id)])
            # curent_courses = http.request.env['odoocms.student.course.alternate'].sudo().search([()])
            grade_courses, rep_courses, alternate_courses = http.request.env['odoocms.student.course.alternate'].sudo()._get_domain(student)

            values.update({
                'grade_courses': grade_courses,
                'rep_courses': rep_courses,
                'alternate_courses': alternate_courses,
                'alternate_course_requests': alternate_course_requests,
            })
            return http.request.render('odoocms_student_portal.student_enrollment_alternative', values)
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Alternate Course',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/request/alternate/course/save'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def course_request_alternate_save(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            course_type = kw.get('course_type')
            grade_course = kw.get('grade_course')
            scheme_course = kw.get('scheme_course')
            # alter_course = kw.get('alter_course')
            # alter_description= kw.get('alter_description')

            if course_type == 'scheme':
                alternate_course_id = request.env['odoocms.student.course.alternate'].sudo().search([])
                values={
                    'student_id': student.id,
                    'type': course_type,
                    'course_id': int(scheme_course),
                    'alternate_course_id': kw.get('alter_course') or False,
                    'reason': kw.get('alter_description'),
                    'state': 'submit',
                }
                alternate_course_id.sudo().create(values)
            elif course_type == 'grade':
                alternate_course_id = request.env['odoocms.student.course.alternate'].sudo().search([])
                values = {
                    'student_id': student.id,
                    'type': course_type,
                    'registration_id': int(grade_course),
                    'alternate_course_id': kw.get('alter_course') or False,
                    'reason': kw.get('alter_description'),
                    'state': 'submit',
                }
                alternate_course_id.sudo().create(values)
           
            return request.redirect('/student/request/alternate/course/')
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Alternate Course Save',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/request/alternate/course/delete'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def course_enrollment_alternate_save(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            id= kw.get('id')
            # alter_course = kw.get('alter_course')
            # alter_description= kw.get('alter_description')

            request.env['odoocms.student.course.alternate'].sudo().search([('student_id', '=', student.id),('id','=',id)]).unlink()

            data  = {}
            #alternate_course_id.sudo().create(values)
            
        except Exception as e:
            data = {
                'error_message': e or False
            }
            data = json.dumps(data)
            return data

    @http.route(['/student/enrollment/schedule'], type='http', auth="user", website=True)
    def course_enrollment_schedule(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)

            student_subjects = http.request.env['odoocms.student.course'].sudo().search([(
                'student_id', '=', student.id), ('term_id', '=', values['term'].id)])

            term_planning = request.env['odoocms.academic.term.planning'].sudo().search([])

            values.update({
                'term_planning':term_planning,
            })


            return http.request.render('odoocms_student_portal.student_enrollment_schedule', values)
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Enrollment Schedule',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)


    @http.route(['/student/clearance'], type='http', auth="user", website=True)
    def studentClearanceReq(self):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)

            requests = http.request.env['odoocms.student.clearance'].sudo().search([('student_id', '=', student.id)])
            approval_requests = ''
            approval_dd_requests = ''
            text = ''
            if requests:
                if len(http.request.env['approval.request'].sudo().search(
                        [('clearance_form_id.student_id', '=', student.id)])) == 1:
                    approval_requests = http.request.env['approval.request'].sudo().search(
                        [('clearance_form_id.student_id', '=', student.id)])[0]

                    # http.request.env['odoocms.faculty.staff'].sudo().search([('id','=','approval_requests.user_id.id')])  #
                    http.request.env['odoocms.faculty.staff'].sudo().search([])  #

                if len(http.request.env['approval.request'].sudo().search(
                        [('clearance_form_id.student_id', '=', student.id)])) > 1:
                    approval_requests = http.request.env['approval.request'].sudo().search(
                        [('clearance_form_id.student_id', '=', student.id)])[1]
                    # remarks = approval_requests.user_remarks

                    # approval_requests.user_remarks = "".join([s for s in remarks.splitlines(True) if s.strip()])

                    approval_dd_requests = http.request.env['approval.request'].sudo().search(
                        [('clearance_form_id.student_id', '=', student.id)])[0]

            # cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
            # cleantext = re.sub(cleanr, '', approval_requests.user_remarks)
            # text = cleantext
            # if "Remarks by user" in cleantext:
            #     text = cleantext.replace("Remarks by user", " ")

            values.update({
                'clearance_request': requests or False,
                'approval_requests': approval_requests or False,
                'approval_dd_requests': approval_dd_requests or False,
            })
            return http.request.render('odoocms_student_portal.student_clearance_request', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/clearance/save'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def clearanceRequestSave(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            clearance_record_id = request.env['odoocms.student.clearance'].sudo().search([])
            
            data = {
                'student_id': student.id,
                'state': 'submit',
            }
            previous_clearance_record = request.env['odoocms.student.clearance'].sudo().search(
                [('student_id', '=', student.id)])
            if previous_clearance_record:
                print('Record is alreay generated')
            else:
                clearance_record_id = request.env['odoocms.student.clearance'].sudo().create(data)
                # object = http.request.env['odoocms.student.clearance'].sudo().search([])
                # object = http.request.env['odoocms.student.clearance.selection.wiz'].sudo().search(['selected_student_ids.ids','=',student.id])
                # object.selected_student_ids = [(4, [student])]
                # object.selected_student_ids = [(6, 0, student)]
                # object.generate_request()

                approval_cat_id = request.env['approval.category'].sudo().search([('name', '=', 'Clearance Approval')])
                # if not approval_cat_id:
                #     raise UserError(_(
                #         "Please Add Approval Category with name 'Clearance Approval' and 'Clearance DD Request approval'."))
                # approval_cat_dd_id = request.env['approval.category'].search(
                #     [('name', '=', 'Clearance DD Request approval')])
                # if not approval_cat_dd_id:
                #     raise UserError(_("Please Add Approval Category with name 'Clearance DD Request approval'."))
                approver_ids = []
                for user in approval_cat_id.user_ids:
                    approver_ids.append([0, 0, {'user_id': user.id}])
                
                request_data = {
                    'name': 'Clearance Request approval',
                    'request_owner_id': request.env.user.id,
                    'category_id': approval_cat_id.id,
                    'date': datetime.date.today(),
                    'approver_ids': approver_ids,
                    'request_status': 'pending',
                    'remarks': '',
                    'student_mobile': clearance_record_id.student_id.mobile,
                    'email': clearance_record_id.student_id.email,
                    'clearance_form_id': clearance_record_id.id,
                }
                request_id = request.env['approval.request'].sudo().create(request_data)
                request_id.sudo().action_confirm()
                clearance_record_id.approval_request_id = request_id.id

            return request.redirect('/student/clearance')
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    # clearance_cancel_req
    @http.route(['/student/clearance/req/cancel'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def clearanceRequestCancel(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            id = kw.get('id')
            request.env['odoocms.student.clearance'].sudo().search(
                [('student_id', '=', student.id), ('id', '=', id)]).unlink()
            request.env['approval.request'].sudo().search(
                [('clearance_form_id.student_id', '=', student.id), ('id', '=', id)]).unlink()
            data = {
                'status_is': '',
            }
            
        except Exception as e:
            data = {
                'message': e or False
            }
        data = json.dumps(data)
        return data

    @http.route(['/student/tuition/fee/defer/request'], type='http', auth="user", website=True)
    def tuitionfeeDeferRequest(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)

            terms = request.env['odoocms.academic.term'].sudo().search([])
            requests = request.env['odoocms.tuition.fee.deferment.request'].sudo().search([('student_id', '=', student.id)])

            values.update({
                'student_requests': requests,
                'all_terms': terms,
            })
            return http.request.render('odoocms_student_portal.student_tuition_fee_defer_request', values)
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Fee Defer',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

