from odoo import http
from odoo.http import request


class Dashboard(http.Controller):
    @http.route(['faculty/error'], type='http', auth="user", website=True)
    def securityerror(self, **kw):
         company = request.env.user.company_id
         # partner = http.request.env.user.partner_id

         values = {
             'company':company
         }
         return http.request.render('studentwebportal.student_error',values)