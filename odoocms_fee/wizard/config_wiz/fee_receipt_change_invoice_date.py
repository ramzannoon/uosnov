from odoo import api, fields, models
from odoo.exceptions import UserError


class FeeReceiptChangeInvoiceDate(models.TransientModel):
    _name = 'fee.receipt.change.invoice.date'
    _description = 'Change Invoice Date'

    @api.model
    def _get_invoice(self):
        if self.env.context.get('active_model', False)=='account.move' and self.env.context.get('active_id', False):
            return self.env.context['active_id']

    @api.model
    def _get_prev_due_date(self):
        if self.env.context.get('active_model', False)=='account.move' and self.env.context.get('active_id', False):
            invoice_id = self.env['account.move'].search([('id', '=', self.env.context.get('active_id'))])
            return invoice_id.invoice_date_due

    invoice_id = fields.Many2one('account.move', string='Invoice', default=_get_invoice)
    prev_due_date = fields.Date('Previous Due Date', default=_get_prev_due_date)
    new_due_date = fields.Date('Due Date')

    def change_invoice_date(self):
        if self.invoice_id:
            if self.invoice_id.invoice_payment_state in ('in_payment', 'paid'):
                raise UserError('You cannot Change the Due Date of the Paid Fee Receipts.')
            if self.invoice_id.invoice_payment_state=='cancel':
                raise UserError('You cannot Change the Due Date of the Cancelled Fee Receipts.')
            if self.new_due_date < fields.Date.today():
                raise UserError('Cannot Assign the Previous Date as Due Date.')
            self.invoice_id.invoice_date_due = self.new_due_date
            for line in self.invoice_id.line_ids:
                if line.date_maturity:
                    line.date_maturity = self.new_due_date
            body = 'Invoice Due Date is changed from %s to %s' % (self.prev_due_date.strftime("%d/%m/%Y"), self.new_due_date.strftime("%d/%m/%Y"))
            self.invoice_id.message_post(body=body)
        return {'type': 'ir.actions.act_window_close'}
