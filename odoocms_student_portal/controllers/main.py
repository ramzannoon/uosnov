from odoo import http
from odoo.http import request
from datetime import date
import pdb

def prepare_portal_values(request):
	user = request.env.user
	partner = user.partner_id
	#student = http.request.env['odoocms.student'].sudo().search([('partner_id', '=', partner.id)])
	student = user.student_id
	if not student:
		values = {
			'error_message' : 'Unauthorized Access',
		}
		return values, False, False
	else:
		# many to many relation
		sql = """ SELECT DISTINCT recipient_id FROM notification_recipient_rel WHERE user_id = """ + str(student.user_id.id)
		request.cr.execute(sql)
		returned_ids = request.cr.fetchall()
		recipient_list = []
		for rec in returned_ids:
			recipient_list.append(rec[0])
		notifications = http.request.env['cms.notification'].sudo().search([
			('expiry', '>', date.today()), ('visible_for', 'in', ['student', 'all']), '|', ('id', 'in', recipient_list), ('allow_preview', '=', True), ('alert', '=', False)
		])
		alerts = http.request.env['cms.notification'].sudo().search([
			('expiry', '>', date.today()), ('visible_for', 'in', ['student', 'all']), ('id', 'in', recipient_list), ('allow_preview', '=', True), ('alert', '=', True)
		])
		notifications = notifications.sorted(key=lambda r: r.date, reverse=True)
		alerts = alerts.sorted(key=lambda r: r.date, reverse=True)
		config_term = http.request.env['ir.config_parameter'].sudo().get_param('odoocms.current_term')
		if config_term:
			term = request.env['odoocms.academic.term'].sudo().browse(int(config_term))
		else:
			term = student.term_id
		menus = http.request.env['odoocms.student.portal.menu'].sudo().search([], order='sequence')
		values = {
			'menus': menus,
			'student': student,
			'company': user.company_id,
			'notifications': notifications,
			'alerts':alerts,
			'term': term,
			'partner': partner
		}
	return values, True, student