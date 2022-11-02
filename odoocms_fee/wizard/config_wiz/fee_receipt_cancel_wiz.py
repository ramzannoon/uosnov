from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import pdb


class FeeReceiptCancel(models.TransientModel):
    _name = 'fee.receipt.cancel.wiz'
    _description = """This Wizard will Cancel all the Fee Receipts That are in Draft Status. System will check that 
                        if the Receipt are not in the Draft Status Skip it."""

    @api.model
    def _get_receipts(self):
        receipts = []
        if self._context.get('active_model', False)=='account.move' and self._context.get('active_ids', False):
            receipt_ids = self.env['account.move'].search([('id', 'in', self._context.get('active_ids')), ('invoice_payment_state', 'in', ('not_paid', 'open', 'unpaid'))])
            if receipt_ids:
                receipts = [(6, 0, receipt_ids.ids)]
        return receipts

    receipt_ids = fields.Many2many('account.move', 'fee_receipt_cancel_wiz_rel', 'wiz_id', 'invoice_id', default=_get_receipts)
    show_detail = fields.Boolean('Show', compute='compute_show', store=True)

    @api.depends('receipt_ids')
    def compute_show(self):
        for rec in self:
            if len(rec.receipt_ids) >= 1:
                rec.show_detail = True
            else:
                rec.show_detail = False

    def action_cancel_receipt(self):
        for rec in self:
            for receipt in rec.receipt_ids:
                receipt.button_cancel()
