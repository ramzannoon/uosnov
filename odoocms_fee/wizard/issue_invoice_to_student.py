import pdb
import time
import datetime
from odoo import api, fields, models,_
from dateutil.relativedelta import relativedelta


class OdooCMSIssueInvoice(models.TransientModel):
	_name ='odoocms.issue.invoice'
	_description = 'Issue Invoice To Students'
				
	@api.model	
	def _get_invoicess(self):
		if self.env.context.get('active_model', False) == 'account.move' and self.env.context.get('active_ids', False):
			return self.env.context['active_ids']
		
	invoice_ids = fields.Many2many('account.move', string='Students',
		help="""Invoice Will issue to selected records only.""",default=_get_invoicess)


	def issue_invoice_to_students(self):
		for invoice in self.invoice_ids:
			if invoice.state =='draft':
				invoice.state = 'unpaid'
		return {'type': 'ir.actions.act_window_close'}
