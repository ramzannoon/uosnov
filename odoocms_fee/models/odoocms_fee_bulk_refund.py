from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import pdb
from datetime import date


class OdooCMSFeeRefundHeads(models.Model):
    _name = 'odoocms.fee.refund.bulk.heads'
    _description = 'Fee Refund Bulk Heads'
    fee_head_id = fields.Many2one('odoocms.fee.head', string='Fee Heads')
    amount = fields.Monetary(compute='calculate_heads_amount', string='Amount', store=True, default=0.0)
    refund_id = fields.Many2one('odoocms.fee.refund.bulk', string='Refund')
    refund_amount = fields.Char(string='Refund Flat/percentage Amount', required=True)
    refund_amount_total = fields.Monetary(compute='calculate_refund_amount', string='Calculated Refund Amount', store=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)
    cancel_reason_id = fields.Many2one('odoocms.fee.refund.reason', 'Refund Cancel Reason')
    remarks = fields.Text('Refund Cancel Remarks')
    state = fields.Selection([('draft', 'Draft'), ('submitted', 'Submitted'), ('approve', 'Approved'), ('done', 'Done'), ('cms_done', 'CMS Done'), ('cancel', 'Canceled')], default='draft', string="Status", track_visibility='onchange')

    @api.onchange('fee_head_id')
    def calculate_heads_amount(self):
        for rec in self:
            if rec.fee_head_id:
                invoice_ids = rec.refund_id.group_id.invoice_ids[0]
                search_amount = self.env['account.move.line'].search([('invoice_id', '=', invoice_ids.id), ('fee_head_id', '=', rec.fee_head_id.id)])
                rec.amount = search_amount.price_unit

    @api.depends('refund_amount', 'fee_head_id')
    def calculate_refund_amount(self):
        for rec in self:
            if rec.refund_amount and rec.fee_head_id:
                if rec.refund_amount.find('%') > 0:
                    refund_amount = eval(rec.refund_amount[0: len(rec.refund_amount) - 1])
                    rec.refund_amount_total = (rec.amount * int(refund_amount)) / 100
                else:
                    rec.refund_amount_total = int(rec.refund_amount)

    def action_cancel_cms(self):
        for rec in self:
            search_invoice = self.env['account.move'].search([('invoice_group_id', '=', self.refund_id.group_id.id), ('state', '=', 'paid')])
            for invoice in search_invoice:
                ledger_data_credit = {
                    'student_id': invoice.student_id.id,
                    'date': self.refund_id.date,
                    'credit': rec.refund_amount_total,
                    'description': "Refund Cancel",
                    'invoice_id': invoice.id,
                }
                ledger_id = self.env['odoocms.student.ledger'].create(ledger_data_credit)
                ledger_data_debit = {
                    'student_id': invoice.student_id.id,
                    'date': self.refund_id.date,
                    'debit': rec.refund_amount_total,
                    'description': rec.fee_head_id.name,
                    'invoice_id': invoice.id,
                }
                ledger_id = self.env['odoocms.student.ledger'].create(ledger_data_debit)
        self.state = 'cancel'


