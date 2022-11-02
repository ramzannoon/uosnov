import json

from odoo import http
from odoo.http import request
from datetime import date
from . import main
import pdb


class FacultyCredentials(http.Controller):
    @http.route(['/faculty/credentials/reset'], type='http', auth="user", website=True)
    def faculty_cred(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)

            values.update({
                'active_menu': '',

            })
            return http.request.render('odoocms_faculty_portal.faculty_password_reset', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)

    @http.route(['/faculty/credentials/reset/save'], type='http', method=['POST'], auth="user", website=True, csrf=False)
    def faculty_cred_save(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
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
                'status_is': "Error",
                'message': e.args[0],
                'color': '#FF0000'
            }
            data = json.dumps(data)
            return data







