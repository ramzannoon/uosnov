# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
from collections import OrderedDict

from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.tools.translate import _
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal
from odoo.addons.web.controllers.main import Binary



class CustomerPortal(CustomerPortal):

	# This function to check where this portal user is in faculty model or not. If yes: show links of faculty portal
	def _prepare_portal_layout_values(self):
		values = super(CustomerPortal, self)._prepare_portal_layout_values()
		partner = request.env.user.partner_id

		faculty = request.env['odoocms.faculty.staff']
		faculty_count = faculty.search_count([('partner_id', '=', partner.id)])

		Student = request.env['odoocms.student']
		student_count = Student.search_count([('partner_id', '=', partner.id)])

		current_user = http.request.env.user
		application = http.request.env['odoocms.application'].sudo().search([('cnic', '=', current_user.login)])

		values.update({
			'faculty_count': faculty_count,
			'student_count': student_count,
			'application': application,
			'title': "My Contact",
		})
		return values