class OdooCMSFeeRefundRequestBulk(models.Model):
    _name = 'odoocms.fee.refund.bulk'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Student Fee Refund in Bulk'
    _rec_name = 'group_id'

    READONLY_STATES = {
        'submitted': [('readonly', True)],
        'approve': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],

    }

    group_id = fields.Many2one('account.move.group', 'Group', states=READONLY_STATES, requied=True)
    # refund_type_id = fields.Selection(
    #     [('late_fine', 'Late Fine'), ('security', 'Security'), ('scholarship', 'Scholarship'),
    #      ('course_drop', 'Course Drop')], string='Refund Type', required=True)
    description = fields.Text('Detailed Description', states=READONLY_STATES, required=True)
    date = fields.Date('Date', default=fields.Date.today, states=READONLY_STATES, required=True, )
    head_ids = fields.Many2many('odoocms.fee.head', string='Fee Heads')

    fee_head_ids = fields.One2many('odoocms.fee.refund.bulk.heads', 'refund_id', string='Fee Heads')
    state = fields.Selection([('draft', 'Draft'), ('submitted', 'Submitted'), ('approve', 'Approved'), ('done', 'Done'), ('cms_done', 'CMS Done'),
                              ('cancel', 'Canceled')], default='draft', string="Status", track_visibility='onchange')
    can_approve = fields.Boolean('Can Approve', compute='_can_approve', track_visibility='onchange')
    cancel_reason_id = fields.Many2one('odoocms.fee.refund.reason', 'Refund Cancel Reason')
    remarks = fields.Text('Refund Cancel Remarks')
    # student_debit_id = fields.Many2one('account.move',string="Account Move")

    @api.onchange('group_id')
    def _get_group_heads(self):
        for rec in self:
            if rec.group_id:
                invoice_ids = rec.group_id.invoice_ids[0].invoice_line_ids
                for head in invoice_ids:
                    rec.head_ids = head.fee_head_id.mapped('id')

    def _can_approve(self):
        can_approve = False
        if self.state=='submitted':
            can_approve = True
        self.can_approve = can_approve

    def action_submitted(self):
        for rec in self:
            activity = self.env.ref('odoocms_fee.mail_request_to_approve_cms_manager')
            rec.activity_schedule('odoocms_fee.mail_request_to_approve_cms_manager', user_id=activity.user_id.id)
            rec.state = 'submitted'

    def action_submitted_cms_manager(self):
        for rec in self:
            rec.state = 'approve'

    def action_submitted_cms(self):
        for rec in self.fee_head_ids:
            search_invoice = self.env['account.move'].search([('invoice_group_id', '=', self.group_id.id), ('state', '=', 'paid')])
            for invoice in search_invoice:
                ledger_data_credit = {
                    'student_id': invoice.student_id.id,
                    'date': self.date,
                    'credit': rec.refund_amount_total,
                    'description': "Refund",
                    'invoice_id': invoice.id,
                }
                ledger_id = self.env['odoocms.student.ledger'].create(ledger_data_credit)
                ledger_data_debit = {
                    'student_id': invoice.student_id.id,
                    'date': self.date,
                    'debit': rec.refund_amount_total,
                    'description': rec.fee_head_id.name,
                    'invoice_id': invoice.id,
                }
                ledger_id = self.env['odoocms.student.ledger'].create(ledger_data_debit)
        self.state = 'cms_done'
        rec.state = 'cms_done'

    def action_cancel_cms(self):
        fee_heads = self.fee_head_ids.filtered(lambda l: l.state=='cms_done')
        for rec in fee_heads:
            search_invoice = self.env['account.move'].search([('invoice_group_id', '=', self.group_id.id), ('state', '=', 'paid')])
            for invoice in search_invoice:
                ledger_data_credit = {
                    'student_id': invoice.student_id.id,
                    'date': self.date,
                    'credit': rec.refund_amount_total,
                    'description': "Refund Cancel",
                    'invoice_id': invoice.id,
                }
                ledger_id = self.env['odoocms.student.ledger'].create(ledger_data_credit)
                ledger_data_debit = {
                    'student_id': invoice.student_id.id,
                    'date': self.date,
                    'debit': rec.refund_amount_total,
                    'description': rec.fee_head_id.name,
                    'invoice_id': invoice.id,
                }
                ledger_id = self.env['odoocms.student.ledger'].create(ledger_data_debit)
        self.state = 'cancel'
        rec.state = 'cancel'

    def action_account_process(self):
        search_invoice = self.env['account.move'].search([('invoice_group_id', '=', self.group_id.id), ('state', '=', 'paid')])
        for invoice in search_invoice:
            fee_heads = self.fee_head_ids.filtered(lambda l: l.state=='cms_done')
            for rec in fee_heads:
                move_lines = []
                if invoice.state == 'paid':
                    search_payment = self.env['odoocms.fee.payment'].search([('receipt_number', '=', invoice.number)])
                    analytic_tags = self.env['account.analytic.tag']
                    analytic_tags += invoice.student_id.program_id.department_id.campus_id.analytic_tag_id
                    analytic_tag_ids = [(6, 0, analytic_tags.ids)]
                    fee_line = {
                        'name': invoice.student_id.name or '',
                        'ref': invoice.number,
                        # 'partner_id': rec.partner_id.id,
                        'debit': rec.refund_amount_total,
                        'credit': 0,
                        # note: will be come from configuration
                        'account_id': rec.fee_head_id.property_account_income_id.id,
                        'sequence': 10,
                        'analytic_tag_ids': analytic_tag_ids,
                    }
                    refund_line = {
                        'name': invoice.student_id.name or '',
                        'ref': invoice.number,
                        'partner_id': invoice.student_id and invoice.student_id.partner_id and invoice.student_id.partner_id.id,
                        'debit': 0,
                        'credit': rec.refund_amount_total,
                        'account_id': search_payment.journal_id.default_credit_account_id.id,
                        'analytic_tag_ids': analytic_tag_ids,
                    }
            move_lines.append((0, 0, fee_line))
            move_lines.append((0, 0, refund_line))
            move_data = {
                'journal_id': search_payment.journal_id.id,
                'line_ids': move_lines,
                'date': date.today(),
                'name': invoice.number,
                'ref': invoice.number,
            }
            # new_move = self.env['account.move'].create(move_data)
            # rec.student_debit_id = new_move.id
            rec.state = 'done'
