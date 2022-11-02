# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import content_disposition, dispatch_rpc, request

from odoo.addons.portal.controllers.web import Home


class HomeSignUp(Home):

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        if kw:
            name = kw['signup_name']
            email = kw['signup_email']
            cnic = kw['signup_cnic']
            phone = kw['signup_phone']
            password = kw['signup_password']
            confirm_password = kw['signup_confirm_password']

            values = request.params.copy()
            values['error'] = ''

            if password != confirm_password:
                values['error'] = _("Passwords do not match; please retype them.")
            if "@" and "." not in email:
                values['error'] = _("Invalid Email")
            if len(cnic) < 14:
                values['error'] = _("Invalid CNIC Number")
            if len(phone) < 11:
                values['error'] = _("Invalid Phone Number")
            if values['error']:
                return request.render("odoocms_admission_portal.web_signup", values)
            else:
                request.env['crm.lead'].sudo().create({
                    'name': name,
                    'email_from': email,
                    'phone': phone,
                })

                request.env['res.users'].sudo().create({
                    'name': name,
                    'email': email,
                    'login': cnic,
                    'mobile_phone': phone,
                    'password': password,
                    'user_type': 'public',
                    "sel_groups_1_8_9": 9,
                })

                user_sudo = request.env['res.users'].sudo().search([('login', '=', cnic)])
                template = request.env.ref('odoocms_admission_portal.mail_template_user_signup_account_created',
                                           raise_if_not_found=False)
                if user_sudo and template:
                    template.sudo().send_mail(user_sudo.id, force_send=True)
                else:
                    values['error'] = _("Sudo User Don't Exist")

                return request.redirect('/admission/registration')
        return request.render("odoocms_admission_portal.web_signup")
