import time
import datetime
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, UserError
import pdb
import logging

_logger = logging.getLogger(__name__)


class OdooCMSReceiptFeeHeadRemoval(models.Model):
    _name = 'odoocms.receipt.fee.head.removal'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Fee Receipts Fee Head Removal"

    def _get_tax_id(self):
        tax_id = self.env['odoocms.fee.head'].search([('name', '=', 'Advance Tax')])
        if tax_id:
            return tax_id.id
        return False

    name = fields.Char(string='Name')
    sequence = fields.Integer('Sequence')
    date = fields.Date('Date', default=fields.Date.today(), trace=True, index=True)
    fee_head_id = fields.Many2one('odoocms.fee.head', 'Fee Head', tracking=True, index=True, default=_get_tax_id)
    invoice_ids = fields.Many2many('account.move', 'fee_head_removal_invoice_rel', 'fee_head_removal_id', 'invoice_id', 'Fee Receipts')
    state = fields.Selection([('draft', 'Draft'),
                              ('approve', 'Approved'),
                              ('done', 'Done'),
                              ('reject', 'Rejected'), ], string='Status', default='draft', indedx=True)
    remarks = fields.Text('Remarks')

    @api.model
    def create(self, values):
        if not values.get('sequence', False):
            values['name'] = self.env['ir.sequence'].next_by_code('odoocms.receipt.fee.head.removal')
        result = super(OdooCMSReceiptFeeHeadRemoval, self).create(values)
        return result

    def unlink(self):
        for rec in self:
            if not rec.state=='draft':
                raise UserError('You can Delete records in Draft State only.')
        return super(OdooCMSReceiptFeeHeadRemoval, self).unlink()

    def action_approve(self):
        for rec in self:
            if not rec.invoice_ids:
                raise UserError(_("Please Enter the Fee Receipts."))
            rec.state = 'approve'

    def action_done(self):
        for rec in self:
            for invoice in rec.invoice_ids:
                head_to_remove = invoice.invoice_line_ids.filtered(lambda inv: inv.fee_head_id.id==rec.fee_head_id.id)
                if head_to_remove:
                    tax_amt = head_to_remove.credit
                    receivable_entry = invoice.line_ids.filtered(lambda inv: inv.account_id.user_type_id.name=="Receivable")
                    amount1 = receivable_entry.debit - tax_amt
                    head_to_remove.move_id.state = 'draft'

                    # Update Receivable entry
                    self.env.cr.execute("update account_move_line set price_unit = %s, debit=%s, balance=%s, price_subtotal=%s, price_total=%s, amount_residual=%s where id=%s \n"
                        , (-amount1, amount1, amount1, -amount1, -amount1, amount1, receivable_entry.id))

                    # Update invoice Total
                    self.env.cr.execute("update account_move set amount_untaxed=%s,amount_total = %s,amount_residual=%s, amount_untaxed_signed=%s, amount_total_signed=%s, amount_residual_signed=%s where id=%s \n"
                        , (amount1, amount1, amount1, amount1, amount1, amount1, invoice.id))

                    head_to_remove.unlink()
                    # invoice.line_ids = [(2, head_to_remove.id)]
                    if invoice.student_ledger_id:
                        invoice.student_ledger_id.credit = invoice.student_ledger_id.credit - tax_amt
                    invoice.action_post()
                    invoice.action_invoice_send()
            rec.state = 'done'

    def action_reject(self):
        for rec in self:
            rec.state = 'reject'
