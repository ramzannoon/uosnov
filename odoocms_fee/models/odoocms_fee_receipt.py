import datetime
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.tools import float_is_zero, float_compare
from odoo.tools.safe_eval import safe_eval
from odoo import tools
import pdb
import logging

_logger = logging.getLogger(__name__)

try:
    from num2words import num2words
except ImportError:
    _logger.warning("The num2words python library is not installed, amount-to-text features won't be fully available.")
    num2words = None


class OdooCMSFeeReceipt(models.Model):
    _inherit = 'account.move'
    _order = "date desc, name desc, id desc"

    # SARFRAZ 10-11-2020 odoocms.application model does not exist yet
    # applicant_id = fields.Many2one('odoocms.application', 'Applicant', readonly=True, states={'draft': [('readonly', False)]})

    student_id = fields.Many2one('odoocms.student', string='Student', readonly=True, states={'draft': [('readonly', False)]})
    student_name = fields.Char(string='Name', related='student_id.partner_id.name', store=True)
    program_id = fields.Many2one('odoocms.program', 'Program', readonly=True, states={'draft': [('readonly', False)]})
    fee_structure_id = fields.Many2one('odoocms.fee.structure', string='Fee Structure', readonly=True, states={'draft': [('readonly', False)]})
    batch_id = fields.Many2one('odoocms.batch', related='student_id.batch_id', store=True)

    session_id = fields.Many2one('odoocms.academic.session', 'Academic Session')
    career_id = fields.Many2one('odoocms.career', 'Academic Level')
    term_id = fields.Many2one('odoocms.academic.term', 'Current Term', )
    semester_id = fields.Many2one('odoocms.semester', 'Semester')

    institute_id = fields.Many2one('odoocms.institute', 'School Name')
    institute_code = fields.Char(related='institute_id.code', string='School Code', store=True)
    discipline_id = fields.Many2one('odoocms.discipline', 'Discipline')
    campus_id = fields.Many2one('odoocms.campus', 'Campus')
    study_scheme_id = fields.Many2one('odoocms.study.scheme', 'Study Scheme')

    is_fee = fields.Boolean('Is Fee', default=False)
    is_cms = fields.Boolean('CMS Receipt?', default=False)
    is_late_fee = fields.Boolean('Is Late Fee', default=False)
    is_scholarship_fee = fields.Boolean('Scholarship Fee', default=False)
    is_hostel_fee = fields.Boolean('Hostel Fee', default=False)
    fee_paid = fields.Boolean('Is Fee Paid', default=False)

    student_ledger_id = fields.Many2one('odoocms.student.ledger', 'Student Ledger')
    registration_id = fields.Many2one('odoocms.student.course', 'Student Course')

    back_invoice = fields.Many2one('account.move', 'Back Invoice')
    forward_invoice = fields.Many2one('account.move', 'Forward Invoice')
    receipt_type_ids = fields.Many2many('odoocms.receipt.type', string='Receipt For')
    waiver_ids = fields.Many2many('odoocms.fee.waiver', string='Fee Waiver')
    waiver_amount = fields.Float('Waiver Amount')
    payment_date = fields.Date('Payment Date')

    # If fee payment is late, system will generate an invoice for fine.
    # Fine invoice will be linked to original invoice
    super_invoice = fields.Many2one('account.move', 'Super Invoice')
    sub_invoice = fields.Many2one('account.move', 'Sub Invoice')

    tag = fields.Char('Tag', help='Attach the tag', readonly=True)
    reference = fields.Char('Receipt Reference')

    description_id = fields.Many2one('odoocms.fee.description', 'Fee Description')
    invoice_group_id = fields.Many2one('account.move.group', 'Invoice Group')

    total_fine = fields.Integer(default=0)
    amount_total_with_fine = fields.Integer(default=0)
    download_time = fields.Datetime()

    invoice_payment_state = fields.Selection(selection=[('not_paid', 'Draft'),
                                                            ('open', 'Verify'),
                                                            ('unpaid', 'Issue To Student'),
                                                            ('in_payment', 'In Payment'),
                                                            ('paid', 'Paid'),
                                                            ('cancel', 'Cancelled')],
                                             default='not_paid', tracking=True, 
                                             string='Payment Status'
                                            )
    barcode = fields.Char('Barcode', compute='compute_barcode', store=True)
    donor_id = fields.Many2one('odoocms.fee.donors', 'Donor', tracking=True)
    validity_date = fields.Date('Validity Date')
    student_tags = fields.Char('Student Tags', compute='_compute_student_tags', store=True)
    # fee_structure_head_id = fields.Many2one('odoocms.fee.structure.head', string='Fee Structure Head')
    # fee_structure_head_line_id = fields.Many2one('odoocms.fee.structure.head.line', string='Fee Structure Head Line')
    to_be = fields.Boolean('To Be', default=False)

    def add_follower(self, partners, subtype_ids=None):
        self.message_subscribe(partner_ids=partners.ids, subtype_ids=subtype_ids)

    def add_followers(self, partners):
        mt_comment = self.env.ref('mail.mt_comment').id

        self.add_follower(partners, [mt_comment, ])
        if self.student_id and self.student_id.user_id:
            self.add_follower(self.student_id.user_id.partner_id, [mt_comment, ])

    @api.model
    def create(self, values):
        invoice = super(OdooCMSFeeReceipt, self.with_context(mail_create_nolog=True, mail_create_nosubscribe=True)).create(values)
        invoice.sudo().add_followers(self.env.user.partner_id)
        return invoice

    def action_invoice_send(self):
        for inv in self:
            inv.invoice_payment_state = 'unpaid'

    def action_invoice_open(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        to_open_invoices = self.filtered(lambda inv: inv.state=='unpaid')
        to_open_invoices.write({'state': 'draft'})
        return super(OdooCMSFeeReceipt, self).action_invoice_open()

    def post(self):
        result = super(OdooCMSFeeReceipt, self).post()
        if self.move_type=='out_invoice' and self.is_fee:
            self.invoice_payment_state = 'open'
        elif self.move_type=='out_refund':
            self.invoice_payment_state = 'open'
        return result

    def _get_refund_common_fields(self):
        return super(OdooCMSFeeReceipt, self)._get_refund_common_fields() + ['student_id', 'applicant_id', 'program_id', 'fee_structure_id', 'is_fee', 'is_cms']

    def _get_report_base_filename(self):
        self.ensure_one()
        return self.move_type=='out_invoice' and self.state=='draft' and _('Draft Invoice') or \
               self.move_type=='out_invoice' and self.state in ('open', 'unpaid', 'in_payment', 'paid') and _('Invoice - %s') % (self.number) or \
               self.move_type=='out_refund' and self.state=='draft' and _('Credit Note') or \
               self.move_type=='out_refund' and _('Credit Note - %s') % self.number or \
               self.move_type=='in_invoice' and self.state=='draft' and _('Vendor Bill') or \
               self.move_type=='in_invoice' and self.state in ('open', 'in_payment', 'paid') and _('Vendor Bill - %s') % (self.number) or \
               self.move_type=='in_refund' and self.state=='draft' and _('Vendor Credit Note') or \
               self.move_type=='in_refund' and _('Vendor Credit Note - %s') % self.number

    def is_zero(self, amount):
        return tools.float_is_zero(amount, precision_rounding=2)

    def amount_to_text(self, amount):
        self.ensure_one()

        def _num2words(number, lang):
            try:
                return num2words(number, lang=lang).title()
            except NotImplementedError:
                return num2words(number, lang='en').title()

        if num2words is None:
            logging.getLogger(__name__).warning("The library 'num2words' is missing, cannot render textual amounts.")
            return ""

        formatted = "%.{0}f".format(2) % amount
        parts = formatted.partition('.')
        integer_value = int(parts[0])
        fractional_value = int(parts[2] or 0)

        lang_code = self.env.context.get('lang') or self.env.user.lang
        lang = self.env['res.lang'].search([('code', '=', lang_code)])
        amount_words = tools.ustr('{amt_value} {amt_word}').format(
            amt_value=_num2words(integer_value, lang=lang.iso_code),
            amt_word='.',
        )
        if not self.is_zero(amount - integer_value):
            amount_words += ' ' + 'and' + tools.ustr(' {amt_value} {amt_word}').format(
                amt_value=_num2words(fractional_value, lang=lang.iso_code),
                amt_word='.',
            )
        return amount_words

    # def action_invoice_paid(self):
    #     # lots of duplicate calls to action_invoice_paid, so we remove those already paid
    #     to_pay_invoices = self.filtered(lambda inv: inv.invoice_payment_state!='paid')
    #     if to_pay_invoices.filtered(lambda inv: inv.invoice_payment_state not in ('open', 'in_payment')):
    #         raise UserError(_('Invoice must be validated in order to set it to register payment.'))
    #     if to_pay_invoices:
    #         pdb.set_trace()
    #     if to_pay_invoices.filtered(lambda inv: not inv.reconciled):
    #         raise UserError(
    #             _('You cannot pay an invoice which is partially paid. You need to reconcile payment entries first.'))
    #
    #     for invoice in to_pay_invoices:
    #         if any([move.journal_id.post_at_bank_rec and move.state=='draft' for move in
    #                 invoice.payment_move_line_ids.mapped('move_id')]):
    #             invoice.write({'state': 'in_payment'})
    #         else:
    #             invoice.write({'state': 'paid'})
    #
    #             if invoice.applicant_id:
    #                 applicant = invoice.applicant_id
    #                 first_semester_number = 1
    #                 first_semester = self.env['odoocms.semester'].browse(first_semester_number)
    #                 first_semester_scheme = self.env['odoocms.semester.scheme'].search([
    #                     ('academic_session_id', '=', applicant.academic_session_id.id),
    #                     ('semester_id', '=', first_semester.id)
    #                 ])
    #                 student = applicant.create_student()
    #                 student.term_id = first_semester_scheme.academic_semester_id.id
    #                 student.semester_id = first_semester.id
    #                 # student.register_courses(first_semester_scheme)

    def unlink(self):
        for move in self:
            slip_barcode = move.barcode
            move.name = '/'
            self._context.get('force_delete')
#            if not move.invoice_payment_state=="not_paid":
 #               raise UserError(_("You cannot delete an entry which has been posted once."))
            have_defer_link = self.env['odoocms.tuition.fee.deferment.line'].search([('defer_invoice_id', '=', move.id), ('state', '!=', 'done')])
            student_waivers = self.env['odoocms.student.fee.waiver'].search([('invoice_id', '=', move.id)])

            if student_waivers:
                student_waivers.unlink()
            if have_defer_link:
                have_defer_link.unlink()
            move.line_ids.unlink()
            move.invoice_line_ids.unlink()
            move.student_ledger_id.unlink()
            move.action_create_receipt_deletion_log()
            if slip_barcode:
                br_ledger_entries = self.env['odoocms.student.ledger'].search([('slip_barcode', '=', slip_barcode)])
                if br_ledger_entries:
                    br_ledger_entries.unlink()
        return super(OdooCMSFeeReceipt, self).unlink()

    def amount_after_first_due_date(self):
        first_due_date = ''
        first_due_date_amount = ''
        for rec in self:
            if rec.invoice_date:
                first_due_date_days = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.first_due_date_days') or '15')
                fine_charge_type = (self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.fine_charge_type') or 'percentage')
                first_due_date_fine = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.first_due_date_fine') or '5')
                if fine_charge_type and fine_charge_type=='percentage':
                    first_due_date_amount = round(rec.amount_total * (first_due_date_fine / 100), 0)
                if fine_charge_type and fine_charge_type=="fixed":
                    first_due_date_amount = first_due_date_fine
                invoice_date_due = rec.invoice_date_due + datetime.timedelta(days=1)
                invoice_date_due_end = rec.invoice_date_due + datetime.timedelta(days=first_due_date_days)
                first_due_date = "Between " + invoice_date_due.strftime("%d-%b-%y") + " to " + invoice_date_due_end.strftime("%d-%b-%y")

                first_due_date_amount = round(rec.amount_total + first_due_date_amount, 2)
        return first_due_date, first_due_date_amount

    def amount_after_second_due_date(self):
        second_due_date = ''
        second_due_date_amount = ''
        for rec in self:
            if rec.invoice_date:
                first_due_date_days = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.first_due_date_days') or '15')
                second_due_date_days = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.second_due_date_days') or '30')
                fine_charge_type = (self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.fine_charge_type') or 'percentage')
                second_due_date_fine = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.second_due_date_fine') or '10')
                if fine_charge_type and fine_charge_type=='percentage':
                    second_due_date_amount = round(rec.amount_total * (second_due_date_fine / 100), 0)
                if fine_charge_type and fine_charge_type=="fixed":
                    second_due_date_amount = second_due_date_fine

                invoice_date1 = rec.invoice_date_due + datetime.timedelta(days=first_due_date_days + 1)
                invoice_date = rec.invoice_date_due + datetime.timedelta(days=second_due_date_days)
                # second_due_date = "From " + invoice_date1.strftime("%d-%b-%y") + " to Onward " + invoice_date.strftime("%d-%b-%y")
                second_due_date = "From " + invoice_date1.strftime("%d-%b-%y") + " to Onward"
                second_due_date_amount = round(rec.amount_total + second_due_date_amount, 0)
        return second_due_date, second_due_date_amount

    @api.depends('name')
    def compute_barcode(self):
        for rec in self:
            if rec.name and not rec.name=='/' and not rec.barcode:
                rec.barcode = self.env['ir.sequence'].next_by_code('odoocms.fee.receipt.barcode.sequence')

    def action_create_receipt_deletion_log(self):
        for rec in self:
            values = {
                'name': rec.name,
                'move_id': rec.id,
                'barcode': rec.barcode,
                'number': rec.name,
                'student_id': rec.student_id.id,
                'session_id': rec.student_id.session_id and rec.student_id.session_id.id or False,
                'career_id': rec.student_id.career_id and rec.student_id.career_id.id or False,
                'institute_id': rec.student_id.institute_id and rec.student_id.institute_id.id or False,
                'campus_id': rec.student_id.campus_id and rec.student_id.campus_id.id or False,
                'program_id': rec.student_id.program_id and rec.student_id.program_id.id or False,
                'discipline_id': rec.student_id.discipline_id and rec.student_id.discipline_id.id or False,
                'term_id': rec.student_id.term_id and rec.student_id.term_id.id or False,
                'semester_id': rec.student_id.semester_id and rec.student_id.semester_id.id or False,
            }
            self.env['odoocms.fee.receipt.deletion.log'].create(values)

    def button_cancel(self):
        for rec in self:
            super(OdooCMSFeeReceipt, rec).button_cancel()
            rec.invoice_payment_state = 'cancel'
            if rec.student_ledger_id:
                debit = rec.student_ledger_id.credit
                if rec.back_invoice or rec.forward_invoice:
                    debit = rec.amount_total
                new_ledger = rec.student_ledger_id.copy(
                    default={
                        # 'debit': rec.student_ledger_id.credit,
                        'debit': debit,
                        'credit': 0,
                        'description': 'Cancellation of Fee Receipt',
                    }
                )

    def group_invoice_lines(self):
        for rec in self:
            res = {}
            lines = []
            results = self.env['account.move.line'].read_group([('move_id', '=', rec.id), ('fee_category_id', '!=', False)], fields=['fee_category_id', 'price_subtotal'], groupby=['fee_category_id'])
            for result in results:
                fee_categ_id = self.env['odoocms.fee.category'].search([('id', '=', result['fee_category_id'][0])])
                if result['price_subtotal'] > 0:
                    lines.append({'category': fee_categ_id.name,
                                  'amount': result['price_subtotal'],
                                  })
        res = lines
        return res

    @api.model
    def create_tax_line100(self, nlimit=100):
        tax_rate = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.tax_rate') or '5')
        taxable_amount = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.taxable_amount') or '200000')
        taxable_fee_heads = self.env['odoocms.fee.head'].search([('taxable', '=', True)])

        receipts = self.env['account.move'].search([('to_be', '=', True)], limit=nlimit)
        for receipt in receipts:
            previous_term_taxable_amt = 0
            current_term_taxable_amt = 0
            net_amount = 0
            tax_amount = 0
            if not any([inv_ln.fee_head_id.id==60 for inv_ln in receipt.invoice_line_ids]):
                fall20_fee_recs = self.env['nust.student.fall20.fee'].search([('student_id', '=', receipt.student_id.id)])
                if fall20_fee_recs:
                    for fall20_fee_rec in fall20_fee_recs:
                        fall20_fee_rec.invoice_id = receipt.id
                        fall20_fee_rec.fee_status = 'c'
                        previous_term_taxable_amt += fall20_fee_rec.amount

                for receipt_line in receipt.invoice_line_ids:
                    # if not 'Discounts' in line[2]:
                    if receipt_line.price_unit < 0:
                        current_term_taxable_amt += receipt_line.price_unit
                    else:
                        if receipt_line.fee_head_id.id in taxable_fee_heads.ids:
                            current_term_taxable_amt += receipt_line.price_unit

                net_amount = previous_term_taxable_amt + current_term_taxable_amt

                if net_amount > taxable_amount:
                    tax_amount = round(net_amount * (tax_rate / 100), 3)

                fee_head = self.env['odoocms.fee.head'].search([('name', '=', 'Advance Tax')])
                if not fee_head:
                    raise UserError(_("Advance Tax Fee Head is not defined in the System."))
                if tax_amount > 0:
                    lines = []
                    tax_line = {
                        'sequence': 900,
                        'price_unit': tax_amount,
                        'quantity': 1,
                        'product_id': fee_head.product_id.id,
                        'name': "Tax Charged on Fee",
                        'account_id': fee_head.property_account_income_id.id,
                        # 'account_analytic_id': line.fee_head_id.account_analytic_id,
                        # 'analytic_tag_ids': analytic_tag_ids,
                        'fee_head_id': fee_head.id,
                        'exclude_from_invoice_tab': False,
                    }
                    lines.append([0, 0, tax_line])
                    receipt.update({'invoice_line_ids': lines})
            receipt.to_be = False

    @api.depends('student_id', 'student_id.tag_ids')
    def _compute_student_tags(self):
        for rec in self:
            if rec.student_id and rec.student_id.tag_ids:
                student_groups = ''
                for tag in rec.student_id.tag_ids:
                    if tag.code:
                        student_groups = student_groups + tag.code + ", "
                rec.student_tags = student_groups

    @api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state')
    def _compute_amount(self):
        invoice_ids = [move.id for move in self if move.id and move.is_invoice(include_receipts=True)]
        self.env['account.payment'].flush(['state'])
        if invoice_ids:
            self._cr.execute(
                '''
                    SELECT move.id
                    FROM account_move move
                    JOIN account_move_line line ON line.move_id = move.id
                    JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
                    JOIN account_move_line rec_line ON
                        (rec_line.id = part.debit_move_id AND line.id = part.credit_move_id)
                    JOIN account_payment payment ON payment.id = rec_line.payment_id
                    JOIN account_journal journal ON journal.id = rec_line.journal_id
                    AND move.id IN %s
                UNION
                    SELECT move.id
                    FROM account_move move
                    JOIN account_move_line line ON line.move_id = move.id
                    JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
                    JOIN account_move_line rec_line ON
                        (rec_line.id = part.credit_move_id AND line.id = part.debit_move_id)
                    JOIN account_payment payment ON payment.id = rec_line.payment_id
                    JOIN account_journal journal ON journal.id = rec_line.journal_id
                    AND move.id IN %s
                ''', [tuple(invoice_ids), tuple(invoice_ids)]
            )
            in_payment_set = set(res[0] for res in self._cr.fetchall())
        else:
            in_payment_set = {}

        for move in self:
            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            currencies = set()

            for line in move.line_ids:
                if line.currency_id:
                    currencies.add(line.currency_id)

                if move.is_invoice(include_receipts=True):
                    # === Invoices ===

                    if not line.exclude_from_invoice_tab:
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.tax_line_id:
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.account_id.user_type_id.type in ('receivable', 'payable'):
                        # Residual amount.
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            if move.move_type=='entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1
            move.amount_untaxed = sign * (total_untaxed_currency if len(currencies)==1 else total_untaxed)
            move.amount_tax = sign * (total_tax_currency if len(currencies)==1 else total_tax)
            move.amount_total = sign * (total_currency if len(currencies)==1 else total)
            move.amount_residual = -sign * (total_residual_currency if len(currencies)==1 else total_residual)
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = abs(total) if move.move_type=='entry' else -total
            move.amount_residual_signed = total_residual

            currency = len(currencies)==1 and currencies.pop() or move.company_id.currency_id
            is_paid = currency and currency.is_zero(move.amount_residual) or not move.amount_residual

            # Compute 'invoice_payment_state'.
            if move.move_type=='entry':
                move.invoice_payment_state = False
            elif move.state=='posted' and is_paid:
                if move.id in in_payment_set:
                    move.invoice_payment_state = 'in_payment'
                else:
                    move.invoice_payment_state = 'paid'
            elif move.is_fee and move.amount_residual > 0 and move.amount_residual!=move.amount_total:
                move.invoice_payment_state = 'in_payment'
            else:
                move.invoice_payment_state = 'not_paid'


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"
    _order = "move_id desc,sequence"

    fee_head_id = fields.Many2one('odoocms.fee.head', 'Fee Head')
    fee_category_id = fields.Many2one('odoocms.fee.category', 'Fee Category', related='fee_head_id.category_id', store=True)
    student_id = fields.Many2one('odoocms.student', 'Student', related='move_id.student_id', store=True)
    # student_tags = fields.Many2many('odoocms.student.tag', 'move_line_student_tags_rel', 'move_line_id', 'tag_id', compute='_compute_student_tags', store=True)
    career_id = fields.Many2one('odoocms.career', 'Academic Level', related='move_id.career_id', store=True)
    program_id = fields.Many2one('odoocms.program', 'Program', related='move_id.program_id', store=True)
    session_id = fields.Many2one('odoocms.academic.session', 'Session', related='move_id.session_id', store=True)
    discipline_id = fields.Many2one('odoocms.discipline', 'Discipline', related='move_id.discipline_id', store=True)
    institute_id = fields.Many2one('odoocms.institute', 'School', related='move_id.institute_id', store=True)
    campus_id = fields.Many2one('odoocms.campus', 'Campus', related='move_id.campus_id', store=True)
    term_id = fields.Many2one('odoocms.academic.term', 'Current Term', related='move_id.term_id', store=True)
    semester_id = fields.Many2one('odoocms.semester', 'Semester', related='move_id.semester_id', store=True)
    batch_id = fields.Many2one('odoocms.batch', related='move_id.batch_id', store=True)
    tag = fields.Char('Tag', related='move_id.tag', store=True)
    # course_id--> This field will store the Course Id for the Extra Semester Course
    course_id = fields.Many2one('odoocms.student.course', 'Course')

    # @api.depends('student_id', 'student_id.tag_ids')
    # def _compute_student_tags(self):
    #     for rec in self:
    #         if rec.student_id and rec.student_id.tag_ids:
    #             rec.student_tags = [[6, 0, rec.move_id.student_id.tag_ids.ids]]


class AccountInvoiceGroup(models.Model):
    _name = "account.move.group"
    _description = 'Invoice Group'
    _rec_name = 'tag'

    invoice_ids = fields.One2many('account.move', 'invoice_group_id', 'Invoice')
    tag = fields.Char('Tag')
    reference = fields.Char('Reference')
    description = fields.Html('Description')
    date = fields.Date('Date')
    state = fields.Selection([('draft', 'Generated'),
                              ('cancel', 'Cancelled')], default='draft')

    def action_cancel_invoice_group(self):
        for rec in self:
            if rec.invoice_ids:
                if any([inv.invoice_payment_state not in ('not_paid', 'unpaid', 'open') for inv in rec.invoice_ids]):
                    for invoice_id in rec.invoice_ids:
                        invoice_id.button_cancel()
                else:
                    raise UserError('Please check that, there are some receipts in payment status.')

                if all([inv.invoice_payment_state=='cancel' for inv in rec.invoice_ids]):
                    rec.state = 'cancel'
            else:
                raise UserError(_('There is no invoice in this Group to Cancel.'))


            # class AccountInvoiceRefund(models.TransientModel):
#     _inherit = "account.invoice.refund"
#
#
#     def compute_refund(self, mode='refund'):
#         inv_obj = self.env['account.move']
#         inv_tax_obj = self.env['account.move.tax']
#         inv_line_obj = self.env['account.move.line']
#         context = dict(self._context or {})
#         xml_id = False
#
#         for form in self:
#             created_inv = []
#             date = False
#             description = False
#             for inv in inv_obj.browse(context.get('active_ids')):
#                 if inv.state in ['draft', 'cancel']:
#                     raise UserError(_('Cannot create credit note for the draft/cancelled invoice.'))
#                 if inv.reconciled and mode in ('cancel', 'modify'):
#                     raise UserError(_(
#                         'Cannot create a credit note for the invoice which is already reconciled, invoice should be unreconciled first, then only you can add credit note for this invoice.'))
#
#                 date = form.date or False
#                 description = form.description or inv.name
#                 refund = inv.refund(form.date_invoice, date, description, inv.journal_id.id)
#
#                 created_inv.append(refund.id)
#                 if mode in ('cancel', 'modify'):
#                     movelines = inv.move_id.line_ids
#                     to_reconcile_ids = {}
#                     to_reconcile_lines = self.env['account.move.line']
#                     for line in movelines:
#                         if line.account_id.id == inv.account_id.id:
#                             to_reconcile_lines += line
#                             to_reconcile_ids.setdefault(line.account_id.id, []).append(line.id)
#                         if line.reconciled:
#                             line.remove_move_reconcile()
#                     refund.action_invoice_open()
#                     for tmpline in refund.move_id.line_ids:
#                         if tmpline.account_id.id == inv.account_id.id:
#                             to_reconcile_lines += tmpline
#                     to_reconcile_lines.filtered(lambda l: l.reconciled == False).reconcile()
#                     if mode == 'modify':
#                         invoice = inv.read(inv_obj._get_refund_modify_read_fields())
#                         invoice = invoice[0]
#                         del invoice['id']
#                         invoice_lines = inv_line_obj.browse(invoice['invoice_line_ids'])
#                         invoice_lines = inv_obj.with_context(mode='modify')._refund_cleanup_lines(invoice_lines)
#                         tax_lines = inv_tax_obj.browse(invoice['tax_line_ids'])
#                         tax_lines = inv_obj._refund_cleanup_lines(tax_lines)
#                         invoice.update({
#                             'type': inv.type,
#                             'date_invoice': form.date_invoice,
#                             'state': 'draft',
#                             'number': False,
#                             'invoice_line_ids': invoice_lines,
#                             'tax_line_ids': tax_lines,
#                             'date': date,
#                             'origin': inv.origin,
#                             'fiscal_position_id': inv.fiscal_position_id.id,
#                         })
#                         for field in inv_obj._get_refund_common_fields():
#                             if inv_obj._fields[field].type == 'many2one':
#                                 invoice[field] = invoice[field] and invoice[field][0]
#                             else:
#                                 invoice[field] = invoice[field] or False
#                         inv_refund = inv_obj.create(invoice)
#                         body = _(
#                             'Correction of <a href=# data-oe-model=account.move data-oe-id=%d>%s</a><br>Reason: %s') % (
#                                inv.id, inv.number, description)
#                         inv_refund.message_post(body=body)
#                         if inv_refund.payment_term_id.id:
#                             inv_refund._onchange_payment_term_date_invoice()
#                         created_inv.append(inv_refund.id)
#                 xml_id = inv.type == 'out_invoice' and inv.is_cms and 'odoocms_fee.action_odoocms_receipt_refund' or \
#                          inv.type == 'out_invoice' and 'account.action_invoice_out_refund' or \
#                          inv.type == 'out_refund' and inv.is_cms and 'odoocms_fee.action_odoocms_receipt' or \
#                          inv.type == 'out_refund' and 'account.action_invoice_tree1' or \
#                          inv.type == 'in_invoice' and 'account.action_invoice_in_refund' or \
#                          inv.type == 'in_refund' and 'account.action_invoice_tree2'
#
#         if xml_id:
#             #result = self.env.ref('account.%s' % (xml_id)).read()[0]
#             result = self.env.ref('%s' % (xml_id)).read()[0]
#             if mode == 'modify':
#                 # When refund method is `modify` then it will directly open the new draft bill/invoice in form view
#                 if inv_refund.type == 'in_invoice':
#                     view_ref = self.env.ref('account.move_supplier_form')
#                 else:
#                     if inv_refund.is_cms:
#                         view_ref = self.env.ref('odoocms_fee.odoocms_receipt_form')
#                     else:
#                         view_ref = self.env.ref('account.move_form')
#                 result['views'] = [(view_ref.id, 'form')]
#                 result['res_id'] = inv_refund.id
#             else:
#                 invoice_domain = safe_eval(result['domain'])
#                 invoice_domain.append(('id', 'in', created_inv))
#                 result['domain'] = invoice_domain
#             return result
#         return True