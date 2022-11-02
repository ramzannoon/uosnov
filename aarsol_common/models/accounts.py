import time
import pdb
from odoo.osv import expression
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _
from itertools import groupby
from odoo.tools import pycompat
import base64

import odoo.tools as tools
from odoo import http
import openerp.addons.web.controllers.main as main
import json
import werkzeug
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
from collections import OrderedDict
from werkzeug.urls import url_decode, iri_to_uri
from odoo.tools import html_escape, pycompat
from odoo.tools.safe_eval import safe_eval

from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception as _serialize_exception, Response

def serialize_exception(f):
	@functools.wraps(f)
	def wrap(*args, **kwargs):
		try:
			return f(*args, **kwargs)
		except Exception as e:
			_logger.exception("An exception occured during an http request")
			se = _serialize_exception(e)
			error = {
				'code': 200,
				'message': "Odoo Server Error",
				'data': se
			}
			return werkzeug.exceptions.InternalServerError(json.dumps(error))
	return wrap
    
def grouplines(self, ordered_lines, sortkey):
	grouped_lines = []
	for key, valuesiter in groupby(ordered_lines, sortkey):
		group = {}
		group['category'] = key
		group['lines'] = list(v for v in valuesiter)

		grouped_lines.append(group)
	return grouped_lines


class Company(models.Model):
    _inherit = 'res.company'

    product_printer = fields.Char()
    location_printer = fields.Char()
    shipping_printer = fields.Char()
    product_height = fields.Float(string="Product Height", default=1.0)
    product_width = fields.Float(string="Product Width", default=1.25)
    location_height = fields.Float(string="Location Height", default=1.0)
    location_width = fields.Float(string="Location Width", default=1.25)
    shipping_height = fields.Float(string="Shipping Height", default=1.0)
    shipping_width = fields.Float(string="Shipping Width", default=1.25)
    print_onreceive_product = fields.Boolean(string='Print When Receive Product', help='Print Product Label When Receive Product')
    printer_type = fields.Selection([('zpl', 'ZPL'), ('epl', 'EPL')], string="Type", default="zpl")


class Picking(models.Model):
    _inherit = "stock.picking"

    print_onreceive_product = fields.Boolean(related='company_id.print_onreceive_product', string='Print When Receive Product', help='Print Product Label When Receive Product', store=True)


class MailTemplate(models.Model):
	_inherit = "mail.template"
	

	def generate_recipients(self, results, res_ids):
		"""Generates the recipients of the template. Default values can ben generated
		instead of the template values if requested by template or context.
		Emails (email_to, email_cc) can be transformed into partners if requested
		in the context. """
		self.ensure_one()

		if self.use_default_to or self._context.get('tpl_force_default_to'):
			default_recipients = self.env['mail.thread'].message_get_default_recipients(res_model=self.model, res_ids=res_ids)
			for res_id, recipients in default_recipients.items():
				results[res_id].pop('partner_to', None)
				results[res_id].update(recipients)

		for res_id, values in results.items():
			partner_ids = values.get('partner_ids', list())
			if self._context.get('tpl_partners_only'):
				mails = tools.email_split(values.pop('email_to', '')) + tools.email_split(values.pop('email_cc', ''))
				for mail in mails:
					partner_id = self.env['res.partner'].find_or_create(mail)
					partner_ids.append(partner_id)
			partner_to = values.pop('partner_to', '')
			if partner_to:
				# placeholders could generate '', 3, 2 due to some empty field values
				tpl_partner_ids = [int(pid) for pid in partner_to.split(',') if pid]
				partner_ids += self.env['res.partner'].sudo().browse(tpl_partner_ids).exists().ids
				#Add By AARSOL For For user to add in it.
				partner_ids += self.env.user.partner_id and self.env.user.partner_id.ids
			results[res_id]['partner_ids'] = partner_ids
		return results
	

	def generate_email(self, res_ids, fields=None):
		"""Generates an email from the template for given the given model based on
			records given by res_ids.

		:param template_id: id of the template to render.
		:param res_id: id of the record to use for rendering the template (model 
			is taken from template definition)
		:returns: a dict containing all relevant fields for creating a new
			mail.mail entry, with one extra key ``attachments``, in the
				format [(report_name, data)] where data is base64 encoded.
		"""
		
		self.ensure_one()
		multi_mode = True
		if isinstance(res_ids, pycompat.integer_types):
			res_ids = [res_ids]
			multi_mode = False
		if fields is None:
			fields = ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to', 'scheduled_date']
		
		res_ids_to_templates = self.get_email_template(res_ids)

		# templates: res_id -> template; template -> res_ids
		templates_to_res_ids = {}
		for res_id, template in res_ids_to_templates.items():
			templates_to_res_ids.setdefault(template, []).append(res_id)

		results = dict()
		for template, template_res_ids in templates_to_res_ids.items():
			Template = self.env['mail.template']
			# generate fields value for all res_ids linked to the current template
			if template.lang:
				Template = Template.with_context(lang=template._context.get('lang'))
			for field in fields:
				Template = Template.with_context(safe=field in {'subject'})
				generated_field_values = Template.render_template(
					getattr(template, field), template.model, template_res_ids,
					post_process=(field == 'body_html'))
				for res_id, field_value in generated_field_values.items():
					results.setdefault(res_id, dict())[field] = field_value
			# compute recipients
			if any(field in fields for field in ['email_to', 'partner_to', 'email_cc']):
				results = template.generate_recipients(results, template_res_ids)
			# update values for all res_ids
			for res_id in template_res_ids:
				values = results[res_id]
				# body: add user signature, sanitize
				if 'body_html' in fields and template.user_signature:
					signature = self.env.user.signature
					if signature:
						values['body_html'] = tools.append_content_to_html(values['body_html'], signature, plaintext=False)
				if values.get('body_html'):
					values['body'] = tools.html_sanitize(values['body_html'])
				# technical settings
				values.update(
					mail_server_id=template.mail_server_id.id or False,
					auto_delete=template.auto_delete,
					model=template.model,
					res_id=res_id or False,
					attachment_ids=[attach.id for attach in template.attachment_ids],
				)

            # Add report in attachments: generate once for all template_res_ids
			if template.report_template:
				for res_id in template_res_ids:
					attachments = []
					report_name = self.render_template(template.report_name, template.model, res_id)
					report = template.report_template
					report_service = report.report_name

					if report.report_type not in ['qweb-html', 'qweb-pdf','qweb-pptp']:
						raise UserError(_('Unsupported report type %s found.') % report.report_type)
					
					if report.report_type == 'qweb-pptp':
						result = report.render_qweb_ppt([res_id])
						format = 'pdf'
					else:	
						result, format = report.render_qweb_pdf([res_id])

					# TODO in trunk, change return format to binary to match message_post expected format
					result = base64.b64encode(result)
					if not report_name:
						report_name = 'report.' + report_service
					ext = "." + format
					if not report_name.endswith(ext):
						report_name += ext
					attachments.append((report_name, result))
					results[res_id]['attachments'] = attachments
		return multi_mode and results or results[res_ids[0]]
		




