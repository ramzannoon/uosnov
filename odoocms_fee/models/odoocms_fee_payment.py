from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import pdb
from datetime import date


class OdooCMSFeePaymentRegister(models.Model):
    _name = 'odoocms.fee.payment.register'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Fee Payment Register, Combine multiple fee payment receipts'

    name = fields.Char('Name', tracking=True)
    sequence = fields.Char('Sequence')
    date = fields.Date('Date', default=fields.Date.today(), tracking=True)
    fee_payment_ids = fields.One2many('odoocms.fee.payment', 'payment_register_id', 'Fee Payments')
    non_barcode_ids = fields.One2many('odoocms.fee.non.barcode.receipts', 'payment_register_id', 'Non Barcode Ref')
    fee_processed_ids = fields.One2many('odoocms.fee.processed.receipts', 'payment_register_id', 'Processed Receipts')
    state = fields.Selection([('Draft', 'Draft'),
                              ('Posted', 'Posted'),
                              ('Cancel', 'Cancel')], string='Status', default='Draft')
    total_receipts = fields.Float('Total Receipts', compute='compute_total_receipt', store=True, tracking=True)
    non_barcode_receipts = fields.Float('Non Barcode Receipts', compute='compute_total_receipt', store=True, tracking=True)
    total_amount = fields.Float('Total Invoice Amount', compute='compute_total_amount', store=True, tracking=True)
    total_received_amount = fields.Float('Total Received Amount', compute='compute_total_amount', store=True, tracking=True)
    total_diff_amount = fields.Float('Total Diff Amount', compute='compute_total_amount', store=True, tracking=True)
    barcode = fields.Char('Barcode')

    @api.model
    def create(self, values):
        result = super(OdooCMSFeePaymentRegister, self).create(values)
        if not result.name:
            result.name = self.env['ir.sequence'].next_by_code('odoocms.fee.payment.register')
        return result

    def unlink(self):
        for rec in self:
            return super(OdooCMSFeePaymentRegister, self).unlink()

    @api.depends('fee_payment_ids', 'non_barcode_ids')
    def compute_total_receipt(self):
        for rec in self:
            rec.total_receipts = rec.fee_payment_ids and len(rec.fee_payment_ids.ids) or 0.0
            rec.non_barcode_receipts = rec.non_barcode_ids and len(rec.non_barcode_ids.ids) or 0.0

    def action_cancel(self):
        self.state = 'Cancel'

    @api.depends('fee_payment_ids', 'fee_payment_ids.amount')
    def compute_total_amount(self):
        for rec in self:
            total = 0
            received_amt = 0
            diff_amt = 0
            for payment in rec.fee_payment_ids:
                total = total + payment.amount
                received_amt = received_amt + payment.received_amount
                diff_amt = diff_amt + payment.diff_amount
            rec.total_amount = total
            rec.total_received_amount = received_amt
            rec.total_diff_amount = diff_amt

    @api.onchange('barcode')
    def onchange_barcode(self):
        if self.barcode:
            if self.state=='Draft':
                already_exist = False
                invoice_id = self.env['account.move'].search([('barcode', '=', self.barcode), ('move_type', '=', 'out_invoice'), ('amount_residual', '>', 0)])
                if not invoice_id:
                    invoice_id = self.env['account.move'].search([('name', '=', self.barcode), ('move_type', '=', 'out_invoice'), ('amount_residual', '>', 0)])

                already_exist = self.env['odoocms.fee.payment'].search([('receipt_number', '=', self.barcode),
                                                                        ('invoice_id.amount_residual', '=', 0.0)])
                if not already_exist:
                    already_exist = self.env['account.move'].search([('barcode', '=', self.barcode),
                                                                     ('move_type', '=', 'out_invoice'),
                                                                     ('amount_residual', '=', 0.0)])
                if not already_exist:
                    fee_payment_rec_exist = self.env['odoocms.fee.payment'].search([('receipt_number', '=', self.barcode)], order='id', limit=1)
                    if fee_payment_rec_exist:
                        if fee_payment_rec_exist.received_amount >= fee_payment_rec_exist.amount:
                            already_exist = fee_payment_rec_exist

                if not already_exist:
                    already_exist = self.env['odoocms.fee.payment'].search([('invoice_id', '=', invoice_id.id),
                                                                            ('payment_register_id', '=', self.id),
                                                                            ('invoice_id.amount_residual', '>', 0.0),
                                                                            ], order='id', limit=1)

                # Create the Record in the Fee Payment Receipts
                if invoice_id and not already_exist:
                    values = {
                        'invoice_id': invoice_id.id,
                        'receipt_number': self.barcode,
                        'student_id': invoice_id.student_id and invoice_id.student_id.id or False,
                        'invoice_status': invoice_id.invoice_payment_state and invoice_id.invoice_payment_state or '',
                        'amount': invoice_id.amount_residual,
                        'id_number': invoice_id.student_id.id_number and invoice_id.student_id.id_number or '',
                        'session_id': invoice_id.session_id and invoice_id.session_id.id or False,
                        'career_id': invoice_id.career_id and invoice_id.career_id.id or False,
                        'institute_id': invoice_id.institute_id and invoice_id.institute_id.id or False,
                        'discipline_id': invoice_id.discipline_id and invoice_id.discipline_id.id or False,
                        'campus_id': invoice_id.campus_id and invoice_id.campus_id.id or False,
                        'term_id': invoice_id.term_id and invoice_id.term_id.id or False,
                        'semester_id': invoice_id.semester_id and invoice_id.semester_id.id or False,
                        'journal_id': 16,
                        'date': self.date,
                        'payment_register_id': self.id,
                        'received_amount': invoice_id.amount_residual,
                    }
                    self.env['odoocms.fee.payment'].create(values)

                # Already Exist But Payment Register is not Set
                if already_exist and already_exist._table=='odoocms_fee_payment' and not already_exist.payment_register_id:
                    for already_exist_id in already_exist:
                        already_exist_id.payment_register_id = self._origin.id

                # Already Exit And Payment Register is also Set
                if already_exist and already_exist._table=='odoocms_fee_payment' and already_exist.payment_register_id:
                    for already_exist_id in already_exist:
                        # Create Records in the Processed Receipts
                        notes = "Already Processed in " + (already_exist_id.payment_register_id.name and already_exist_id.payment_register_id.name or '') + " on " + already_exist_id.date.strftime("%d/%m/%Y")
                        processed_values = {
                            'barcode': self.barcode,
                            'name': self.barcode,
                            'payment_register_id': self.id,
                            'notes': notes,
                        }
                        self.env['odoocms.fee.processed.receipts'].create(processed_values)

                # If invoice_id is not found then create in the Non Barcode Receipts
                if not invoice_id and not already_exist:
                    non_barcode_exit = self.env['odoocms.fee.non.barcode.receipts'].search([('barcode', '=', self.barcode)])
                    if not non_barcode_exit:
                        non_barcode_vals = {
                            'barcode': self.barcode,
                            'name': self.barcode,
                            'payment_register_id': self.id,
                        }
                        self.env['odoocms.fee.non.barcode.receipts'].create(non_barcode_vals)
            self.barcode = None

    def action_post(self):
        for rec in self:
            # if any([p_rec.invoice_id.invoice_payment_state != 'open' for p_rec in rec.fee_payment_ids]):
            # raise UserError("Some Invoices in the Entered Records are not in the Open State,
            # Please Recheck and again Process.")
            print('HI')
            for payment in rec.fee_payment_ids:
                invoice = self.env['account.move'].search([('barcode', '=', payment.receipt_number), ('invoice_payment_state', '!=', 'not_paid'), ('move_type', '=', 'out_invoice'), ('amount_residual', '>', 0.0)])
                print(invoice)
                if invoice and not payment.processed:
                    # Check the Fines
                    fine_amt = 0
                    if payment.diff_amount < 0 and payment.date > invoice.invoice_date_due:
                        fine_amt = payment.action_update_invoice(invoice)
                        self.env['account.move'].flush()
                        receivable_line = invoice.line_ids.filtered(lambda l: l.account_id.name=='Account Receivable')
                        if receivable_line:
                            receivable_line.amount_residual = receivable_line.amount_residual + fine_amt
                            receivable_line._amount_residual()

                    invoice_ids = [(4, invoice.id, None)]
                    invoice_ids2 = invoice
                    due_date = invoice.invoice_date_due
                    date_invoice = payment.date
                    payment_date = fields.Date.from_string(payment.date)
                    invoice.payment_date = rec.date
                    days = (payment_date - due_date).days

                    # analytic_tags = self.env['account.analytic.tag']
                    # analytic_tags += invoice.student_id.campus_id.analytic_tag_id
                    # # analytic_tags += invoice.student_id.grade_level_id.analytic_tag_id  # cost center
                    # # analytic_tags += invoice.student_id.campus_id.city_id.analytic_tag_id  # cost city
                    # analytic_tag_ids = [(6, 0, analytic_tags.ids)]
                    # # analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in analytic_tags]

                    partner_id = invoice.student_id and invoice.student_id.partner_id or False
                    if invoice.is_scholarship_fee:
                        partner_id = invoice.donor_id and invoice.donor_id.partner_id or False

                    data = {
                        'payment_type': 'inbound',
                        'payment_method_id': '1',
                        'partner_type': 'customer',
                        'currency_id': invoice.journal_id.company_id.currency_id.id,
                        'partner_id': partner_id and partner_id.id or False,
                        'payment_date': payment.date,
                        'communication': payment.receipt_number,
                        'amount': payment.received_amount,
                        # 'amount': payment.received_amount if payment.received_amount <= payment.amount else payment.amount,# 17-06-2021
                        'journal_id': payment.journal_id.id,
                        'invoice_ids': invoice_ids,
                        # 'account_analytic_id': invoice.student_id.campus_id.account_analytic_id.id,
                        # 'account_analytic_id': False,
                        # 'analytic_tag_ids': [],
                        'donor_id': invoice.donor_id and invoice.donor_id.id or False,
                    }
                    # for invoice_rec in invoice_ids2:
                    #     if invoice_rec.invoice_payment_state=='unpaid':
                    #         invoice_rec.action_post()
                            # 23-05-2021
                            # invoice_rec.invoice_payment_state = 'in_payment'

                    pay_rec = self.env['account.payment'].create(data)
                    pay_rec.post()
                    if pay_rec.move_line_ids:
                        pay_rec_moves = pay_rec.move_line_ids.mapped('move_id')
                        pay_rec_moves.write({'institute_id': invoice.institute_id.id})
                    payment.name = pay_rec.name
                    invoice.payment_id = pay_rec.id
                    invoice_ids2.payment_date = payment.date

                    if not invoice.is_scholarship_fee:
                        ledger_data = {
                            'student_id': invoice.student_id.id,
                            'date': date_invoice,
                            'debit': payment.received_amount,
                            'invoice_id': invoice.id,
                            'payment_id': payment.id,
                            'id_number': invoice.student_id.id_number,
                            'session_id': invoice.student_id.session_id and invoice.student_id.session_id.id or False,
                            'career_id': invoice.student_id.career_id and invoice.student_id.career_id.id or False,
                            'program_id': invoice.student_id.program_id and invoice.student_id.program_id.id or False,
                            'institute_id': invoice.student_id.institute_id and invoice.student_id.institute_id.id or False,
                            'discipline_id': invoice.student_id.discipline_id and invoice.student_id.discipline_id.id or False,
                            'campus_id': invoice.student_id.campus_id and invoice.student_id.campus_id.id or False,
                            'term_id': invoice.student_id.term_id and invoice.student_id.term_id.id or False,
                            'semester_id': invoice.student_id.campus_id and invoice.student_id.semester_id.id or False,
                            'description': 'Payment of Fee Receipt',
                        }
                        ledger_id = self.env['odoocms.student.ledger'].create(ledger_data)
                        payment.student_ledger_id = ledger_id.id
                        payment.state = 'done'
                        payment.processed = True

                    # # Sending Email for the Fee Receipt Ack
                    # if invoice.is_student_invoice and invoice.student_id.father_official_email or invoice.student_id.father_personal_email:
                    #     template = self.env.ref('odooschool_fee.email_template_fee_receipt_ack')
                    #     invoice.message_post_with_template(template.id, composition_mode='comment')

                # Not Invoice
                if not invoice:
                    invoice = self.env['account.move'].search([('barcode', '=', payment.receipt_number),
                                                               ('invoice_payment_state', '!=', 'not_paid'),
                                                               ('move_type', '=', 'out_invoice'),
                                                               ('amount_residual', '=', 0.0)])
                    if invoice:
                        invoice.invoice_payment_state = 'paid'
                        payment.state = 'done'

            # if Non Barcode
            if rec.non_barcode_ids:
                rec.non_barcode_ids.write({'state': 'Posted'})

            # if Already Processed Receipts
            if rec.fee_processed_ids:
                rec.fee_processed_ids.write({'state': 'Posted'})

            if all([line.state=='done' for line in rec.fee_payment_ids]):
                rec.state = 'Posted'

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Fee Import From Fee Register'),
            'template': '/odoocms_fee/static/xls/fee_payment_register.xlsx'
        }]


