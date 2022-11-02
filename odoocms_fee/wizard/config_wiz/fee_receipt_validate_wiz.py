from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import pdb


class FeeReceiptValidate(models.TransientModel):
    _name = 'fee.receipt.validate.wiz'
    _description = """This Wizard will Shift all the Fee Receipts That are in Unpaid State to the 'Open' State. System will check that 
                        if the Receipt are in the Unpaid State then Change otherwise Skip it."""

    @api.model
    def _get_receipts(self):
        receipts = []
        if self._context.get('active_model', False)=='account.move' and self._context.get('active_ids', False):
            receipt_ids = self.env['account.move'].search([('id', 'in', self._context.get('active_ids')), ('invoice_payment_state', '=', 'not_paid')])
            if receipt_ids:
                receipts = [(6, 0, receipt_ids.ids)]
        return receipts

    receipt_ids = fields.Many2many('account.move', default=_get_receipts)
    show_detail = fields.Boolean('Show', compute='compute_show', store=True)

    @api.depends('receipt_ids')
    def compute_show(self):
        for rec in self:
            if len(rec.receipt_ids) >= 1:
                rec.show_detail = True
            else:
                rec.show_detail = False

    def action_post_receipt(self):
        for rec in self:
            for receipt in rec.receipt_ids:
                if not receipt.name=='/':
                    is_already_exist = self.env['account.move'].search([('name', '=', receipt.name)])
                    if is_already_exist:
                        # Get the journal's sequence.
                        sequence = receipt._get_sequence()
                        if not sequence:
                            raise UserError(_('Please define a sequence on your journal.'))
                        receipt.name = sequence.with_context(ir_sequence_date=receipt.date).next_by_id()
                receipt.action_post()
                # Moved these two Lines into the action_post Method
                # receipt.send_fee_receipt_email()
                # receipt.send_fee_receipt_sms()
