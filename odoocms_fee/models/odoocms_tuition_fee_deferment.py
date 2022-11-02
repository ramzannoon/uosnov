from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools.safe_eval import safe_eval
import pdb


class OdooCMSTuitionFeeDefermentRequest(models.Model):
    _name = 'odoocms.tuition.fee.deferment.request'
    _inherit = ['odoocms.student.fee.public']
    _description = "Fee Deferment Requests"

    name = fields.Char('Name')
    sequence = fields.Char('Sequence')
    student_id = fields.Many2one('odoocms.student', 'Student Name', tracking=True)
    request_date = fields.Date('Request Date', required=True, default=lambda self: fields.Date.today(), tracking=True)
    approve_date = fields.Date('Approve Date', tracking=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('submit', 'Submit'),
                              ('approved', 'Approved'),
                              ('reject', 'Rejected')], string='Status', tracking=True, default='draft')

    defer_type = fields.Selection([('fixed', 'Fixed'),
                                   ('percentage', 'Percentage')], default='fixed', string='Type')
    line_ids = fields.One2many('odoocms.tuition.fee.deferment.line', 'deferment_id', 'Deferment Details')
    semester_tuition_fee = fields.Float('Tuition Fee', compute='get_tuition_fee', store=True)
    defer_value = fields.Float('Defer Value')
    total_amount = fields.Float('Total Defer Amount', compute='_compute_totals', store=True)
    total_paid_amount = fields.Float('Total Paid Defer Amount', compute='_compute_totals', store=True)
    total_unpaid_amount = fields.Float('Total Unpaid Defer Amount', compute='_compute_totals', store=True)
    approved_tuition_fee = fields.Float('Approved Fee', compute='_compute_approved_fee', store=True)
    installments_start_date = fields.Date('Installments Start Date', tracking=True)

    notes = fields.Text('Notes', tracking=True)
    to_be = fields.Boolean('To Be', default=False)

    @api.constrains('student_id', 'career_id')
    def student_constrains(self):
        for rec in self:
            if rec.student_id:
                already_exist = self.env['odoocms.tuition.fee.deferment.request'].search([('student_id', '=', rec.student_id.id),
                                                                                          ('career_id', '=', rec.career_id.id),
                                                                                          ('id', '!=', rec.id),
                                                                                          ('state', '!=', 'reject')])
                if already_exist:
                    raise UserError(_('This Student Request for the deferment is already Available in System. Duplicates are not Allowed.'))

    @api.model
    def create(self, values):
        if not values.get('sequence', False):
            values['name'] = self.env['ir.sequence'].next_by_code('odoocms.tuition.fee.deferment.request')
        result = super(OdooCMSTuitionFeeDefermentRequest, self).create(values)
        return result

    def unlink(self):
        for rec in self:
            if not rec.state=='draft':
                raise UserError('You can delete the records which are in Draft state, Please contact the System Administrator.')
        return super(OdooCMSTuitionFeeDefermentRequest, self).unlink()

    def action_submit(self):
        for rec in self:
            rec.state = 'submit'

    def action_approved(self):
        for rec in self:
            rec.state = 'approved'
            rec.approve_date = fields.Date.today()

    def action_rejected(self):
        for rec in self:
            rec.state = 'reject'

    @api.depends('line_ids', 'line_ids.amount', 'line_ids.paid_amount')
    def _compute_totals(self):
        for rec in self:
            total_amt = 0
            total_paid_amt = 0
            total_unpaid = 0
            if rec.line_ids:
                for line in rec.line_ids:
                    total_amt += line.amount
                    total_paid_amt += line.paid_amount

            rec.total_amount = total_amt
            rec.total_paid_amount = total_paid_amt
            rec.total_unpaid_amount = total_amt - total_paid_amt

    @api.constrains('semester_tuition_fee')
    def semester_fee_constrain(self):
        for rec in self:
            # if rec.semester_tuition_fee <= 0:
            if rec.semester_tuition_fee < 0:
                raise UserError(_('Semester Fee Should be Greater then Zero.'))

    @api.depends('defer_value', 'defer_type', 'semester_tuition_fee')
    def _compute_approved_fee(self):
        for rec in self:
            approved_amt = 0
            if rec.semester_tuition_fee > 0:
                if rec.defer_type=='percentage':
                    if rec.defer_value < 100:
                        approved_amt = round(rec.semester_tuition_fee * rec.defer_value / 100)
                    else:
                        raise UserError(_('Percentage should be less then 100%.'))

                if rec.defer_type=='fixed':
                    if rec.defer_value < rec.semester_tuition_fee:
                        approved_amt = rec.semester_tuition_fee - rec.defer_value
                    else:
                        raise UserError(_('Fixed Amount should be Less then Semester Fee'))
            rec.approved_tuition_fee = approved_amt

    @api.depends('student_id', 'term_id', 'career_id')
    def get_tuition_fee(self):
        for rec in self:
            tuition_fee = 0
            fee_structure = self.env['odoocms.fee.structure'].search([('session_id', '=', self.session_id.id),
                                                                      ('term_id', '=', rec.term_id.id),
                                                                      ('career_id', '=', rec.career_id.id)])
            if not fee_structure:
                fee_structure = self.env['odoocms.fee.structure'].search([('session_id', '=', self.session_id.id),
                                                                          ('career_id', '=', rec.career_id.id)], order='id desc', limit=1)
            if fee_structure:
                fee_structure_heads = fee_structure.head_ids.filtered(lambda l: l.category_id.name=='Tuition Fee')
                if fee_structure_heads:
                    for fee_structure_head in fee_structure_heads:
                        for fee_structure_head_line in fee_structure_head.line_ids:
                            if self.env['odoocms.student'].search(safe_eval(fee_structure_head_line.domain) + [('id', '=', self.student_id.id)]):
                                tuition_fee = fee_structure_head_line.amount
            rec.semester_tuition_fee = tuition_fee


class OdooCMSTuitionFeeDefermentLine(models.Model):
    _name = 'odoocms.tuition.fee.deferment.line'
    _description = "Fee Deferment Detail"

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence')
    student_id = fields.Many2one('odoocms.student', 'Student')
    deferment_id = fields.Many2one('odoocms.tuition.fee.deferment.request', 'Deferment Request')
    invoice_date = fields.Date('Invoice Date')
    invoice_date_due = fields.Date('Due Date')
    original_invoice_id = fields.Many2one('account.move', 'Invoice')
    defer_invoice_id = fields.Many2one('account.move', 'Deferment Invoice')
    payment_id = fields.Many2one('account.payment', 'Payment Ref')
    amount = fields.Float(string="Invoice Amount")
    paid_amount = fields.Float('Paid Amount')
    state = fields.Selection([('draft', 'Not Paid'),
                              ('done', 'Paid')], default='draft', string='Status')
