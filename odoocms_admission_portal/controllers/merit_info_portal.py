import base64

from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal
from odoo.addons.web.controllers.main import Binary
import json
import pdb
from datetime import date


class CustomerPortalMeritList(CustomerPortal):

	@http.route(['/my/merit'], type='http', auth="user", website=True)
	def portal_applicant_merit_info(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):

		current_user = http.request.env.user
		application = http.request.env['odoocms.application'].sudo().search([('cnic', '=', current_user.login)])
		admission_reg = http.request.env['odoocms.admission.register'].sudo().search([('id','=',application.register_id.id)])

		applicant_merit = http.request.env['odoocms.application.merit'].sudo().search([
			('application_id', '=', application.id),
			('merit_register_id','=',admission_reg.merit_register_id.id)
		])

		locked_application = http.request.env['odoocms.application.merit'].sudo().search([
			('application_id', '=', application.id),
			('locked', '=', True)
		])

		cancelled_application = http.request.env['odoocms.application.merit'].sudo().search([
			('application_id', '=', application.id),
			('state', 'in', ('cancel','reject','absent'))
		])
		allocation_lines = admission_reg.allocation_id.seat_ids.filtered(lambda l: l.program_id in application.preference_ids.mapped('program_id'))
		quota_ids = http.request.env['odoocms.admission.quota']
		if application.quota_id:
			quota_ids += application.quota_id
		if application.quota_id2:
			quota_ids += application.quota_id2

		allocation_lines = allocation_lines.filtered(lambda l: l.category == 'open_merit' or l.quota_id in quota_ids)

		values = {
			'applicant_merit': applicant_merit.filtered(lambda l: l.merit_register_id.state == 'open'),
			'applicant':application,
			'default_url': '/my/merit',
			'locked_application':locked_application,
			'cancelled_application':cancelled_application,
			'admission_reg': admission_reg,
			'today':date.today(),
			'allocation_lines': allocation_lines,
		}
		return request.render("odoocms_admission_portal.portal_applicant_merit", values)

	@http.route('/save/admission/voucher', csrf=False, type="http", methods=['POST', 'GET'], auth="public", website=True)
	def save_voucher(self, **kw):
		current_user = http.request.env.user
		voucher_image = kw.get('voucher_image',False)
		voucher_number = kw.get('voucher_number', False)
		date_voucher = kw.get('date_voucher', False)
		applicant_merit = int(kw.get('applicant_merit', 0))
		lock_seat = kw.get('lock_seat')
		if lock_seat == 'yes':
			locked = True
		else:
			locked = False

		applicant_merit_id = http.request.env['odoocms.application.merit'].sudo().search([('id','=',applicant_merit)])

		if applicant_merit_id and applicant_merit_id.merit_register_id.date_end < date.today():
			values = {
				'header': 'Error',
				'message': 'Date Over! Last date of fee details submission was:'+ str(applicant_merit_id.merit_register_id.date_end)
			}
			return request.render("odoocms_admission_portal.submission_message", values)
		if applicant_merit_id and not applicant_merit_id.voucher_status and applicant_merit_id.state == 'draft':
			values = {
				'voucher_image':base64.encodestring(voucher_image.read()),
				'voucher_number': voucher_number,
				'date_voucher': date_voucher,
				'date_submission': date.today(),
				'locked': locked,
			}
			applicant_merit_id.write(values)
			return request.redirect('/my/merit')
		else:
			values = {
				'header':'Error',
				'message':'Something went wrong. Details are not submitted!'
			}
			return request.render("odoocms_admission_portal.submission_message", values)

	@http.route('/download/admission/feevoucher', csrf=False, type="http", methods=['POST', 'GET'], auth="public", website=True)
	def download_admission_fee_voucher(self, **kw):
		current_user = http.request.env.user

		application = http.request.env['odoocms.application'].sudo().search([('cnic', '=', current_user.login)])
		return application._show_report(model=application, report_type='pdf', report_ref='odoocms_admission_portal.student_admission_invoice', download=True)


	