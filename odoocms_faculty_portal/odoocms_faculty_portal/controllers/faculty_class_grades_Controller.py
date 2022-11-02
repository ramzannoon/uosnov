
from odoo import http
from odoo.http import request
from . import main
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal

from bokeh.util import session_id
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
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
            grade_classes = http.request.env['odoocms.class.grade'].sudo().search([
                ('grade_staff_id', '=', faculty_staff.id),('term_id','=',values['config_term'])]).filtered(lambda l: len(l.primary_class_ids) > 0 )
            # if not grade_classes:
            #     values = {            #
            #         'error_message': 'Grade class not exists!',
            #     }
            #     return request.render("odoocms_faculty_portal.faculty_error", values)

            # rechecking_requests = http.request.env['odoocms.request.subject.rechecking'].sudo().sudo().search([('state', '=', 'approve')])
            color = ['md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400']
            
            values.update({
                'grade_classes': grade_classes or False,
                # 'rechecking_requests':rechecking_requests,
                'rechecking_requests': False,
                # These are for breadcrumbs
                'page': 'result',
                'color': color,
            })
            return http.request.render('odoocms_faculty_portal.faculty_portal_result_grade_classes', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)

    @http.route(['/faculty/class/assign/grades/id/<int:id>'], type='http', auth="user", website=True)
    def faculty_staff_assign_grades(self, id=0, date_begin=None, date_end=None, sortby=None, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
            if id != 0:
                domain = [
                    ('id', '=', id),
                    ('grade_staff_id', '=', faculty_staff.id),
                ]
                
                grade_class = request.env['odoocms.class.grade'].sudo().search(domain)
                if not grade_class:
                    values = {
                        'header': 'Error!',
                        'error_message': 'Grade class not exists!',
                    }
                    return request.render("odoocms_faculty_portal.faculty_error", values)

                # grading_method = http.request.env['ir.config_parameter'].sudo().get_param('odoocms_exam.grading_method')
                # if grading_method:
                #     grading_method = grading_method
                # else:
                #     grading_method = 'absolute'

                if True:   #grading_method == 'grade_curve':
                    
                    bokeh_server_address = request.env['ir.config_parameter'].sudo().get_param('odoocms.bokeh_server_address')
                    bokeh_secret_key = request.env['ir.config_parameter'].sudo().get_param('odoocms.bokeh_secret_key')
                    s_id = session_id.generate_session_id(secret_key=bokeh_secret_key, signed=True)
                    db = request.env.cr.dbname
                    link = "http://" + bokeh_server_address + ":5006/b9?bokeh-session-id={}&class_id={}&db={}".format(s_id, id, db)
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
            else:
                values = {
                    'header': 'Error!',
                    'error_message': 'Nothing Found!',
                }
                return request.render("odoocms_faculty_portal.faculty_error", values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)

    @http.route(['/faculty/class/final/grades/id'],type='http', auth="user", method=['POST'], website=True, csrf=False)
    def grade_submit(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
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
                'error_message': e or False
            }
        data = json.dumps(data)
        return data
