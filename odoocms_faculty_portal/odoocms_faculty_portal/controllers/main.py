from odoo import http
from odoo.http import request
from datetime import date
import pdb


def prepare_portal_values(request):
	company = request.env.user.company_id
	partner = request.env.user.partner_id
	faculty_staff = http.request.env['odoocms.faculty.staff'].sudo().search([('user_partner_id', '=', partner.id)])
	if not faculty_staff:
		values = {
			'error_message' : 'Unauthorized Access',
		}
		return values, False, False
	else:
		# notifications = http.request.env['odoocms.notification'].sudo().search([
		# 	('expiry', '>', date.today()), ('visible_for', 'in', ['faculty', 'all']), ('allow_preview', '=', True)
		# ])
		sql = """SELECT DISTINCT recipient_id FROM notification_recipient_rel WHERE user_id = """ + str(faculty_staff.user_id.id)
		request.cr.execute(sql)
		returned_ids = request.cr.fetchall()
		recipient_list = []
		for rec in returned_ids:
			recipient_list.append(rec[0])

		notifications = http.request.env['cms.notification'].sudo().search([
			('expiry', '>', date.today()), ('visible_for', 'in', ['faculty', 'all']), '|', ('id', 'in', recipient_list), ('allow_preview', '=', True), ('alert', '=', False)
		])
		alerts = http.request.env['cms.notification'].sudo().search([
			('expiry', '>', date.today()), ('visible_for', 'in', ['faculty', 'all']), ('id', 'in', recipient_list), ('allow_preview', '=', True), ('alert', '=', True)
		])

		alerts = alerts.sorted(key=lambda r: r.date, reverse=True)
		noti = notifications.sorted(key=lambda r: r.date, reverse=True)
		
		config_term = http.request.env['ir.config_parameter'].sudo().get_param('odoocms.current_term')
		if config_term:
			config_term = int(config_term)
			term = request.env['odoocms.academic.term'].sudo().browse(int(config_term))
		else:
			config_term = 0
			term = 'Not Set'

		menus = http.request.env['odoocms.faculty.portal.menu'].sudo().search([],order='sequence')
		color = [    'md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
				     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
				     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
				     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
				     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400''md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400''md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400''md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400''md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400''md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400''md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400''md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
				     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
				     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
				     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
				     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400''md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400''md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400''md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400''md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400''md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400''md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400','md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400''md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400']

		values = {
			'menus': menus,
			'faculty_staff': faculty_staff,
			'partner': partner,
			'name': partner.name,
			'company': company or False,
			'notifications': noti,
			'config_term': config_term,
			'alerts':alerts,
			'color': color,
			'user': request.env.user,
			'term': term,
		}
	return values, True, faculty_staff