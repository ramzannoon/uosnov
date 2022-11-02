from odoo import http
from odoo.http import content_disposition, Controller, request, route
# from odoo import datetime


# class LoanRequest(http.Controller):
#
#     @http.route(['/loan/Leave/form'], type='http', auth="user", website=True, method=['GET'], portal=True)
#     def loan_form(self, **post):
#         print("4444444444444444444444444444444444444", post)
#
#         employee_id = request.env['hr.loan'].sudo().search([])
#         # payment_date = post.get('payment_date')
#         # loan_amount = post.get('loan_amount')
#         # currency_id = post.get('currency_id')
#         # department_id = post.get('department_id')
#
#         data = {
#             'employee_id': employee_id,
#             # 'loan_amount': loan_amount,
#             # 'payment_date': payment_date,
#             # 'currency_id': currency_id,
#             # 'department_id': department_id,
#
#         }
#         print("44444444444444444444444444444444444445555555", data, employee_id)
#         return request.render("odoocms_employee_portal.loan_leave_request_form", data)
#
#     @http.route(['/loan/Leave/form/submit'], type='http', auth="user", website=True, method=['POST'], portal=True)
#     def loan_leave_form_submit(self, **post):
#         print(1111111111111111111111, post)
#
#         date = post.get('date')
#         employee_id = request.env['emp.travel.request'].sudo().search([])
#
#         b = request.env['hr.loan'].sudo().create({
#             'name': post.get('name'),
#             'employee_id': post.get('employee_id'),
#             'date': date,
#             # 'amount': post.get("amount")
#         })
#         print(2222222222222222, b)
#         return request.render("odoocms_employee_portal.loan_leave_form_success", )


class Test(http.Controller):

    @http.route(['/test/Leave/form'], type='http', auth="user", website=True, method=['GET'], portal=True)
    def test_form(self, **post):
        print("4444444444444444444444444444444444444", post)

        current_user = http.request.env.user
        employee_id = request.env['hr.loan'].sudo().search([('employee_id', '=', current_user.name),('state', '=', 'approve')])

        # payment_date = post.get('payment_date')
        # loan_amount = post.get('loan_amount')
        # currency_id = post.get('currency_id')
        # department_id = post.get('department_id')

        data = {
            'employee_id': employee_id,
            # 'loan_amount': loan_amount,
            # 'payment_date': payment_date,
            # 'currency_id': currency_id,
            # 'department_id': department_id,

        }
        print("44444444444444444444444444444444444445555555", data, employee_id)
        return request.render("odoocms_employee_portal.test_leave_request_form", data)



    @http.route(['/test/Leave/form/submit'], type='http', auth="user", website=True, method=['POST'], portal=True)
    def test_submit(self, **post):
        print(1111111111111111111111, post)
        date = post.get('date')
        loan_amount = post.get('loan_amount')
        installment = post.get('installment')
        current_user = http.request.env.user
        # employee = request.env['hr.loan'].sudo().search([('employee_id', '=', request.env.user.id)])
        # print(employee,"ddddddddddddddddddddddddd")


        # print(11111111111111111 )
        # if date < Datetime.now():
        #     print(222222222222222222222222222222)
        #     return request.render("odoocms_employee_portal.travel_leave_form_error")

        b = request.env['hr.loan'].sudo().create({
            'name': post.get('name'),
            'employee_id': current_user.employee_id.id,
            'date': date,
            'loan_amount': loan_amount,
            'installment': installment,

            # 'amount': post.get("amount")
        })
        print(2222222222222222, b,current_user.employee_id)
        # return request.redirect('/test/Leave/form')

        return request.render("odoocms_employee_portal.test_loan_leave_form_success", )


    @http.route(['/test/back'], type='http', auth="user", website=True, portal=True)
    def test_back(self, **post):
        return request.redirect('/test/Leave/form')


class LoanLeaveRecordss(http.Controller):

    @http.route(['/loan/Leave/recss'], type='http', auth="user", website=True, method=['GET'], portal=True)
    def loan_recs_form(self, **post):
        return request.render("odoocms_employee_portal.loan_leaves_recs", )

