from datetime import date
from odoo import http
from . import main
import pdb

from odoo.http import content_disposition, Controller, request, route


class StudentIndustrialVisit(http.Controller):
    @http.route(['/student/siva'], type='http', auth="user", website=True)
    def student_siva(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)

            values.update({
                'active_menu': 'notifications'
            })
            return http.request.render('odoocms_student_portal.student_notifications', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)