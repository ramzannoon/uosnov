
from odoo import http
from odoo.http import request
from .. import main
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal

#from bokeh.util import session_id
from bokeh.util import token
from datetime import date
import json
import pdb

import logging
_logger = logging.getLogger(__name__)


class FacultyGradePortal(CustomerPortal):

    @http.route(['/faculty/grade/home'], type='http', auth="user", website=True)
    def faculty_staff_grade_home(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_web.portal_error", values)
            
            grade_classes = http.request.env['odoocms.class.grade'].sudo().search([
                ('grade_staff_id', '=', faculty_staff.id),('term_id','=',values['config_term'])]).filtered(lambda l: len(l.primary_class_ids) > 0 )
            term_ids = http.request.env['odoocms.academic.term'].sudo().search([], order='sequence desc')


            values.update({
                'grade_classes': grade_classes or False,
                # 'rechecking_requests':rechecking_requests,
                'rechecking_requests': False,
                'term_ids':term_ids,
                'active_term': values['config_term'],
                # These are for breadcrumbs
                'page': 'result',

            })
            return http.request.render('odoocms_faculty_portal.faculty_portal_result_grade_classes', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_web.portal_error', values)

    @http.route(['/faculty/grade/home/search'], type='http', auth="user", website=True,  csrf=False)
    def faculty_staff_grade_home_search(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_web.portal_error", values)
            term = kw.get('term_id')
            if term:
                term = int(term)
            if not term:
                term = values['config_term']

            grade_classes = http.request.env['odoocms.class.grade'].sudo().search([
                ('grade_staff_id', '=', faculty_staff.id), ('term_id', '=', term)]).filtered(lambda l: len(l.primary_class_ids) > 0)
            term_ids = http.request.env['odoocms.academic.term'].sudo().search([], order='sequence desc')

            values.update({
                'grade_classes': grade_classes or False,
                # 'rechecking_requests':rechecking_requests,
                'rechecking_requests': False,
                'config_term' : term,
                'term_ids': term_ids,
                'active_term': values['config_term'],
                # These are for breadcrumbs
                'page': 'result',

            })
            return http.request.render('odoocms_faculty_portal.faculty_portal_result_grade_classes', values)
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': '/faculty/grade/home/search',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_web.portal_error', values)

    @http.route(['/faculty/class/assign/grades/id/<int:id>'], type='http', auth="user", website=True)
    def faculty_staff_assign_grades(self, id=0, date_begin=None, date_end=None, sortby=None, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_web.portal_error", values)
            
            if id != 0:
                domain = [
                    ('id', '=', id),
                    ('grade_staff_id', '=', faculty_staff.id),
                ]
                
                grade_class = request.env['odoocms.class.grade'].sudo().search(domain)[0]

                if not grade_class:
                    values = {
                        'header': 'Error!',
                        'error_message': 'Grade class not exists!',
                    }
                    return request.render("odoocms_web.portal_error", values)

                # grading_method = http.request.env['ir.config_parameter'].sudo().get_param('odoocms_exam.grading_method')
                # if grading_method:
                #     grading_method = grading_method
                # else:
                #     grading_method = 'absolute'

                if grade_class.grade_method_id.code == 'histogram':   #grading_method == 'grade_curve':
                    
                    bokeh_server_address = request.env['ir.config_parameter'].sudo().get_param('odoocms.bokeh_server_address')
                    bokeh_secret_key = request.env['ir.config_parameter'].sudo().get_param('odoocms.bokeh_secret_key')
                    #s_id = session_id.generate_session_id(secret_key=bokeh_secret_key, signed=True)
                    s_id = token.generate_session_id(secret_key=bokeh_secret_key, signed=True)
                    db = request.env.cr.dbname
                    link = bokeh_server_address + "/b9?bokeh-session-id={}&class_id={}&db={}".format(s_id, id, db)
                    _logger.info('Link: %s' % (link))
                    
                    values.update({
                        'grade_class': grade_class,
                        'link': link,
                        'company': request.env.user.company_id,
                        # For breadcrumbs
                        'page': 'assign_grade',
                        'view_grade_class': grade_class,
                    })
                    return request.render("odoocms_faculty_portal.faculty_portal_class_grades", values)

                if not grade_class.grade_method_id.code == 'histogram':
                    values.update({
                        'grade_class': grade_class,
                        #'link': link,
                        'company': request.env.user.company_id,
                        # For breadcrumbs
                        'page': 'assign_grade',
                        'view_grade_class': grade_class,
                    })
                    return request.render("odoocms_faculty_portal.faculty_portal_class_grades", values)
            else:
                values = {
                    'header': 'Error!',
                    'error_message': 'Nothing Found!',
                }
                return request.render("odoocms_web.portal_error", values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            data = {
                # 'student_id': student.id,
                'name': 'Grade Class Home',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            return http.request.render('odoocms_web.portal_error', values)

    @http.route(['/faculty/class/calculate/grades/id'], type='http', auth="user", method=['POST'], website=True, csrf=False)
    def calculate_grade_portal(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_web.portal_error", values)

            id = int(kw.get('id', '0'))
            if id != 0:
                domain = [
                    ('id', '=', id),
                    ('grade_staff_id', '=', faculty_staff.id),
                ]
                grade_class = request.env['odoocms.class.grade'].sudo().search(domain)
                assess_limit_check = grade_class.test_minimum_assessments()

                if assess_limit_check == 'Pass':
                    grade_class.assign_absolute_grades()
                else:
                    data = {
                        'color': 'danger',
                        'message': assess_limit_check,
                    }
                    data = json.dumps(data)
                    return data

            data = {
                'color': 'success',
                'message': 'Grades Assigned.',
            }

        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': '/faculty/class/calculate/grades/id',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            data = {
                'message':  e.args[0] or False,
                'color': 'danger',
            }
        data = json.dumps(data)
        return data

    @http.route(['/faculty/class/calculate/xf/grades/id'], type='http', auth="user", method=['POST'], website=True, csrf=False)
    def calculate_grade_xf_portal(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_web.portal_error", values)

            id = int(kw.get('id', '0'))
            if id != 0:
                domain = [
                    ('id', '=', id),
                    ('grade_staff_id', '=', faculty_staff.id),
                ]
                grade_class = request.env['odoocms.class.grade'].sudo().search(domain)
                assess_limit_check = grade_class.test_minimum_assessments()

                if assess_limit_check == 'Pass':
                    grade_class.assign_xf()
                else:
                    data = {
                        'color': 'danger',
                        'message': assess_limit_check,
                    }
                    data = json.dumps(data)
                    return data

            data = {
                'color': 'success',
                'message': 'XF Grades Assigned.',
            }

        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': '/faculty/class/calculate/xf/grades/id',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            data = {
                'message':  e.args[0] or False,
                'color': 'danger',
            }
        data = json.dumps(data)
        return data

    @http.route(['/faculty/class/unassign/xf/grades/id'], type='http', auth="user", method=['POST'], website=True,
                csrf=False)
    def unassign_grade_xf_portal(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_web.portal_error", values)

            id = int(kw.get('id', '0'))
            if id != 0:
                domain = [
                    ('id', '=', id),
                    ('grade_staff_id', '=', faculty_staff.id),
                ]
                grade_class = request.env['odoocms.class.grade'].sudo().search(domain)
                assess_limit_check = grade_class.test_minimum_assessments()

                if assess_limit_check == 'Pass':
                    grade_class.unassign_xf()
                else:
                    data = {
                        'color': 'danger',
                        'message': assess_limit_check,
                    }
                    data = json.dumps(data)
                    return data

            data = {
                'color': 'success',
                'message': 'XF Grades Un-Assigned.',
            }

        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': '/faculty/class/unassign/xf/grades/id',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            data = {
                'message': e.args[0] or False,
                'color': 'danger',
            }
        data = json.dumps(data)
        return data

    @http.route(['/faculty/class/final/grades/id'],type='http', auth="user", method=['POST'], website=True, csrf=False)
    def grade_submit_portal(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_web.portal_error", values)
            
            id = int(kw.get('id', '0'))
            if id != 0:
                domain = [
                    ('id', '=', id),
                    ('grade_staff_id', '=', faculty_staff.id),
                ]
                grade_class = request.env['odoocms.class.grade'].sudo().search(domain)
                assess_limit_check = grade_class.test_minimum_assessments()

                if assess_limit_check == 'Pass':
                    grade_class.submit_result()

                else:
                    data = {
                        'color': 'danger',
                        'message': assess_limit_check,
                    }
                    data = json.dumps(data)
                    return data

            data = {
                'color': 'success',
                'message' : 'Result submitted',
            }
            
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': '/faculty/class/final/grades/id',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            data = {
                'message':  e.args[0] or False,
                'color': 'danger',
            }
        data = json.dumps(data)
        return data



