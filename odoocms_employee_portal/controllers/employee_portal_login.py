from odoo import http
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo import fields, models, _, api
from odoo.http import content_disposition, Controller, request, route
# from datetime import datetime


class CataloguePrint(http.Controller):

    @http.route(['/report/pdf/catalogue_download'], type='http', auth='user', method=['GET', 'POST'])
    def download_catalogue(self, employee_id):
        pdf, _ = request.env.ref('odoocms_employee_portal.employee_action_report').sudo(). \
            render_qweb_pdf([int(employee_id)])
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf)),
                          ('Content-Disposition', 'catalogue' + '.pdf;')]
        return request.make_response(pdf, headers=pdfhttpheaders)


class EmployeeLoginDashboard(http.Controller):
    @http.route(['/employee/dashboard'], type='http', auth="user", website=True, method=['GET'])
    def employee_home_new(self, **kw):
        payslip_id = request.env['hr.employee'].sudo().search([])
        return request.render("odoocms_employee_portal.employee_reportsss", {
            'payslip_id': payslip_id,
        })

        #         # @http.route('/employee/dashboard2/<model("hr.employee"):so>/', type='http', auth="user", website=True)

        @http.route(['/employee/dashboard2'], type='http', auth="user", website=True, method=['GET', 'POST'])
        def employee_page(self, so, **kw):
            return request.render("odoocms_employee_portal.employee_portal_dashboard_page", {
                'emp': so
            })

        # @http.route(['/employee/report'], type='http', auth="user", website=True)
        # def employee_report(self, **kw):
        #     return request.render("odoocms_employee_portal.employee_payslips_template")

        ###############################################################################


class EmployeeReport(http.Controller):

    @http.route(['/employee/report'], type='http', auth="user", website=True, method=['POST'])
    def employee_report(self, **kw):
        current_user = http.request.env.user
        print(current_user, "Current user  ----------------------")

        payslip_id = request.env['hr.employee'].sudo().search([])
        pays_id = request.env['hr.employee'].sudo().search([('current_user', '=', 'employee_id')])
        payslipppss_id = request.env['hr.payslip'].sudo().search([('current_user', '=', 'employee_id')])

        rule_id = request.env['hr.salary.rule'].sudo().search([])
        # docs = request.env['hr.employee'].browse(request.env.context.get('active_id'))
        # docs = pays_id
        datas = {
            'rule_id': rule_id,
            'pays_id': pays_id,
            'payslipppss_id': payslipppss_id,
            # 'docs': docs
        }
        return request.render("odoocms_employee_portal.employee_report_template", datas)


class EmployeeDetails(http.Controller):

    @http.route(['/employee/details'], type='http', auth="user", website=True, method=['GET', 'POST'])
    def employee_report(self, **kw):
        # test = self.user_id
        # print(test)

        current_user = http.request.env.user
        # pay_emp_id = request.env['hr.employee'].sudo().search([('employee_id', '=', current_user.name)])
        payslip_id = request.env['hr.payslip'].sudo().search([('employee_id', '=', current_user.name),('state', '=', 'done')])

        return request.render("odoocms_employee_portal.employee_payslips_template",
                              {'payslip_id': payslip_id})


class LeavesEmployee(http.Controller):

    @http.route(['/leaves/details'], type='http', auth="user", website=True, method=['GET'])
    def leaves_details(self, **kw):
        current_user = http.request.env.user
        print("jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj", current_user)

        leaves_id = request.env['hr.leave'].sudo().search([('employee_id', '=', current_user.name),('state', '=', 'validate')])
        print("gggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg", leaves_id)

        return request.render("odoocms_employee_portal.employee_leaves_template",
                              {'leaves_id': leaves_id,

                               }
                              )


class LeavesformSubmit(http.Controller):
    @http.route(['/leaves/form/submit/successfull'], type='http', auth="user", website=True, method=['GET'])
    def partner_form(self, **post):
        print('taest111111111111111111111111111')
        leaves_id = request.env['hr.leave.type'].sudo().search([])
        data = {
            'leaves_id': leaves_id,
        }
        print("emloyee form data 11", leaves_id)
        return request.render("odoocms_employee_portal.employee_leaves_form_submit", data)

    @http.route(['/leaves/form/submit'], type='http', auth="user", website=True, method=['POST'])
    def customer_form_submit(self, **post):
        print(12333232323232323333, post)
        # self.partner_form()
        holiday_status_id = post.get('leaves')
        date_from = post.get('date_from')
        date_to = post.get('date_to')
        name = post.get('name')
        duration_display = post.get('duration_display')
        print(5555555555555555555555, holiday_status_id)
        leave_request = request.env['hr.leave'].sudo().create({
            'holiday_status_id': holiday_status_id,
            'date_from': date_from,
            'date_to': date_to,
            'name': name,
            'duration_display': duration_display,
        })
        # return request.redirect('/leaves/form/submit/successfull')
        return request.render("odoocms_employee_portal.tmp_customer_form_success", leave_request)


