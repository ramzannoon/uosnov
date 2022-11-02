from odoo import http,_
from odoo.http import content_disposition, Controller, request, route
from datetime import datetime


class TravelLeave(http.Controller):

    @http.route(['/travel/Leave/form'], csrf=False, type='http', auth="user", website=True, method=['GET'], portal=True)
    def travel_form(self, **post):
        employee_id = request.env['emp.travel.request'].sudo().search([])
        # data = {
        #     'employee_id': employee_id,
        # }
        # data
        return request.render("odoocms_employee_portal.travel_leave_form" )

        # return request.redirect('/travel/Leave/form')

    @http.route(['/travel/Leave/form/submit'], csrf=False, type='http', auth="user", website=True, method=['POST'],
                portal=True)
    def travel_leave_form_submit(self, **post):
        print(1111111111111111111111, post)
        # try:
        #     values, success,

        date_from = post.get('date_from')
        date_to = post.get('date_to')
        current_user = http.request.env.user
        employee_id = request.env['emp.travel.request'].sudo().search([('employee_id', '=', current_user.name),('state', '=', 'approve')])
        values = request.params.copy()

        print(11111111111111111 , values)
        if date_to < date_from:
            print(222222222222222222222222222222)
            return request.render("odoocms_employee_portal.travel_leave_form_error", values)

        b = request.env['emp.travel.request'].sudo().create({
            'employee_id': current_user.employee_id.id,
            # 'employee_id': employee_id.id,
            'date_from': date_from,
            'date_to': date_to,
            'location': post.get("location"),
            # 'name': name,
        })
        return request.render("odoocms_employee_portal.travel_leave_form_success", values)

    @http.route(['/travel/back'], type='http', auth="user", website=True, portal=True)
    def travel_back(self, **post):
        return request.redirect('/travel/Leave/form')






        # return request.render("odoocms_employee_portal.travel_leave_recs", )

    # return request.redirect('/travel/Leave/form')

    # except Exception as e:
    # values = {
    #     'error_message': e or False
    # }
    # return http.request.render('odoocms_web.portal_error', values)

    # return request.render("odoocms_employee_portal.travel_leave_form_success")

    # return http.request.render("odoocms_employee_portal.travel_leave_form_success", )


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

    # current_user = http.request.env.user
    # voucher_image = kw.get('voucher_image', False)
    # voucher_number = kw.get('voucher_number', False)
    # date_voucher = kw.get('date_voucher', False)
    # applicant_merit = int(kw.get('applicant_merit', 0))
    # lock_seat = kw.get('lock_seat')
    # if lock_seat == 'yes':
    #     locked = True
    # else:
    #     locked = False
    #
    # applicant_merit_id = http.request.env['odoocms.application.merit'].sudo().search(
    #     [('id', '=', applicant_merit)])
    #
    # if applicant_merit_id and applicant_merit_id.merit_register_id.date_end < date.today():
    #     values = {
    #         'header': 'Error',
    #         'message': 'Date Over! Last date of fee details submission was:' + str(
    #             applicant_merit_id.merit_register_id.date_end)
    #     }
    #     return request.render("odoocms_admission_portal.submission_message", values)
    # if applicant_merit_id and not applicant_merit_id.voucher_status and applicant_merit_id.state == 'draft':
    #     values = {
    #         'voucher_image': base64.encodestring(voucher_image.read()),
    #         'voucher_number': voucher_number,
    #         'date_voucher': date_voucher,
    #         'date_submission': date.today(),
    #         'locked': locked,
    #     }
    #     applicant_merit_id.write(values)
    #     return request.redirect('/my/merit')
    # else:
    #     values = {
    #         'header': 'Error',
    #         'message': 'Something went wrong. Details are not submitted!'
    #     }
    #     return request.render("odoocms_admission_portal.submission_message", values)


class TravelLeaveRecordss(http.Controller):

    @http.route(['/travel/Leave/recss'], type='http', auth="user", website=True, method=['GET'], portal=True)
    def travel_recs_form(self, **post):
        return request.render("odoocms_employee_portal.travel_leave_recs", )
