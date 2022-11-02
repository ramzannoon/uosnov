import pdb
import time
import datetime
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta


class OdooCMSSpliteInvoiceLines(models.TransientModel):
    _name = 'odoocms.split.invoice.lines'
    _description = 'Split Invoice Lines'

    invoice_line = fields.Many2one('account.move.line', 'Fee Head')
    amount = fields.Float('Amount')
    percentage = fields.Integer('Percentage')
    amount1 = fields.Float('1st Invoice', compute='_get_amount')
    amount2 = fields.Float('2nd Invoice', compute='_get_amount')

    @api.depends('amount', 'percentage')
    def _get_amount(self):
        for rec in self:
            if rec.percentage < 0:
                rec.percentage = 0
            if rec.percentage > 100:
                rec.percentage = 100

            rec.amount1 = rec.amount * rec.percentage / 100.0
            rec.amount2 = rec.amount - rec.amount1


class OdooCMSSpliteInvoice(models.TransientModel):
    _name = 'odoocms.split.invoice'
    _description = 'Split Invoice'

    @api.model
    def _get_invoice(self):
        if self.env.context.get('active_model', False)=='account.move' and self.env.context.get('active_id', False):
            return self.env.context['active_id']

    @api.model
    def _get_invoice_lines(self):
        if self.env.context.get('active_model', False)=='account.move' and self.env.context.get('active_id', False):
            invoice_id = self.env.context['active_id']
            lines = self.env['odoocms.split.invoice.lines']
            for line in self.env['account.move'].browse(invoice_id).invoice_line_ids:
                data = {
                    'invoice_line': line.id,
                    'amount': line.price_subtotal,
                    'percentage': 100,
                    'amount1': line.price_subtotal,
                }
                lines += self.env['odoocms.split.invoice.lines'].create(data)
            return lines.ids

    @api.model
    def _get_total_amount(self):
        total = 0
        if self.env.context.get('active_model', False)=='account.move' and self.env.context.get('active_id', False):
            invoice_id = self.env.context['active_id']
            for line in self.env['account.move'].browse(invoice_id).invoice_line_ids:
                total += line.price_subtotal
            return total

    @api.depends('total_amount', 'amount_percentage')
    def _get_per_amount(self):
        if self.amount_percentage:
            intallment_total = 0
            total1 = 0
            total2 = 0
            self.per_amount = self.total_amount * self.amount_percentage / 100.0
            for rec in self.line_ids:
                intallment_total += rec.amount
                if intallment_total < self.per_amount:
                    rec.percentage = 100
                    total1 += rec.amount
                else:
                    rec.percentage = 0
                    total2 += rec.amount
                rec._get_amount()

            self.total1 = total1
            self.total2 = total2

    invoice_id = fields.Many2one('account.move', string='Invoices', default=_get_invoice)
    date_due1 = fields.Date('Due Date (First)', default=(fields.Date.today() + relativedelta(days=7)))
    date_due2 = fields.Date('Due Date (Second)', default=(fields.Date.today() + relativedelta(days=37)))

    amount_percentage = fields.Selection([('25', '25%'), ('50', '50%'), ('75', '75%')], string='Amount Percentage')

    total_amount = fields.Float('Total amount', readonly=True, default=_get_total_amount)
    per_amount = fields.Float('Percentaged Amount', compute='_get_per_amount', readonly=True)
    total1 = fields.Float('1st Invoice Total', readonly=True, )
    total2 = fields.Float('2nd Invoice Total', readonly=True, )

    line_ids = fields.Many2many('odoocms.split.invoice.lines', string='Invoice Lines', default=_get_invoice_lines)


    def split_invoice(self):
        for rec in self:
            invoices = rec.invoice_id
            split_need = any([line.amount2 > 0 for line in rec.line_ids])
            if not split_need:
                return {'type': 'ir.actions.act_window_close'}

            date_invoice = fields.Date.context_today(self)

            fee_structure = rec.invoice_id.fee_structure_id
            sequence = fee_structure.journal_id.sequence_id
            new_name = sequence.with_context(ir_sequence_date=date_invoice).next_by_id()

            new_invoice = rec.invoice_id.copy(
                default={
                    'state': 'draft',
                    'date_due': rec.date_due2,
                    'date_invoice': date_invoice,
                    'number': new_name,
                    'invoice_line_ids': False}
            )
            new_invoice.back_invoice = rec.invoice_id.id
            rec.invoice_id.forward_invoice = new_invoice.id
            rec.invoice_id.state = 'draft'
            invoices += new_invoice

            for line in rec.line_ids:
                if line.amount2 > 0:
                    analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.invoice_line.analytic_tag_ids]
                    fee_line = {
                        'price_unit': line.amount2,
                        'quantity': 1.00,
                        'product_id': line.invoice_line.product_id.id,
                        'name': line.invoice_line.name,
                        'account_id': line.invoice_line.account_id.id,
                        # 'account_analytic_id': line.fee_head_id.account_analytic_id,
                        'analytic_tag_ids': analytic_tag_ids,
                        'invoice_id': new_invoice.id
                    }
                    if line.amount1 > 0:
                        line.invoice_line.price_unit = line.amount1
                    else:
                        line.invoice_line.unlink()

                    self.env['account.move.line'].create(fee_line)

            for inv in invoices:
                inv.state = 'unpaid'

        if invoices:
            invoice_list = invoices.mapped('id')
            form_view = self.env.ref('odoocms_fee.odoocms_receipt_form')
            tree_view = self.env.ref('odoocms_fee.odoocms_receipt_tree')
            return {
                'domain': [('id', 'in', invoice_list)],
                'name': _('Invoices'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'view_id': False,
                'views': [
                    (tree_view and tree_view.id or False, 'tree'),
                    (form_view and form_view.id or False, 'form'),
                ],
                # 'context': {'default_class_id': self.id},
                'type': 'ir.actions.act_window'
            }
        else:
            return {'type': 'ir.actions.act_window_close'}
