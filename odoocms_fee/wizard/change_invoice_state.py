import pdb
import time
import datetime
from odoo import api, fields, models,_
from dateutil.relativedelta import relativedelta


class OdooCMSChangeInvoiceState(models.TransientModel):
	_name ='odoocms.invoice.state.change'
	_description = 'Change Invoice State'
				
	@api.model	
	def _get_invoices(self):
		if self.env.context.get('active_model', False) == 'account.move' and self.env.context.get('active_ids', False):
			return self.env.context['active_ids']
			
	invoice_ids = fields.Many2many('account.move', string='Invoices',
		help="""Only selected Invoices will be Processed.""",default=_get_invoices)
	state = fields.Selection(
		[('draft', 'Draft'),], string='Status',
		default='draft')
	
	# rule_id = fields.Many2one('odoocms.student.change.state.rule', string = "Reason",)


	def change_invoice_state(self):
		for invoice in self.invoice_ids:
			if invoice.state == 'unpaid':
				invoice.state = 'draft'
				
		return {'type': 'ir.actions.act_window_close'}



