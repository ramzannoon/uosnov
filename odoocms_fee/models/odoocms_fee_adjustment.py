from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import pdb
from datetime import date


class OdooCMSFeeAdjustmentHeads(models.Model):
    _name = 'odoocms.fee.adjustment.heads'
    _description = 'Fee Adjustment Security Heads'

    fee_head_id = fields.Many2one('odoocms.fee.head', string='Fee Heads', readonly=True)
    amount = fields.Monetary(string='Amount', readonly=True, default=0.0)
    refund_id = fields.Many2one('odoocms.fee.adjustment.request', string='Adjustment')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)


class OdooCMSFeeAdjustmentRequest(models.Model):
    _name = 'odoocms.fee.adjustment.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Student Fee Adjustment Request'
    # _rec_name = 'student_id'

    READONLY_STATES = {
        'submitted': [('readonly', True)],
        'approve': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence')
    student_id = fields.Many2one('odoocms.student', 'Student', states=READONLY_STATES, requied=True)
    session_id = fields.Many2one('odoocms.academic.session', 'Academic Session', states=READONLY_STATES)
    career_id = fields.Many2one('odoocms.career', 'Academic Level', states=READONLY_STATES)
    program_id = fields.Many2one('odoocms.program', 'Program', states=READONLY_STATES)
    batch_id = fields.Many2one('odoocms.batch', states=READONLY_STATES)
    institute_id = fields.Many2one('odoocms.institute', 'School', states=READONLY_STATES)
    discipline_id = fields.Many2one('odoocms.discipline', 'Discipline', states=READONLY_STATES)
    campus_id = fields.Many2one('odoocms.campus', 'Campus', states=READONLY_STATES)
    semester_id = fields.Many2one('odoocms.semester', 'Semester', states=READONLY_STATES)
    term_id = fields.Many2one('odoocms.academic.term', 'Term', states=READONLY_STATES)

    description = fields.Text('Detailed Description', states=READONLY_STATES, required=True)
    date = fields.Date('Date', default=fields.Date.today, states=READONLY_STATES, required=True)
    adjustment_ids = fields.One2many('odoocms.fee.adjustment.request.line', 'adjustment_id', string='Fee Adjustment')
    state = fields.Selection([('draft', 'Submitted'),
                              ('approve', 'Approved'),
                              ('done', 'Done'),
                              ('cancel', 'Canceled')
                              ], default='draft', string="Status", tracking=True)

    reason_id = fields.Many2one('odoocms.fee.refund.reason', 'Reason', requied=True)
    remarks = fields.Text('Adjustment Cancel Remarks')
    total_amount = fields.Float('Total Amount', compute='_compute_total_amount', store=True)
    total_refund_amount = fields.Float('Total Adjusted Amount', compute='_compute_total_refund', store=True)
    student_ledger_id = fields.Many2one('odoocms.student.ledger', 'Ledger Ref', tracking=True)
    refund_type_id = fields.Selection([('late_fine', 'Late Fine'),
                                       ('security', 'Security'),
                                       ('scholarship', 'Scholarship'),
                                       ('course_drop', 'Course Drop'),
                                       ('extra', 'Extra Amount Paid'),
                                       ('tax', 'Advance Tax Paid'),
                                       ('other', 'Other')
                                       ], string='Type', required=True)

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

    @api.depends('adjustment_ids', 'adjustment_ids.actual_amount')
    def _compute_total_amount(self):
        for rec in self:
            total_amount = 0
            if rec.adjustment_ids:
                for line in rec.adjustment_ids:
                    total_amount += line.actual_amount
            rec.total_amount = total_amount

    @api.depends('adjustment_ids', 'adjustment_ids.refund_amount')
    def _compute_total_refund(self):
        for rec in self:
            total_refund = 0
            if rec.adjustment_ids:
                for line in rec.adjustment_ids:
                    total_refund += line.refund_amount
            rec.total_refund_amount = total_refund

    @api.model
    def create(self, values):
        if not values.get('name', False):
            values['name'] = self.env['ir.sequence'].next_by_code('odoocms.fee.adjustment.request')
        result = super(OdooCMSFeeAdjustmentRequest, self).create(values)
        return result

    def action_approve_refund(self):
        for rec in self:
            if not rec.adjustment_ids:
                raise UserError(_('Please Enter the Detail.'))
            rec.adjustment_ids.write({'state': 'approve'})
            rec.state = 'approve'

    def action_refund_done(self):
        for rec in self:
            if rec.adjustment_ids:
                if rec.total_refund_amount > 0:
                    ledger_data = {
                        'student_id': rec.student_id.id,
                        'debit': rec.total_refund_amount,
                        'credit': 0,
                        'date': fields.Date.today(),
                        'description': "Student Adjustments ",
                    }
                    ledger_id = self.env['odoocms.student.ledger'].create(ledger_data)
                    rec.student_ledger_id = ledger_id and ledger_id.id or False
            rec.adjustment_ids.write({'state': 'done'})
            rec.state = 'done'

    def action_cancel_refund(self):
        for rec in self:
            if rec.adjustment_ids:
                rec.adjustment_ids.write({'state': 'cancel'})
            rec.state = 'cancel'

    def unlink(self):
        for rec in self:
            if not rec.state=='draft':
                raise UserError('You Cannot Delete this record, Please contact the System Administrator.')
        return super(OdooCMSFeeAdjustmentRequest, self).unlink()


class OdooCMSFeeAdjustmentRequestLine(models.Model):
    _name = 'odoocms.fee.adjustment.request.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Student Fee Adjustment Request Line'

    description = fields.Char('Description')
    refund_type_id = fields.Selection([('late_fine', 'Late Fine'),
                                       ('security', 'Security'),
                                       ('scholarship', 'Scholarship'),
                                       ('course_drop', 'Course Drop'),
                                       ('extra', 'Extra Amount Paid'),
                                       ('other', 'Other')
                                       ], string='Type', required=True)

    refund_amount = fields.Integer(string='Adjustment Amount', required=True)
    actual_amount = fields.Integer(string='Actual Adjustment Amount')
    adjustment_id = fields.Many2one('odoocms.fee.adjustment.request', string='Adjustment')

    state = fields.Selection([('draft', 'Submitted'),
                              ('approve', 'Approved'),
                              ('done', 'Done'),
                              ('cancel', 'Canceled')
                              ], default='draft', string="Status", tracking=True)


class OdooCMSFeeAdjustmentRequestReversal(models.Model):
    _name = 'odoocms.fee.adjustment.request.reversal'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Student Fee Adjustment Request Reversal'

    READONLY_STATES = {
        'submitted': [('readonly', True)],
        'approve': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence')
    student_id = fields.Many2one('odoocms.student', 'Student', states=READONLY_STATES, requied=True)
    session_id = fields.Many2one('odoocms.academic.session', 'Academic Session', states=READONLY_STATES)
    career_id = fields.Many2one('odoocms.career', 'Academic Level', states=READONLY_STATES)
    program_id = fields.Many2one('odoocms.program', 'Program', states=READONLY_STATES)
    batch_id = fields.Many2one('odoocms.batch', states=READONLY_STATES)
    institute_id = fields.Many2one('odoocms.institute', 'School', states=READONLY_STATES)
    discipline_id = fields.Many2one('odoocms.discipline', 'Discipline', states=READONLY_STATES)
    campus_id = fields.Many2one('odoocms.campus', 'Campus', states=READONLY_STATES)
    semester_id = fields.Many2one('odoocms.semester', 'Semester', states=READONLY_STATES)
    term_id = fields.Many2one('odoocms.academic.term', 'Term', states=READONLY_STATES)

    date = fields.Date('Date', default=fields.Date.today, states=READONLY_STATES, required=True)
    adjustment_request_id = fields.Many2one('odoocms.fee.adjustment.request', string='Adjustment Request')
    student_ledger_id = fields.Many2one('odoocms.student.ledger', 'Ledger Ref', tracking=True)
    state = fields.Selection([('draft', 'Submitted'),
                              ('approve', 'Approved'),
                              ('done', 'Done'),
                              ('cancel', 'Canceled')
                              ], default='draft', string="Status", tracking=True)
    remarks = fields.Text('Adjustment Cancel Remarks')

    @api.onchange('adjustment_request_id')
    def onchange_adjustment_request(self):
        for rec in self:
            if rec.adjustment_request_id:
                rec.student_id = rec.adjustment_request_id.student_id and rec.adjustment_request_id.student_id.id or False
                rec.session_id = rec.adjustment_request_id.session_id and rec.adjustment_request_id.session_id.id or False
                rec.career_id = rec.adjustment_request_id.career_id and rec.adjustment_request_id.career_id.id or False
                rec.program_id = rec.adjustment_request_id.program_id and rec.adjustment_request_id.program_id.id or False
                rec.batch_id = rec.adjustment_request_id.batch_id and rec.adjustment_request_id.batch_id.id or False
                rec.term_id = rec.adjustment_request_id.term_id and rec.adjustment_request_id.term_id.id or False
                rec.semester_id = rec.adjustment_request_id.semester_id and rec.adjustment_request_id.semester_id.id or False
                rec.discipline_id = rec.adjustment_request_id.discipline_id and rec.adjustment_request_id.discipline_id.id or False
                rec.institute_id = rec.adjustment_request_id.institute_id and rec.adjustment_request_id.institute_id.id or False
                rec.campus_id = rec.adjustment_request_id.campus_id and rec.adjustment_request_id.campus_id.id or False

    @api.model
    def create(self, values):
        if not values.get('name', False):
            values['name'] = self.env['ir.sequence'].next_by_code('odoocms.fee.adjustment.request.reversal')
        result = super(OdooCMSFeeAdjustmentRequestReversal, self).create(values)
        return result

    def action_approve_refund(self):
        for rec in self:
            if not rec.adjustment_request_id:
                raise UserError(_('Please Select the Adjustment Request for Reversal'))
            rec.adjustment_request_id.write({'state': 'approve'})
            rec.state = 'approve'

    def action_refund_done(self):
        for rec in self:
            if rec.adjustment_request_id and rec.adjustment_request_id.student_ledger_id:
                ledger_data = {
                    'student_id': rec.student_id.id,
                    'debit': 0,
                    'credit': rec.adjustment_request_id.student_ledger_id.debit,
                    'date': rec.date,
                    'description': "Student Adjustments Reversal",
                }
                ledger_id = self.env['odoocms.student.ledger'].create(ledger_data)
                rec.student_ledger_id = ledger_id and ledger_id.id or False
            rec.adjustment_request_id.write({'state': 'cancel'})
            rec.state = 'done'

    def action_cancel_refund(self):
        for rec in self:
            rec.state = 'cancel'

    def unlink(self):
        for rec in self:
            if not rec.state=='draft':
                raise UserError('You Cannot Delete this record, Please contact the System Administrator.')
        return super(OdooCMSFeeAdjustmentRequestReversal, self).unlink()
