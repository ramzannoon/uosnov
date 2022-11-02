from odoo import http
from odoo.http import request
from datetime import datetime,date
from . import main
import pdb
class StudentProfile(http.Controller):
    @http.route(['/student/profile'], type='http', auth="user", website=True)
    def home(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)

            return http.request.render('odoocms_student_portal.studentProfile',values)

        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Profile',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)