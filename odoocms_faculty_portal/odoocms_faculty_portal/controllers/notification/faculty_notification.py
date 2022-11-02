from odoo import http
from odoo.http import request
from datetime import date
from .. import main
import pdb


class FacultyProfile(http.Controller):
    @http.route(['/faculty/notifications'], type='http', auth="user", website=True)
    def notification(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_web.portal_error", values)

            values.update({
                'active_menu': 'notifications',
            })
            return http.request.render('odoocms_faculty_portal.faculty_notifications', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_web.portal_error', values)