class OdooCMSFeePayment(models.Model):
    _name = 'odoocms.fee.payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Fee Payment'

    name = fields.Char()
    sequence = fields.Integer('Sequence')
    date = fields.Date('Date', required=True, readonly=True, states={'draft': [('readonly', False)]}, default=fields.Date.today())
    description = fields.Char('Description', readonly=True, states={'draft': [('readonly', False)]})
    amount = fields.Float('Amount', required=True, readonly=True, states={'draft': [('readonly', False)]}, default=0)
    doc_no = fields.Text('DOC No', readonly=True, states={'draft': [('readonly', False)]})
    id_number = fields.Char('Student ID', readonly=True, states={'draft': [('readonly', False)]})
    receipt_number = fields.Char('Receipt No', required=True, readonly=True, states={'draft': [('readonly', False)]})
    journal_id = fields.Many2one('account.journal', 'Journal', required=False, readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'),
                              ('done', 'Done'),
                              ('error', 'Error')], 'Status', default='draft', readonly=True, states={'draft': [('readonly', False)]})

    transaction_date = fields.Date('Transaction Date', default=fields.Date.today(), required=True)
    student_ledger_id = fields.Many2one('odoocms.student.ledger', String='Student Ledger')
    student_id = fields.Many2one('odoocms.student', 'Student', compute='compute_invoice_data', store=True)

    tag = fields.Char('Batch-ID/Tag', help='Attach the tag', readonly=True)
    payment_register_id = fields.Many2one('odoocms.fee.payment.register', 'Payment Register', tracking=True, index=True, auto_join=True, ondelete='cascade')
    invoice_id = fields.Many2one('account.move', 'Invoice', compute='compute_invoice_data', store=True)
    invoice_status = fields.Selection(related='invoice_id.invoice_payment_state', string='Invoice Status', store=True)
    diff_amount = fields.Float('Diff Amount', compute='compute_diff_amt', store=True)
    received_amount = fields.Float('Received Amount')
    invoice_payment_state = fields.Selection(related="invoice_id.invoice_payment_state", string="Invoice Payment Status", store=True)
    processed = fields.Boolean('Processed', default=False)

    career_id = fields.Many2one('odoocms.career', 'Academic Level', compute='compute_invoice_data', store=True)
    program_id = fields.Many2one('odoocms.program', 'Academic Program', tracking=True, compute='compute_invoice_data', store=True)
    institute_id = fields.Many2one('odoocms.institute', 'School', compute='compute_invoice_data', store=True)
    discipline_id = fields.Many2one('odoocms.discipline', 'Discipline', compute='compute_invoice_data', store=True)
    campus_id = fields.Many2one('odoocms.campus', 'Campus', compute='compute_invoice_data', store=True)
    term_id = fields.Many2one('odoocms.academic.term', 'Current Academic Term', tracking=True, compute='compute_invoice_data', store=True)
    session_id = fields.Many2one('odoocms.academic.session', 'Academic Session', tracking=True, compute='compute_invoice_data', store=True)
    semester_id = fields.Many2one('odoocms.semester', 'Semester', tracking=True, compute='compute_invoice_data', store=True)
    to_be = fields.Boolean('To Be', default=False)

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Student Fee Payments'),
            'template': '/odoocms_fee/static/xls/fee_collection.xlsx'
        }]

    def unlink(self):
        for rec in self:
            if not rec.state=='draft':
                raise UserError('You Cannot delete this Record, This Record is not in the Draft State.')
            return super(OdooCMSFeePayment, self).unlink()

    @api.depends('receipt_number')
    def compute_invoice_data(self):
        for rec in self:
            invoice_id = self.env['account.move'].search([('barcode', '=', rec.receipt_number), ('move_type', '=', 'out_invoice'), ('amount_residual', '>', 0)])
            if not invoice_id:
                invoice_id = self.env['account.move'].search([('name', '=', rec.receipt_number), ('move_type', '=', 'out_invoice'), ('amount_residual', '>', 0)])
            if invoice_id:
                rec.invoice_id = invoice_id.id
                rec.invoice_status = invoice_id.invoice_payment_state
                rec.student_id = invoice_id.student_id and invoice_id.student_id.id or False
                rec.amount = invoice_id.amount_residual
                rec.session_id = invoice_id.session_id and invoice_id.session_id.id or False
                rec.career_id = invoice_id.career_id and invoice_id.career_id.id or False
                rec.program_id = invoice_id.program_id and invoice_id.program_id.id or False
                rec.institute_id = invoice_id.institute_id and invoice_id.institute_id.id or False
                rec.discipline_id = invoice_id.discipline_id and invoice_id.discipline_id.id or False
                rec.campus_id = invoice_id.campus_id and invoice_id.campus_id.id or False
                rec.term_id = invoice_id.term_id and invoice_id.term_id.id or False
                rec.semester_id = invoice_id.semester_id and invoice_id.semester_id.id or False

    @api.depends('amount', 'received_amount')
    def compute_diff_amt(self):
        for rec in self:
            rec.diff_amount = rec.amount - rec.received_amount

    def action_invoice_issue_validate(self):
        for rec in self:
            rec.invoice_id.action_invoice_send()
            rec.invoice_id.action_post()

    def action_update_invoice(self, invoice=False):
        for rec in self:
            amount = 0
            if invoice:
                first_due_date_days = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.first_due_date_days') or '15')
                second_due_date_days = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.second_due_date_days') or '30')
                first_due_date_fine = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.first_due_date_fine') or '5')
                second_due_date_fine = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.second_due_date_fine') or '10')

                days = (rec.date - invoice.invoice_date_due).days
                if days <= first_due_date_days:
                    amount = round(invoice.amount_residual * (first_due_date_fine / 100))
                if days > first_due_date_days:
                    amount = round(invoice.amount_residual * (second_due_date_fine / 100))
            fine_line = invoice.invoice_line_ids.filtered(lambda l: l.fee_head_id.name=='Fine')
            receivable_line = invoice.line_ids.filtered(lambda l: l.account_id.name=='Account Receivable')

            if fine_line:
                # Will Credit
                self.env.cr.execute("update account_move_line set price_unit = %s, credit=%s, balance=%s, price_subtotal=%s, price_total=%s where id=%s \n"
                    , (amount, amount, -amount, amount, amount, fine_line.id))

                # Receivable Line, it will debit

                debit_amt = receivable_line.debit + amount
                self.env.cr.execute("update account_move_line set price_unit = %s, debit=%s, balance=%s, price_subtotal=%s, price_total=%s where id=%s \n"
                    , (-debit_amt, debit_amt, debit_amt, -debit_amt, -debit_amt, receivable_line.id,))

                # Invoice Total Update
                self.env.cr.execute("update account_move set amount_untaxed=%s,amount_total = %s,amount_residual=%s, amount_untaxed_signed=%s, amount_total_signed=%s, amount_residual_signed=%s where id=%s \n"
                    , (debit_amt, debit_amt, debit_amt, debit_amt, debit_amt, debit_amt, invoice.id))
                ledger_id = self.env['odoocms.student.ledger'].search([('invoice_id', '=', invoice.id)], order='id desc', limit=1)
                ledger_id.credit = ledger_id.credit + amount
                rec.amount += amount
        return amount

    def action_read_fee_payments(self):
        self.ensure_one()
        return {
            'name': "Fee Payments Form",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'odoocms.fee.payment',
            'res_id': self.id,
        }


