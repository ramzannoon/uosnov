import json

from odoo import http
from odoo.http import request
from datetime import date
from .. import main
import pdb


class StudentCredentials(http.Controller):
    @http.route(['/student/credentials/change'], type='http', auth="user", website=True)
    def student_cred(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)

            values.update({
                'active_menu': '',

            })
            return http.request.render('odoocms_student_portal.student_password_reset', values)
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Login Credentials',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_web.portal_error', values)

    @http.route(['/student/credentials/change/save'], type='http', method=['POST'], auth="user", website=True, csrf=False)
    def student_cred_save(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            old_passwd=kw.get('old_credential')
            new_passwd=kw.get('new_credential')
            if not old_passwd and new_passwd:
                data = {
                    'status_is': "Error",
                    'message': 'Provide complete data.',
                    'color': '#FF0000'
                }

                data = json.dumps(data)
                return data

            result = request.env.user.sudo().change_password(old_passwd, new_passwd)

            data = {
                'status_is': "",
                'message': '',
                'color': '#FF0000'
            }

            data = json.dumps(data)
            return data
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'login Credentials Save',
                'description': e or False,
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







