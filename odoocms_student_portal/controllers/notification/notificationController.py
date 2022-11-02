from odoo import http
from .. import main
from odoo.http import request


class StudentNotification(http.Controller):
    @http.route(['/student/notifications'], type='http', auth="user", website=True)
    def student_notifications(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            values.update({
                'active_menu': 'notifications'
            })
            return http.request.render('odoocms_student_portal.student_notifications', values)
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'notification',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)
