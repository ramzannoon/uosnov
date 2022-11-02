# -*- coding: utf-8 -*-


import pdb
from odoo import http, tools, _, SUPERUSER_ID
from odoo.http import content_disposition, Controller, request, route, dispatch_rpc

from odoo.addons.portal.controllers.web import Home
from odoo.addons.website.controllers.main import Website


#class CustomerPortal(Controller):
#	@route(['/my', '/my/home'], type='http', auth="user", website=True)
#	def home(self, **kw):
#		user = request.env['res.users'].browse(request.uid)
		# employee = request.env['odoocms.faculty.staff'].sudo().search([('user_id', '=', user.id)])
		# student = request.env['odoocms.student'].sudo().search([('user_id', '=', user.id)])
#		
#		if user.has_group('base.group_portal'):
#			if user.user_type:
#				return request.redirect('/' + user.user_type + '/dashboard')
#			else:
#				data = {
#					'name': 'login',
#					'description': 'Resource Mapping',
#					'state': 'submit',
#				}
#				request.env['odoocms.error.reporting'].sudo().create(data)
#				values = {
#					'error_message': 'Your Account is not mapped with any resource, Contact System Administrator',
#				}
#				return request.render("odoocms_web.portal_error", values)
#		redirect = b'/web?' + request.httprequest.query_string
#		return http.redirect_with_hash(redirect)


# class CWebsite(Website):
# 	@http.route(auth='public')
# 	def index(self, data={},**kw):
# 		super(CWebsite, self).index(**kw)
# 		return http.request.render('<your_addon>.<your_template_id>', data)
  
  
class MyWebsite(Home):
	@http.route(website=True, auth="public", sitemap=False)
	def web_login(self, redirect=None, *args, **kw):
		response = super(MyWebsite, self).web_login(redirect=redirect, *args, **kw)
		if not redirect and request.params['login_success']:
			user = request.env['res.users'].browse(request.uid)
			
			# employee = request.env['odoocms.faculty.staff'].sudo().search([('user_id', '=', user.id)])
			# student = request.env['odoocms.student'].sudo().search([('user_id', '=', user.id)])
			if user.has_group('base.group_portal') and user.user_type != 'employee':
				return request.redirect('/'+user.user_type+'/dashboard')
			else:
				return request.redirect('/my')
			
			redirect = b'/web?' + request.httprequest.query_string
			return http.redirect_with_hash(redirect)
			
			# if user.has_group('base.group_portal') and user.user_type == 'faculty':
			# 	return request.redirect('/faculty/dashboard')
			# if user.has_group('base.group_portal') and user.user_type == 'student':
			# 	return request.redirect('/student/dashboard')
			# if user.has_group('base.group_portal') and user.user_type == 'employee':
			# 	return request.redirect('/employee/dashboard')
			# if user.has_group('base.group_portal') and user.user_type == 'external':
			# 	return request.redirect('/external/dashboard')
			
			
			# return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
			
			# if request.env['res.users'].browse(request.uid).has_group('base.group_user'):
			# 	redirect = b'/web?' + request.httprequest.query_string
			# else:
			# 	redirect = '/my'
			# return http.redirect_with_hash(redirect)
		return response



	
# class Home(Home):
# 	# we added auth="public" and added website inherited code below
# 	@http.route('/web/login', type='http', auth="public", sitemap=False)
# 	def web_login(self, redirect=None, **kw):
# 		main.ensure_db()
# 		request.params['login_success'] = False
# 		if request.httprequest.method == 'GET' and redirect and request.session.uid:
# 			return http.redirect_with_hash(redirect)
#
# 		if not request.uid:
# 			request.uid = odoo.SUPERUSER_ID
#
# 		values = request.params.copy()
# 		try:
# 			values['databases'] = http.db_list()
# 		except odoo.exceptions.AccessDenied:
# 			values['databases'] = None
#
# 		if request.httprequest.method == 'POST':
# 			old_uid = request.uid
# 			try:
# 				uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
# 				request.params['login_success'] = True
#
# 				user = request.env['res.users'].browse(request.uid)
# 				employee = request.env['odoocms.faculty.staff'].sudo().search([('user_id', '=', user.id)])
# 				ext_employee = request.env['odoocms.external.staff'].sudo().search([('user_id', '=', user.id)])
# 				student = request.env['odoocms.student'].sudo().search([('user_id', '=', user.id)])
#
# 				# teacher = request.env['hr.employee']
# 				# if employee and employee.job_id and employee.job_id.name == 'Class Teacher':
# 				# 	teacher = employee
#
# 				if user.has_group('base.group_portal') and ext_employee:
# 					return request.redirect('/external/profile')
# 				if user.has_group('base.group_portal') and employee:
# 					return request.redirect('/faculty/profile')
# 				if user.has_group('base.group_portal') and student:
# 					return request.redirect('/student/profile')
# 				return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
#
# 			except odoo.exceptions.AccessDenied as e:
# 				request.uid = old_uid
# 				if e.args == odoo.exceptions.AccessDenied().args:
# 					values['error'] = _("Wrong login/password")
# 				else:
# 					values['error'] = e.args[0]
# 		else:
# 			if 'error' in request.params and request.params.get('error') == 'access':
# 				values['error'] = _('Only employee can access this database. Please contact the administrator.')
#
# 		if 'login' not in values and request.session.get('auth_login'):
# 			values['login'] = request.session.get('auth_login')
#
# 		if not odoo.tools.config['list_db']:
# 			values['disable_database_manager'] = True
#
# 		# otherwise no real way to test debug mode in template as ?debug =>
# 		# values['debug'] = '' but that's also the fallback value when
# 		# missing variables in qweb
# 		if 'debug' in values:
# 			values['debug'] = True
#
# 		response = request.render('web.login', values)
# 		response.headers['X-Frame-Options'] = 'DENY'
#
# 		#website web_login function
# 		if not redirect and request.params['login_success']:
# 			if request.env['res.users'].browse(request.uid).has_group('base.group_user'):
# 				redirect = b'/web?' + request.httprequest.query_string
# 			else:
# 				if request.env['res.users'].browse(request.uid).has_group('base.group_portal'):
# 					redirect = '/my/dashboard'
# 				else:
# 					redirect = '/my'
# 			return http.redirect_with_hash(redirect)
#
# 		# auth_signup web_login function
# 		response.qcontext.update(self.get_auth_signup_config())
# 		if request.httprequest.method == 'GET' and request.session.uid and request.params.get('redirect'):
# 			# Redirect if already logged in and redirect param is present
# 			return http.redirect_with_hash(request.params.get('redirect'))
#
# 		return response
#
