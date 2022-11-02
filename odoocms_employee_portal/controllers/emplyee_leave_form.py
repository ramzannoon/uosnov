from odoo import http
from odoo.http import request, route, Controller
from datetime import datetime


class PartnerForm(http.Controller):

    @http.route(['/customer/form'], type='http', auth="user", website=True, method=['GET'], portal=True)
    def partner_form(self, **post):
        leaves_id = request.env['hr.leave.type'].sudo().search([])
        data = {
            'leaves_id': leaves_id,
        }
        return request.render("odoocms_employee_portal.tmp_customer_form", data)

    @http.route(['/customer/form/submit'], type='http', auth="user", website=True, method=['POST'], portal=True)
    def customer_form_submit(self, **post):
        employee = request.env['hr.employee'].sudo().search([('name', '=', request.env.user.name)])

        # print('this is myu dats ', (datetime.fromisoformat(post.get('date_from')) - datetime.fromisoformat(post.get('date_to'))).days)
        fmt = '%Y-%m-%d'

        date_from = post.get('date_from')
        date_to = post.get('date_to')
        d1 = datetime.strptime(date_from, fmt)
        print(d1)
        d2 = datetime.strptime(date_to, fmt)
        print(d2)
        date_difference = (d2 - d1).days + 1

        # date_difference = now.strftime("%d")

        # aaa = datetime.fromisoformat(post['date_from'],)
        # values = request.params.copy()

        # gg = datetime.datetime.strptime(post.get('date_from'), "%Y-%m-%d")

        # print(f"this is my new date object{aaa}")

        # leave_check = request.env['hr.leave.allocation'].sudo().search(
        #     [('holiday_status_id', '=', values['leaves_id'])])
        # print(11111111111111111, leave_check)

        # if leave_check:
        #     return request.render("odoocms_employee_portal.tmp_customer_form_success")
        # else:
        #     return request.render("odoocms_employee_portal.repeat_leave_type_error")
        #
        #     print(222222222222222222222222222222)
        #     return request.render("odoocms_employee_portal.travel_leave_form_error", values)

        if not post['date_from'] == post.get('date_to'):
            request.env['hr.leave'].sudo().create({
                'employee_id': employee.id,
                'holiday_status_id': int(post.get('leaves_id')),
                # post.get['leaves_id'],
                'request_date_from': post.get('date_from'),
                'request_date_to': post.get('date_to'),
                'date_from': post.get('date_from'),
                'date_to': post.get('date_to'),
                'number_of_days': date_difference,
                'name': post.get('name'),
            })
            # (datetime.fromisoformat(post.get('date_from')) - datetime.fromisoformat(post.get('date_to'))).days,
        return request.render("odoocms_employee_portal.tmp_customer_form_success", )

    def date_function(self):
        fmt = '%Y-%m-%d'
        date_from = self.date_from
        date_to = self.date_to
        d1 = datetime.strptime(date_from, fmt)
        print(d1)
        d2 = datetime.strptime(date_to, fmt)
        print(d2)
        date_difference = d2 - d1
        print(date_difference, "66666666666666666666666666666")

    @http.route(['/customer/back'], type='http', auth="user", website=True, method=['GET'], portal=True)
    def back_customer_form(self, **post):
        return request.redirect('/customer/form')


class TestForm(http.Controller):

    @http.route(['/editleave/form'], type='http', auth="user", website=True, method=['GET'], portal=True)
    def editleave_form(self, **post):
        leaves_id = request.env['hr.leave.type'].sudo().search([])
        data = {
            'leaves_id': leaves_id,
        }
        return request.render("odoocms_employee_portal.edit_leave_form", data)

    @http.route(['/editleave/form/successfull'], type='http', auth="user", website=True, method=['POST'], portal=True)
    def editleave_form_submit(self, **post):
        employee = request.env['hr.employee'].search([('name', '=', request.env.user.name)])
        fmt = '%Y-%m-%d'
        date_from = post.get('date_from')
        date_to = post.get('date_to')
        # d1 = datetime.strptime('date_from', fmt)
        # d2 = datetime.strptime('date_to', fmt)
        # date_difference = (d2 - d1).days
        # date_difference = now.strftime("%d")
        a = request.env['hr.leave'].sudo().create({
            'employee_id': employee.id,
            'holiday_status_id': int(post.get('leaves_id')),
            # post.get['leaves_id'],
            'request_date_from': post.get('date_from'),
            'request_date_to': post.get('date_to'),
            'number_of_days': post.get('name'),
            'name': post.get('name'),
        })
        return request.redirect('/editleave/form')

        # return request.render("odoocms_employee_portal.edit_leave_form_success",)
