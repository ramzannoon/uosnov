from odoo import http
from odoo.http import request

class Dashboard(http.Controller):
    @http.route(['/error'], type='http', auth="user", website=True)
    def securityerror(self, **kw):
         company = request.env.user.company_id
         values = {
             'company' :company,
         }
         return http.request.render('odoocms_student_portal.student_error')