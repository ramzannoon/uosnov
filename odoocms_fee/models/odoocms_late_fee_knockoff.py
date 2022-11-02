import time
import datetime
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, UserError
import pdb
import logging

_logger = logging.getLogger(__name__)


class OdooCMSLateFeeKnockoffRequest(models.Model):
    _name = 'odoocms.late.fee.knockoff.request'
    _inherit = ['odoocms.student.fee.public']
    _description = "Student Late Fee Waive Off Requests"

    name = fields.Char(string='Name')
    sequence = fields.Integer('Sequence')
    student_id = fields.Many2one('odoocms.student', string='Student', tracking=True, index=True)
    invoice_id = fields.Many2one('account.move', string='Student Invoice', tracking=True, index=True)
    invoice_date_due = fields.Date('Invoice Due Date', related='invoice_id.invoice_date_due', store=True)
    invoice_date = fields.Date('Invoice Date', related='invoice_id.invoice_date', store=True)
    invoice_first_due_date = fields.Date('1st After Due Date', tracking=True, compute="_compute_due_date", store=True)
    invoice_second_due_date = fields.Date('2nd After Due Date', tracking=True, compute="_compute_due_date", store=True)
    new_due_date = fields.Date('New Due Date', tracking=True)
    late_fine_amount = fields.Float('Late Fine AMount', tracking=True, compute='_compute_due_date', store=True)
    invoice_amount = fields.Float('Invoice Amount', compute='_compute_invoice_amt', store=True)
    request_date = fields.Date('Request Date', default=fields.Date.today(), tracking=True)
    approve_date = fields.Date('Approved Date')
    reject_date = fields.Date('Rejected Date')
    is_first_due_date_passed = fields.Boolean('Is First Due Date Passed?', compute='_compute_due_date', store=True)
    is_second_due_date_passed = fields.Boolean('Is Second Due Date Passed?', compute='_compute_due_date', store=True)
    state = fields.Selection([('draft', 'Request'),
                              ('hod', 'HOD'),
                              ('ddf', 'DDF'),
                              ('approve', 'Approved'),
                              ('reject', 'Rejected'),
                              ('fee_manager', 'Fee Manager')], string='Status', default='draft', indedx=True)
    remarks = fields.Text('Remarks')

    @api.model
    def create(self, values):
        if not values.get('sequence', False):
            values['name'] = self.env['ir.sequence'].next_by_code('odoocms.late.fee.knockoff.request')
        result = super(OdooCMSLateFeeKnockoffRequest, self).create(values)
        return result

    def unlink(self):
        for rec in self:
            if not rec.state == 'draft':
                raise UserError('You can Delete records in Draft State only.')
        return super(OdooCMSLateFeeKnockoffRequest, self).unlink()

    def action_hod(self):
        for rec in self:
            rec.state = 'hod'

    def action_dd_fin(self):
        for rec in self:
            rec.state = 'ddf'

    def action_approved(self):
        for rec in self:
            if not rec.new_due_date:
                raise UserError(_('Please enter the New Due Date of the Invoice.'))
            if not rec.invoice_id:
                raise UserError(_('Please, select the Invoice.'))
            old_due_date = rec.invoice_id.invoice_date_due
            rec.invoice_id.invoice_date_due = rec.new_due_date
            msg = "Invoice Due Date has been changed from %s to %s" %(old_due_date.strftime("%d-%m-%y"), rec.new_due_date.strftime("%d-%m-%y"))
            rec.invoice_id.message_post(body=msg)
            rec.state = 'approve'
            rec.approve_date = fields.Date.today()

    def action_rejected(self):
        for rec in self:
            rec.state = 'reject'
            rec.reject_date = fields.Date.today()

    def action_fee_manager(self):
        for rec in self:
            rec.state = 'fee_manager'

    @api.onchange('student_id')
    def get_student_invoice(self):
        for rec in self:
            if rec.student_id:
                invoice_id = self.env['account.move'].search([('student_id', '=', rec.student_id.id),
                                                              ('invoice_payment_state', '=', 'unpaid')], order='id desc', limit=1)
                if invoice_id:
                    rec.invoice_id = invoice_id.id
                    rec.invoice_amount = invoice_id.amount_residual
                else:
                    rec.invoice_id = False

    @api.depends('invoice_id')
    def _compute_invoice_amt(self):
        for rec in self:
            if rec.invoice_id:
                rec.invoice_amount = rec.invoice_id.amount_residual
            else:
                rec.invoice_amount = 0

    @api.depends('invoice_id')
    def _compute_due_date(self):
        late_fine_amount = 0
        for rec in self:
            if rec.invoice_id and rec.invoice_id.invoice_date_due:
                rec.invoice_first_due_date = rec.invoice_id.invoice_date_due + datetime.timedelta(days=15)
                rec.invoice_second_due_date = rec.invoice_id.invoice_date_due + datetime.timedelta(days=30)
                if rec.request_date > rec.invoice_first_due_date:
                    rec.is_first_due_date_passed = True
                    late_fine_amount = round(rec.invoice_id.amount_total * .05, 2)

                else:
                    rec.is_first_due_date_passed = False

                if rec.request_date > rec.invoice_second_due_date:
                    rec.is_second_due_date_passed = True
                    late_fine_amount = round(rec.invoice_id.amount_total * 0.1, 2)
                else:
                    rec.is_invoice_second_due_date = False
            else:
                rec.invoice_first_due_date = ''
                rec.invoice_second_due_date = ''
                rec.is_first_due_date_passed = False
                rec.is_second_due_date_passed = False
            rec.late_fine_amount = late_fine_amount
