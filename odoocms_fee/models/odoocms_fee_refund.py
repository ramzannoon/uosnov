from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import pdb


class OdooCMSFeeRefundReason(models.Model):
    _name = 'odoocms.fee.refund.reason'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Fee Refund Reason"

    name = fields.Char('Refund Reason', required=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('lock', 'Locked')
                              ], string='Status', default='draft', tracking=True)

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'


class OdooCMSFeeRefundTypes(models.Model):
    _name = 'odoocms.fee.refund.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Fee Refund Types'

    name = fields.Char('Name', tracking=True)
    code = fields.Char('Code', tracking=True)
    sequence = fields.Integer('Sequence')
    receipt_type = fields.Many2one('odoocms.receipt.type', string='Receipt Type', tracking=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('lock', 'Locked')
                              ], string='Status', default='draft', tracking=True)

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'


class OdooCMSFeeRefundHeads(models.Model):
    _name = 'odoocms.fee.refund.heads'
    _description = 'Fee Refund Security Heads'

    fee_head_id = fields.Many2one('odoocms.fee.head', string='Fee Heads', readonly=True)
    amount = fields.Monetary(string='Amount', readonly=True, default=0.0)
    refund_id = fields.Many2one('odoocms.fee.refund.request', string='Refund')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)


class OdooCMSFeeRefundRequest(models.Model):
    _name = 'odoocms.fee.refund.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Student Fee Refund Request'

    READONLY_STATES = {'submitted': [('readonly', True)],
                       'approve': [('readonly', True)],
                       'done': [('readonly', True)],
                       'cancel': [('readonly', True)],
                       }

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence')
    student_id = fields.Many2one('odoocms.student', 'Student', states=READONLY_STATES)
    session_id = fields.Many2one('odoocms.academic.session', 'Academic Session', states=READONLY_STATES)
    career_id = fields.Many2one('odoocms.career', 'Academic Level', states=READONLY_STATES)
    program_id = fields.Many2one('odoocms.program', 'Program', states=READONLY_STATES)
    batch_id = fields.Many2one('odoocms.batch', states=READONLY_STATES)
    institute_id = fields.Many2one('odoocms.institute', 'School', states=READONLY_STATES)
    discipline_id = fields.Many2one('odoocms.discipline', 'Discipline', states=READONLY_STATES)
    campus_id = fields.Many2one('odoocms.campus', 'Campus', states=READONLY_STATES)
    semester_id = fields.Many2one('odoocms.semester', 'Semester', states=READONLY_STATES)
    term_id = fields.Many2one('odoocms.academic.term', 'Term', states=READONLY_STATES)

    date = fields.Date('Request Date', default=fields.Date.today, states=READONLY_STATES, required=True)
    refund_by = fields.Selection([('cash', 'Cash'),
                                  ('bank', 'Bank'),
                                  ('cheque', 'Cheque')], default='cash', string='Refund Mode', tracking=True)
    reason_id = fields.Many2one('odoocms.fee.refund.reason', 'Refund Reason', requied=True)
    refund_line_ids = fields.One2many('odoocms.fee.refund.request.line', 'refund_id', string='Refund Lines')
    description = fields.Text('Detailed Description', states=READONLY_STATES, required=True)

    state = fields.Selection([('draft', 'Submitted'),
                              ('approve', 'Approved'),
                              ('reject', 'Rejected'),
                              ('done', 'Done'),
                              ('cancel', 'Canceled')], default='draft', string="Status", tracking=True)

    refund_type = fields.Selection([('admission', 'Admission Tuition'),
                                    ('semester_fee', 'Semester Tuition Fee'),
                                    ('wavier', 'Waiver'),
                                    ('late_fine', 'Late Fine'),
                                    ('security', 'Security'),
                                    ('scholarship', 'Scholarship'),
                                    ('course_drop', 'Course Drop'),
                                    ], string='Refund Type', required=True, states=READONLY_STATES)

    total_amount = fields.Float('Total Amount', compute='_compute_total_amount', store=True)
    total_refund_amount = fields.Float('Total Refund Amount', compute='_compute_total_refund', store=True)
    student_ledger_id = fields.Many2one('odoocms.student.ledger', 'Ledger Ref', tracking=True)
    payment_journal_id = fields.Many2one('account.journal', 'Payment Journal', tracking=True)
    payment_id = fields.Many2one('account.payment', 'Payment', tracking=True)

    @api.onchange('student_id')
    def onchange_student_id(self):
        for rec in self:
            if rec.student_id:
                rec.session_id = rec.student_id.session_id and rec.student_id.session_id.id or False
                rec.career_id = rec.student_id.career_id and rec.student_id.career_id.id or False
                rec.program_id = rec.student_id.program_id and rec.student_id.program_id.id or False
                rec.batch_id = rec.student_id.batch_id and rec.student_id.batch_id.id or False
                rec.term_id = rec.student_id.term_id and rec.student_id.term_id.id or False
                rec.semester_id = rec.student_id.semester_id and rec.student_id.semester_id.id or False
                rec.discipline_id = rec.student_id.discipline_id and rec.student_id.discipline_id.id or False
                rec.institute_id = rec.student_id.institute_id and rec.student_id.institute_id.id or False
                rec.campus_id = rec.student_id.campus_id and rec.student_id.campus_id.id or False

    @api.model
    def create(self, values):
        if not values.get('name', False):
            values['name'] = self.env['ir.sequence'].next_by_code('odoocms.fee.refund.request')
        result = super(OdooCMSFeeRefundRequest, self).create(values)
        result.action_create_lines()
        return result

    def action_create_lines(self):
        for rec in self:
            if rec.refund_type in ('semester_fee', 'admission'):
                invoice_ids = self.env['account.move'].search([('student_id', '=', rec.student_id.id),
                                                               ('term_id', '=', rec.student_id.term_id.id),
                                                               ('is_scholarship_fee', '!=', True),
                                                               ('invoice_payment_state', 'in', ('in_payment', 'paid'))])
                if invoice_ids:
                    for invoice_id in invoice_ids:
                        lines = invoice_id.invoice_line_ids.filtered(lambda l: l.fee_head_id.refund)
                        if lines:
                            for line in lines:
                                line_data = {
                                    'refund_type': rec.refund_type,
                                    'description': line.name,
                                    'refund_id': rec.id,
                                    'actual_amount': line.price_subtotal,
                                    'refund_amount': 0,
                                }
                                self.env['odoocms.fee.refund.request.line'].create(line_data)
            # CASE-2
            if rec.refund_type=='late_fine':
                invoice_ids = self.env['account.move'].search([('student_id', '=', rec.student_id.id),
                                                               ('term_id', '=', rec.student_id.term_id.id),
                                                               ('is_scholarship_fee', '!=', True),
                                                               ('invoice_payment_state', 'in', ('in_payment', 'paid'))])
                if invoice_ids:
                    for invoice_id in invoice_ids:
                        lines = invoice_id.invoice_line_ids.filtered(lambda l: l.fee_head_id.name in ('Fine', 'Fines') and l.price_subtotal > 0)
                        if lines:
                            for line in lines:
                                line_data = {
                                    'refund_type': rec.refund_type,
                                    'description': line.name,
                                    'refund_id': rec.id,
                                    'actual_amount': line.price_subtotal,
                                    'refund_amount': 0,
                                }
                                self.env['odoocms.fee.refund.request.line'].create(line_data)

    @api.depends('refund_line_ids', 'refund_line_ids.actual_amount')
    def _compute_total_amount(self):
        for rec in self:
            total_amount = 0
            if rec.refund_line_ids:
                for line in rec.refund_line_ids:
                    total_amount += line.actual_amount
            rec.total_amount = total_amount

    @api.depends('refund_line_ids', 'refund_line_ids.refund_amount')
    def _compute_total_refund(self):
        for rec in self:
            total_refund = 0
            if rec.refund_line_ids:
                for line in rec.refund_line_ids:
                    total_refund += line.refund_amount
            rec.total_refund_amount = total_refund

    def action_approve_refund(self):
        for rec in self:
            if not rec.refund_line_ids:
                raise UserError(_('No Refund Detail.'))

            refundable_fee_heads = self.env['odoocms.fee.head'].search([('refund', '=', True)])
            apply_refund = False
            if rec.term_id and rec.batch_id and rec.batch_id.can_apply('full_refund', rec.date):
                apply_refund = 'full'
            if not apply_refund and rec.term_id and rec.batch_id and rec.batch_id.can_apply('half_refund', rec.date):
                apply_refund = 'half'

            if apply_refund:
                if apply_refund=='full' and rec.refund_line_ids:
                    for line in rec.refund_line_ids:
                        line.refund_amount = line.actual_amount
                if apply_refund=='half':
                    for line in rec.refund_line_ids:
                        line.refund_amount = round(line.actual_amount / 2, 3)
            else:
                for line in rec.refund_line_ids:
                    line.refund_amount = 0

            if rec.total_refund_amount > 0:
                ledger_data = {
                    'student_id': rec.student_id.id,
                    'debit': rec.total_refund_amount,
                    'credit': 0,
                    'date': fields.Date.today(),
                    'description': "Student Refund",
                    'refund_request_id': rec.id,
                }
                ledger_id = self.env['odoocms.student.ledger'].create(ledger_data)
                rec.student_ledger_id = ledger_id and ledger_id.id or False
            rec.state = 'approve'
            rec.refund_line_ids.write({'state': 'approve'})

    def action_refund_paid(self):
        for rec in self:
            if not rec.payment_journal_id:
                raise UserError(_('Please Select the Payment Journal/Bank.'))
            if not rec.total_refund_amount > 0:
                raise UserError(_('Refund Amount should be greater then Zero.'))

            data = {
                'payment_type': 'outbound',
                'payment_method_id': '2',
                'partner_type': 'supplier',
                'partner_id': rec.student_id.partner_id and rec.student_id.partner_id.id or False,
                'payment_date': fields.Date.today(),
                'communication': "Amount Paid Against the Student Refund",
                'amount': rec.total_refund_amount,
                'journal_id': rec.payment_journal_id and rec.payment_journal_id.id or False,
                # 'invoice_ids': invoice_ids,
                # 'account_analytic_id': invoice.student_id.campus_id.account_analytic_id.id,
                # 'account_analytic_id': False,
                # 'analytic_tag_ids': [],
            }

            pay_rec = self.env['account.payment'].create(data)
            pay_rec.post()
            rec.payment_id = pay_rec.id

            ledger_data = {
                'student_id': rec.student_id.id,
                'debit': 0,
                'credit': rec.total_refund_amount,
                'date': fields.Date.today(),
                'description': "Student Refund Payment",
                'refund_request_id': rec.id,
            }
            ledger_id = self.env['odoocms.student.ledger'].create(ledger_data)
            rec.state = 'done'
            rec.refund_line_ids.write({'state': 'done'})

    def action_refund_cancel(self):
        for rec in self:
            if rec.refund_line_ids:
                rec.refund_line_ids.write({'state':'cancel'})
            rec.state = 'cancel'


class OdooCMSFeeRefundRequestLine(models.Model):
    _name = 'odoocms.fee.refund.request.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Student Fee Refund Request Line'

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence')
    description = fields.Char('Description')
    refund_id = fields.Many2one('odoocms.fee.refund.request', 'Refund')
    refund_amount = fields.Integer(string='Refund Amount', required=True)
    actual_amount = fields.Integer(string='Actual Refund Amount', )
    remarks = fields.Text('Refund Remarks')

    state = fields.Selection([('draft', 'Submitted'),
                              ('approve', 'Approved'),
                              ('reject', 'Rejected'),
                              ('done', 'Done'),
                              ('cancel', 'Canceled')], default='draft', string="Status", tracking=True)

    refund_type = fields.Selection([('admission', 'Admission Tuition'),
                                    ('semester_fee', 'Semester Tuition Fee'),
                                    ('wavier', 'Waiver'),
                                    ('late_fine', 'Late Fine'),
                                    ('security', 'Security'),
                                    ('scholarship', 'Scholarship'),
                                    ('course_drop', 'Course Drop'),
                                    ], string='Refund Type', required=True)

    def refund_granted(self):
        self.state = 'done'

    def cancel_refund_request(self):
        self.state = 'cancel'
