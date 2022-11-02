import json
from datetime import date
import datetime
from odoo import http
from odoo.http import request
from odoo.addons.odoocms_student_portal.controllers import main as student_main
import base64

class StudentProject(http.Controller):

    @http.route(['/student/project'], type='http', auth="user", website=True)
    def student_project(self, **kw):
        try:
            values, success, student = student_main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            student_project = request.env['odoocms.student.project'].sudo().search([('student_ids', '=', student.id),('state','=','accept')])
            feedback_lines = request.env['odoocms.spm.feedback.lines'].sudo().search([('project_id', '=', student_project.id)])

            values.update({
                'active_menu': 'notifications',
                'projects': student_project,
                'feedback_lines':feedback_lines or False,
            })
            return http.request.render('odoocms_spm.student_projects', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/project/request'], type='http', auth="user", website=True)
    def studentprojectRequest(self, **kw):

        values, success, student = student_main.prepare_portal_values(request)
        if not success:
            return request.render("odoocms_student_portal.student_error", values)

        student_project = request.env['odoocms.student.project'].sudo().search([('student_ids', '=', student.id)])

        values.update({
            'projects': student_project,
        })
        return http.request.render('odoocms_student_portal.student_project_request', values)

    # @http.route(['/student/project/request/save'], type='http', auth="user", website=True, method=['POST'],
    #             csrf=False)
    # def studentprojectRequestSave(self, **kw):
    #     values, success, student = main.prepare_portal_values(request)
    #     if not success:
    #         return request.render("odoocms_student_portal.student_error", values)
    #
    #     student_project = request.env['odoocms.student.project'].sudo().search([('student_ids', '=', student.id)])
    #
    #     values.update({
    #         'projects': student_project,
    #     })
    #     return http.request.render('odoocms_student_portal.student_project_request', values)

    #
    @http.route(['/student/project/documents'], type='http', method=['POST'], auth="user", website=True,
                csrf=False)
    def studentprojectDocumentsUpdate(self, **kw):
        try:
            values, success, student = student_main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            name = kw.get('name')
            code = kw.get('code')
            if kw.get('file'):
                file = base64.b64encode(kw.get('file').read())
            milestone_id = request.env['odoocms.student.project.milestone'].sudo().search([('code','=',code)]).id
            student_project = request.env['odoocms.student.project'].sudo().search([('student_ids', '=', student.id)])
            if student_project:
                student_document = request.env['odoocms.spm.document.lines'].sudo().search([])
                student_document.sudo().create({
                    'milestone_id': milestone_id,
                    'document_title': name,
                    'document_code': code,
                    'attachment_file': file,
                    'project_id': student_project.id})
            data = {'status_is': "NO Error",}
            # return request.redirect('/student/project')
        except Exception as e:
            data = {
                'status_is': "Error",
                'message': e.args[0],
                'color': '#FF0000'
            }
        data = json.dumps(data)
        return data
