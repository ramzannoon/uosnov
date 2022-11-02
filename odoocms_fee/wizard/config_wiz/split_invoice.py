import pdb
import time
import datetime
import math
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class OdooCMSSplitInvoice(models.TransientModel):
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

            if self.env['account.move'].browse(invoice_id).invoice_payment_state not in ('not_paid', 'unpaid', 'open'):
                raise UserError(_('Paid Invoice Cannot be Split.'))

            for line in self.env['account.move'].browse(invoice_id).invoice_line_ids:
                amt1 = 0
                amt2 = 0
                if line.fee_category_id.name=='Tuition Fee':
                    install_no = 1 if self.install_no==0 else self.self.install_no
                    if line.price_subtotal > 0:
                        amt1 = math.ceil(line.price_subtotal / install_no)
                        amt2 = amt1
                else:
                    amt1 = line.price_subtotal
                    amt2 = 0

                data = {
                    'fee_description': line.name,
                    'invoice_line': line.id,
                    'fee_category_id': line.fee_category_id.id,
                    'amount': line.price_subtotal,
                    'amount1': amt1,
                    'amount2': amt2,
                    'split_wiz_id': self.id,
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

    @api.model
    def _get_total_amount2(self):
        total = 0
        if self.env.context.get('active_model', False)=='account.move' and self.env.context.get('active_id', False):
            invoice_id = self.env.context['active_id']

            for line in self.env['account.move'].browse(invoice_id).invoice_line_ids:
                if line.fee_category_id.name=='Tuition Fee':
                    total += line.price_subtotal
            return total

    invoice_id = fields.Many2one('account.move', string='Invoices', default=_get_invoice)
    date_due1 = fields.Date('Due Date (First)', default=(fields.Date.today() + relativedelta(days=7)))
    date_due2 = fields.Date('Due Date (Second)', default=(fields.Date.today() + relativedelta(days=37)))
    total_amount = fields.Float('Total Invoice Amount', readonly=True, default=_get_total_amount)
    total_installable_amount = fields.Float('Total Installable Amount', readonly=True, default=_get_total_amount2)
    total1 = fields.Float('1st Invoice Amount', readonly=True)
    total2 = fields.Float('Installment Amount', readonly=True)
    install_no = fields.Float('Installments', default=0)
    line_ids = fields.Many2many('odoocms.split.invoice.lines', string='Invoice Lines', default=_get_invoice_lines)
    is_split_able = fields.Boolean('Is Split Able', compute='_compute_split_able', store=True)
    warning_message = fields.Html('Warning Message', compute='_compute_warning_message', store=True)

    @api.depends('line_ids', 'line_ids.is_tuition')
    def _compute_split_able(self):
        for rec in self:
            if rec.line_ids:
                if any([ln.is_tuition for ln in rec.line_ids]):
                    rec.is_split_able = True
                else:
                    rec.is_split_able = False

    @api.onchange('install_no')
    def _compute_installment_lines(self):
        for rec in self:
            total1 = 0
            total2 = 0

            max_install_no = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.max_installment_no') or '6')
            if max_install_no and rec.install_no > max_install_no:
                raise UserError(_("You are Exceeding the Installment Limits. Max Limit is %s and you are trying %s") % (max_install_no, rec.install_no))

            install_no = 1 if rec.install_no==0 else rec.install_no
            new_lines = [[5]]

            for line in rec.line_ids:
                line_amt1 = line.invoice_line.price_subtotal
                line_amt2 = 0
                if line.fee_category_id.name=='Tuition Fee' or line.fee_description.strip()=='Previous Arrears' or line.fee_category_id.name=='Hostel Fee' or line.invoice_line.name=='Tax Charged on Fee' or line.amount < 0:
                    # if line.invoice_line.price_subtotal > 0:
                    line_amt1 = math.ceil(line.invoice_line.price_subtotal / install_no)
                    line_amt2 = line_amt1

                lines_data = {
                    'fee_description': line.fee_description,
                    'invoice_line': line.invoice_line.id,
                    'fee_category_id': line.fee_category_id.id,
                    'amount': line.amount,
                    'amount1': line_amt1,
                    'amount2': line_amt2,
                    'split_wiz_id': self.id,
                }
                new_lines.append((0, 0, lines_data))
                total1 += line_amt1
                total2 += line_amt2
            rec.line_ids = new_lines
            rec.total1 = total1
            rec.total2 = total2

    @api.depends('line_ids', 'line_ids.is_tuition')
    def _compute_warning_message(self):
        for rec in self:
            if rec.line_ids:
                if all([not ln.is_tuition for ln in rec.line_ids]):
                    rec.warning_message = """
                       <p class="font-weight-bold" style="text-align:center;background-color: #17134e;color: white;">
                           There is no Tuition Line in the Invoice.
                       </p>
                       """
                else:
                    rec.warning_message = ""

    def split_invoice(self):
        for rec in self:
            discount_amt = 0
            # if not rec.is_split_able:
            #     raise UserError(_('There is not Tuition Line in this Fee Invoice, So it cannot be Split.'))
            if rec.install_no < 2:
                raise UserError(_("Installments should be greater then 1"))

            invoices = rec.invoice_id
            date_invoice = fields.Date.context_today(self)
            fee_structure = rec.invoice_id.fee_structure_id
            sequence = fee_structure.journal_id.sequence_id
            # new_name = sequence.with_context(ir_sequence_date=date_invoice).next_by_id()

            # Installments Greater then 2
            date_due2 = rec.date_due2
            for n in range(1, int(self.install_no)):
                _logger.info('n---- %s' % (n))
                new_name = sequence.with_context(ir_sequence_date=date_invoice).next_by_id()
                new_invoice = rec.invoice_id.copy(
                    default={
                        'state': 'draft',
                        'invoice_date_due': date_due2,
                        'invoice_date': date_invoice,
                        'name': new_name,
                        'invoice_line_ids': False,
                        'line_ids': [],
                        'waiver_amount': 0.0,
                        'waiver_ids': False,
                        'invoice_payment_state': 'not_paid',
                    }
                )
                new_invoice.back_invoice = rec.invoice_id.id
                rec.invoice_id.forward_invoice = new_invoice.id
                rec.invoice_id.state = 'draft'
                invoices += new_invoice
                date_due2 = rec.date_due2 + relativedelta(months=n)

                lines = []
                lines_total = 0
                for line in rec.line_ids:
                    # if line.amount2 > 0:
                    # analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.invoice_line.analytic_tag_ids]
                    fee_line = {
                        'price_unit': line.amount2,
                        'quantity': 1.00,
                        'product_id': line.invoice_line.product_id.id,
                        'name': line.invoice_line.name,
                        'account_id': line.invoice_line.account_id.id,
                        # 'account_analytic_id': line.fee_head_id.account_analytic_id,
                        # 'analytic_tag_ids': analytic_tag_ids,
                        'move_id': new_invoice.id,
                        'fee_head_id': line.invoice_line.fee_head_id.id,
                        'fee_category_id': line.fee_category_id.id,
                        'exclude_from_invoice_tab': False,
                    }
                    lines.append((0, 0, fee_line))
                    if line.amount1 > 0:
                        lines_total += line.amount1
                        if line.invoice_line.credit > 0.0:
                            self.env.cr.execute("update account_move_line set price_unit = %s, credit=%s, balance=%s, price_subtotal=%s, price_total=%s where id=%s \n"
                                , (line.amount1, line.amount1, -line.amount1, line.amount1, line.amount1, line.invoice_line.id))
                        if line.invoice_line.debit > 0.0:
                            self.env.cr.execute("update account_move_line set price_unit = %s, debit=%s, balance=%s, price_subtotal=%s, price_total=%s, amount_residual=%s where id=%s \n"
                                , (-line.amount1, line.amount1, line.amount1, -line.amount1, -line.amount1, line.amount1, line.invoice_line.id))
                    elif line.amount1 < 0:
                        lines_total += line.amount1
                        discount_amt = line.amount1
                    else:
                        # Delete the Zero Value Line (OLD Invoice)
                        self.env.cr.execute("delete from account_move_line where id=%s" % line.invoice_line.id)

                    # else:
                    #     lines_total += round(line.amount1)
                new_invoice.invoice_line_ids = lines

                # Update OLD invoice Total
                invoice_amount = lines_total
                self.env.cr.execute("update account_move set amount_untaxed=%s,amount_total = %s,amount_residual=%s, amount_untaxed_signed=%s, amount_total_signed=%s, amount_residual_signed=%s where id=%s \n"
                    , (invoice_amount, invoice_amount, invoice_amount, invoice_amount, invoice_amount, invoice_amount, rec.invoice_id.id))

                # Update OLD Debit (Receivable Entry)
                debit_entry_id = self.env['account.move.line'].search([('move_id', '=', rec.invoice_id.id), ('account_id', '=', 42)])  # 6=> 121000 Receivable
                if debit_entry_id:
                    debit_entry_id = debit_entry_id[0]
                    self.env.cr.execute("update account_move_line set price_unit = %s, debit=%s, balance=%s, price_subtotal=%s, price_total=%s, amount_residual=%s where id=%s \n"
                        , (-invoice_amount, invoice_amount, invoice_amount, -invoice_amount, -invoice_amount, invoice_amount, debit_entry_id.id))

                # debit Entry when discount
                if abs(discount_amt) > 0:
                    discount_amt = abs(discount_amt)
                    debit_entry_id2 = self.env['account.move.line'].search([('move_id', '=', rec.invoice_id.id), ('account_id', '=', 22), ('price_subtotal', '<', 0)])  # 22=> 450000 Other Income
                    if not debit_entry_id2:
                        debit_entry_id2 = self.env['account.move.line'].search([('move_id', '=', rec.invoice_id.id), ('name', '=', 'Adjustment'), ('price_subtotal', '<', 0)])  # Adjustment

                    if debit_entry_id2:
                        debit_entry_id2 = debit_entry_id2[0]
                        self.env.cr.execute("update account_move_line set price_unit = %s, debit=%s, balance=%s, price_subtotal=%s, price_total=%s, amount_residual=%s where id=%s \n"
                            , (-discount_amt, discount_amt, discount_amt, -discount_amt, -discount_amt, discount_amt, debit_entry_id2.id))

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
                'type': 'ir.actions.act_window'
            }
        else:
            return {'type': 'ir.actions.act_window_close'}