# This Class Will Handle all the barcode Records whose Invoice is
# Not found. (Invoice Barcode does not Match With Barcode)
class OdooCMSFeeNonBarcodeReceipts(models.Model):
    _name = 'odoocms.fee.non.barcode.receipts'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Non Barcode Receipts'

    name = fields.Char('Name')
    barcode = fields.Char('Barcode')
    payment_register_id = fields.Many2one('odoocms.fee.payment.register', 'Payment Register')
    state = fields.Selection([('Draft', 'Draft'),
                              ('Posted', 'Posted'),
                              ('Cancel', 'Cancel')], string='Status', default='Draft')


# This Class Will Handle all the Records that is already processed But User Scan the barcode again.
class OdooCMSFeeProcessedReceipts(models.Model):
    _name = 'odoocms.fee.processed.receipts'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Fee Processed Receipts'

    name = fields.Char('Name')
    barcode = fields.Char('Barcode')
    payment_register_id = fields.Many2one('odoocms.fee.payment.register', 'Payment Register')
    state = fields.Selection([('Draft', 'Draft'),
                              ('Posted', 'Posted'),
                              ('Cancel', 'Cancel')], string='Status', default='Draft')
    notes = fields.Char('Notes')


class OdooCMSPaymentTerms(models.Model):
    _name = 'odoocms.payment.terms'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Fee Payment Terms'

    name = fields.Char('Name', tracking=True)
    code = fields.Char('Code')
    sequence = fields.Integer('Sequence')
    description = fields.Text('Description', tracking=True)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    donor_id = fields.Many2one('odoocms.fee.donors', 'Donor', tracking=True)