class LeavesTypes(http.Controller):

    @http.route(['/leaves/types'], type='http', auth="user", website=True, method=['GET'])
    def leaves_details(self, **kw):
        print("emloyee kanakkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk", )

        leaves_id = request.env['hr.leave.type'].sudo().search([])
        data = {
            'leaves_id': leaves_id,
        }
        # print(11111111111111111111111, post)
        print("emloyee kanakkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkNeww", data)
        return request.render("odoocms_employee_portal.tmp_customer_form", data)

    @http.route(['/customer/form/submit/new'], type='http', auth="user", website=True, method=['POST'])
    def customer_form_submit(self, **post):
        employee = request.env['hr.employee'].search([('name', '=', request.env.user.name)])
        print(11111112222222222222, employee)
        fmt = '%Y-%m-%d'

        date_from = post.get('date_from')
        date_to = post.get('date_to')
        d1 = datetime.strptime(date_from, fmt)
        print(d1)
        d2 = datetime.strptime(date_to, fmt)
        print(d2)
        date_difference = (d2 - d1).days
        # date_difference = now.strftime("%d")

        a = request.env['hr.leave'].sudo().create({
            'employee_id': employee.id,
            'holiday_status_id': int(post.get('leaves_id')),
            # post.get['leaves_id'],
            'request_date_from': post.get('date_from'),
            'request_date_to': post.get('date_to'),
            'number_of_days': date_difference,
            'name': post.get('name'),
        })
        return request.redirect('/leaves/types')

        print(7777777777777777777777777, post.get('date_difference'))
        print(5555555555555555555, post.get('date_to'))
        print(6666666666666666, type(post.get('date_to')))
        print("rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr", date_difference)
        # return request.render("odoocms_employee_portal.tmp_customer_form_success", a)
        # return request.render("odoocms_employee_portal.leave_tyes_form", )


class LeavesSummaryDetails(http.Controller):

    @http.route(['/leaves/summary/details'], type='http', auth="user", website=True, method=['GET', 'POST'])
    def leaves_form(self,  **post):
        current_user = http.request.env.user
        # leave = post.get('leave')

        # number_of_days = post.get('number_of_days')
        # duration_display = post.get('duration_display')
        # remaining_leaves = (number_of_days - duration_display)

        leaves_summary_id = request.env['hr.leave.allocation'].sudo().search([('employee_id', '=', current_user.name)])

        # leaves_summary_id = request.env['hr.leave.type'].sudo().search([])
        # leaves_summary_id = request.env['hr.leave'].sudo().search([])
        #
        #
        # test = ({
        #     'name': post.get('name'),
        # })

        return request.render("odoocms_employee_portal.leaves_summary_details_template",
                              {'leaves_summary_id': leaves_summary_id,})

    # remaining_leaves



class AnnualSummaryDetails(http.Controller):

    @http.route(['/annual/leaves/summary'], type='http', auth="user", website=True, method=['GET', 'POST'])
    def get_sales(self, ):
        current_user = http.request.env.user
        annual_leaves_id = http.request.env['hr.employee'].sudo().search([])
        # ('employee_id', '=', current_user.name)
        return request.render("odoocms_employee_portal.annual_leaves_summary_details_template",
                              {'annual_leaves_id': annual_leaves_id, })

    # annual_leaves_id = request.env['hr.leave.report'].sudo().search([])


class Employeedetails(http.Controller):

    @http.route(['/employee/main/details'], type='http', auth="user", website=True, method=['GET', 'POST'])
    def leaves_details(self, **kw):
        leaves_id = request.env['hr.employee'].sudo().search([])
        return "hello employees"


class LoanRequest(http.Controller):

    @http.route(['/loan/Leave/form'], type='http', auth="user", website=True, method=['GET'], portal=True)
    def loan_form(self, **post):
        loan_id = request.env['hr.loan'].sudo().search([])

        data = {
            'name': loan_id,
        }
        return request.render("odoocms_employee_portal.loan_leave_request_form", data)