class OdooCMSSplitInvoiceLines(models.TransientModel):
    _name = 'odoocms.split.invoice.lines'
    _description = 'Split Invoice Lines'

    fee_description = fields.Char('Description')
    invoice_line = fields.Many2one('account.move.line', 'Fee Head')
    fee_category_id = fields.Many2one('odoocms.fee.category', 'Fee Category')
    amount = fields.Float('Amount')
    amount1 = fields.Float('1st Invoice')
    amount2 = fields.Float('2nd Invoice')
    split_wiz_id = fields.Many2one('odoocms.split.invoice', 'Split Invoice')
    is_tuition = fields.Boolean('Is Tuition', compute='_compute_ln_val', store=True, default=False)

    @api.depends('fee_category_id')
    def _compute_ln_val(self):
        for rec in self:
            is_tuition = False
            if rec.fee_category_id:
                if rec.fee_category_id.name=='Tuition Fee' or rec.fee_description=='Previous Arrears' or rec.fee_category_id.name=='Hostel Fee' or rec.invoice_line.name=='Tax Charged on Fee' or rec.amount < 0:
                    is_tuition = True
            if not rec.fee_category_id and rec.fee_description and rec.fee_description.strip()=='Previous Arrears' or rec.amount < 0:
                is_tuition = True
            rec.is_tuition = is_tuition
