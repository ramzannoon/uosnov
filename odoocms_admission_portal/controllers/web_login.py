# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import odoo
import odoo.modules.registry
import logging
import werkzeug
from odoo.tools.translate import _
from odoo import http
from odoo.http import content_disposition, dispatch_rpc, request
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.exceptions import UserError
import odoo.addons.web.controllers.main as main
from odoo.addons.portal.controllers.web import Home


_logger = logging.getLogger(__name__)


class Home(Home):
	# @http.route('/web/login', type='http', auth="none", sitemap=False) #default funcation is with auth="none" but its changed in website module. So, we added auth="public" and added website inherited code below
	@http.route('/web/login', type='http', auth="public", sitemap=False)
	def web_login(self, redirect=None, **kw):
		main.ensure_db()
		request.params['login_success'] = False
		if request.httprequest.method == 'GET' and redirect and request.session.uid:
			return http.redirect_with_hash(redirect)

		if not request.uid:
			request.uid = odoo.SUPERUSER_ID

		values = request.params.copy()
		try:
			values['databases'] = http.db_list()
		except odoo.exceptions.AccessDenied:
			values['databases'] = None

		if request.httprequest.method == 'POST':
			print('dsssssssssssssssd')
			old_uid = request.uid
			try:
				uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
				request.params['login_success'] = True
				current_user = request.env['res.users'].search([('id','=',uid)])

				student_application = request.env['odoocms.application'].sudo().search([('cnic', '=', current_user.login)])
				student = request.env['odoocms.student'].sudo().search([('partner_id', '=', current_user.partner_id.id)])
				faculty = request.env['odoocms.faculty.staff'].sudo().search([('partner_id', '=', current_user.partner_id.id)])

				if student and not faculty:
					return request.redirect('/student/dashboard')
				elif request.env.user.user_type == 'faculty' and request.env.user.has_group('base.group_portal'):
					return request.redirect('/faculty/dashboard')
				elif request.env.user.user_type == 'employee' and request.env.user.has_group('base.group_portal'):
					return request.redirect('/employee/dashboard')
				elif request.env.user.user_type == 'faculty' and request.env.user.has_group('base.group_user'):
					return request.redirect('/web#')
				elif request.env.user.has_group('base.group_user'):
					return request.redirect('/web#')
				else:
					print('admiss')
					return request.redirect('/admission/registration')
				return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))

			except odoo.exceptions.AccessDenied as e:
				request.uid = old_uid
				if e.args == odoo.exceptions.AccessDenied().args:
					values['error'] = _("Wrong login/password")
				else:
					values['error'] = e.args[0]
		else:
			print('sdddddddddddddddddd')
			if 'error' in request.params and request.params.get('error') == 'access':
				values['error'] = _('Only employee can access this database. Please contact the administrator.')

		if 'login' not in values and request.session.get('auth_login'):
			values['login'] = request.session.get('auth_login')

		if not odoo.tools.config['list_db']:
			values['disable_database_manager'] = True

		# otherwise no real way to test debug mode in template as ?debug =>
		# values['debug'] = '' but that's also the fallback value when
		# missing variables in qweb
		if 'debug' in values:
			values['debug'] = True

		response = request.render('web.login', values)
		response.headers['X-Frame-Options'] = 'DENY'

		#website web_login function
		if not redirect and request.params['login_success']:
			if request.env['res.users'].browse(request.uid).has_group('base.group_user'):
				redirect = b'/web?' + request.httprequest.query_string
			else:
				redirect = '/admission/registration'
			return http.redirect_with_hash(redirect)

		# auth_signup web_login function
		response.qcontext.update(self.get_auth_signup_config())
		if request.httprequest.method == 'GET' and request.session.uid and request.params.get('redirect'):
			# Redirect if already logged in and redirect param is present
			return http.redirect_with_hash(request.params.get('redirect'))

		return response

	@http.route('/web/reset_password', type='http', auth='public', website=True, sitemap=False)
	def web_auth_reset_password(self, *args, **kw):
		qcontext = self.get_auth_signup_qcontext()
		if not qcontext.get('token') and not qcontext.get('reset_password_enabled'):
			raise werkzeug.exceptions.NotFound()

		if 'error' not in qcontext and request.httprequest.method == 'POST':
			try:
				if qcontext.get('token'):
					self.do_signup(qcontext)
					return self.web_login(*args, **kw)
				else:
					login = qcontext.get('login')
					assert login, _("No login provided.")
					_logger.info(
						"Password reset attempt for <%s> by user <%s> from %s",
						login, request.env.user.login, request.httprequest.remote_addr)
					request.env['res.users'].sudo().reset_password(login)
					qcontext['message'] = _("An email has been sent with credentials to reset your password")
			except UserError as e:
				qcontext['error'] = e.name or e.value
			except SignupError:
				qcontext['error'] = _("Could not reset your password")
				_logger.exception('error when resetting password')
			except Exception as e:
				qcontext['error'] = str(e)

		response = request.render('auth_signup.reset_password', qcontext)
		response.headers['X-Frame-Options'] = 'DENY'
		return response
