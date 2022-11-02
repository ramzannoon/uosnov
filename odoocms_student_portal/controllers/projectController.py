from datetime import date
from odoo import http
from . import main
import pdb

from odoo.http import content_disposition, Controller, request, route


class StudentProject(http.Controller):
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

    @http.route(['/student/project/request/save'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def studentprojectRequestSave(self, **kw):
        values, success, student = main.prepare_portal_values(request)
        if not success:
            return request.render("odoocms_student_portal.student_error", values)
        
        student_project = request.env['odoocms.student.project'].sudo().search([('student_ids', '=', student.id)])
       
        values.update({
            'projects': student_project,
        })
        return http.request.render('odoocms_student_portal.student_project_request', values)

    @http.route(['/student/project'], type='http', auth="user", website=True)
    def student_project(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)

            values.update({
                'active_menu': 'notifications'
            })
            return http.request.render('odoocms_student_portal.student_projects', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)