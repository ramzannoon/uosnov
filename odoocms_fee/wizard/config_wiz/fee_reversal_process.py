import pdb
import time
import datetime
from odoo import api, fields, models,_
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class OdooCMSProcessFeeReversal(models.TransientModel):
	_name ='odoocms.process.fee.reversal'
	_description = 'Process Fee reversal'
				
	@api.model	
	def _get_invoices(self):
		if self.env.context.get('active_model', False) == 'account.move' and self.env.context.get('active_ids', False):
			return self.env.context['active_ids']
			
	invoice_ids = fields.Many2many('account.move', string='Invoices',
		help="""Only selected Invoices will be Processed.""",default=_get_invoices)
	fee_head_ids = fields.Many2many('odoocms.fee.head', string='Fee Heads')
	description = fields.Text('Detailed Description',  required = True)
	

	def process_reversal(self):

		request_list = []
		for invoice in self.invoice_ids.filtered(lambda l: l.state == 'paid'):
			head_ids1 = self.fee_head_ids - invoice.invoice_line_ids.mapped('fee_head_id')
			head_ids2 = (self.fee_head_ids-head_ids1)
			if head_ids2:
				data = {
					'student_id': invoice.student_id.id,
					'invoice_id': invoice.id,
					'fee_head_ids': [(6,0, head_ids2.ids)],
					'date': datetime.date.today(),
					'description': self.description,

				}

				request = self.env['odoocms.fee.refund.request'].create(data)
				if request:
					request_list.append(request.id)
		if len(request_list)>0:
			form_view = self.env.ref('odoocms_fee.view_odoocms_student_fee_refund_request_form')
			tree_view = self.env.ref('odoocms_fee.view_odoocms_student_fee_refund_request_tree')
			return {
				'domain': [('id', 'in', request_list)],
				'name': _('Refund Requests'),
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'odoocms.fee.refund.request',
				'view_id': False,
				'views': [
					(tree_view and tree_view.id or False, 'tree'),
					(form_view and form_view.id or False, 'form'),
				],
			# 'context': {'default_class_id': self.id},
			'type': 'ir.actions.act_window'
			}

		return {'type': 'ir.actions.act_window_close'}

