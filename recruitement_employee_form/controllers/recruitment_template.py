from odoo import http
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo import fields, models, _, api
from odoo.http import content_disposition, Controller, request, route


class EmployeeLoginDashboard(http.Controller):
    @http.route(['/recruitment/employee/form'], type='http', auth="user", website=True, method=['GET'])
    def employee_recruitment(self, **kw):

        # return request.redirect('/recruitment/employee/form')
        return request.render("recruitement_employee_form.recruitment_employee_form")
