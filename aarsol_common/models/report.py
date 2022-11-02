from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _
import pdb
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import content_disposition, Controller, request, route
import re


class CustomerPortalAARSOL(CustomerPortal):
	def _show_report(self, model, report_type, report_ref, download=False):
		if report_type not in ('html', 'pdf', 'text','docp'):
			raise UserError(_("Invalid report type: %s") % report_type)
		
		report_sudo = request.env.ref(report_ref).sudo()
		
		if not isinstance(report_sudo, type(request.env['ir.actions.report'])):
			raise UserError(_("%s is not the reference of a report") % report_ref)
		
		method_name = 'render_qweb_%s' % (report_type)
		report = getattr(report_sudo, method_name)([model.id], data={'report_type': report_type})[0]
		reporthttpheaders = [
			('Content-Type', 'application/pdf' if report_type in ('pdf','docp') else 'text/html'),
			('Content-Length', len(report)),
		]
		if report_type == 'pdf' and download:
			filename = "%s.pdf" % (re.sub('\W+', '-', model._get_report_base_filename()))
			reporthttpheaders.append(('Content-Disposition', content_disposition(filename)))
		return request.make_response(report, headers=reporthttpheaders)


class ReportAction(models.Model):
	_inherit = 'ir.actions.report'

	report_type = fields.Selection(selection_add=[
		('qweb-xls', 'XLS'),
		('qweb-ppt', 'PPT'),
		('qweb-pptp', 'PPT-PDF'),
		('qweb-doc', 'DOC'),
		('qweb-docp', 'DOC-PDF'),
		("fillpdf", "PDF Fill"),
	],  ondelete={'fillpdf': 'set default','qweb-xls': 'set default','qweb-ppt': 'set default','qweb-pptp': 'set default','qweb-doc': 'set default','qweb-docp': 'set default'} )

	def render_xlsx(self, docids, data):
		report_model_name = 'report.{}'.format(self.report_name)
		report_model = self.env.get(report_model_name)
		if report_model is None:
			raise UserError(_('%s model was not found' % report_model_name))
		return report_model.with_context({'active_model': self.model}).create_xlsx_report(docids, data)

	def _get_report_from_name(self, report_name):
		res = super(ReportAction, self)._get_report_from_name(report_name)
		if res:
			return res
		report_obj = self.env['ir.actions.report']
		qwebtypes = ['qweb-xls', 'qweb-ppt', 'qweb-pptp', 'qweb-doc', 'qweb-docp', 'fillpdf']
		conditions = [('report_type', 'in', qwebtypes), ('report_name', '=', report_name)]
		context = self.env['res.users'].context_get()
		return report_obj.with_context(context).search(conditions, limit=1)
	
	def render_qweb_xls(self, docids, data=None):
		"""This method generates and returns xls version of a report."""
		# If the report is using a custom model to render its html, we must use it. otherwise, fallback on the generic html rendering.
		report_model_name = 'report.{}'.format(self.report_name)
		report_model = self.env.get(report_model_name)
		
		if report_model is not None:
			data = report_model.make_excel(data)
		else:
			docs = self.env[self.model].browse(docids)
			data = {
				'doc_ids': docids,
				'doc_model': self.model,
				'docs': docs,
			}
			return self.render_template(self.report_name, data)
		return data
	
	def render_qweb_ppt(self, docids, data=None):
		"""This method generates and returns ppt version of a report."""
		# If the report is using a custom model to render its html, we must use it. otherwise, fallback on the generic html rendering.
		report_model_name = 'report.{}'.format(self.report_name)
		report_model = self.env.get(report_model_name)
		
		if report_model is not None:
			data = report_model.make_ppt(data)
		else:
			docs = self.env[self.model].browse(docids)
			data = {
				'doc_ids': docids,
				'doc_model': self.model,
				'docs': docs,
			}
			return docs.ppt5()
		return data
	
	def render_qweb_doc(self, docids, data=None):
		report_model_name = 'report.{}'.format(self.report_name)
		report_model = self.env.get(report_model_name)
		if report_model is None:
			raise UserError(_('%s model was not found' % report_model_name))
		return report_model.with_context({'active_model': self.model}).create_doc_report(docids, data)
	
	def render_qweb_docp(self, docids, data=None):
		report_model_name = 'report.{}'.format(self.report_name)
		report_model = self.env.get(report_model_name)
		if report_model is None:
			raise UserError(_('%s model was not found' % report_model_name))

		pdf_content = report_model.with_context({'active_model': self.model}).create_doc_report(docids, data)
		return pdf_content, 'pdf'