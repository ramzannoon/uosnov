from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import pdb
from datetime import date


class OdooCMSStudentFeeLedger(models.Model):
    _name = "odoocms.student.ledger"
    _inherit = ['odoocms.student.fee.public']
    _description = "Student Ledger"
    _order = "id asc"

    name = fields.Char(string='Name')
    sequence = fields.Integer('Sequence')
    student_id = fields.Many2one('odoocms.student', string='Student')
    id_number = fields.Char('Student ID')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    payment_id = fields.Many2one('odoocms.fee.payment', string='Payment')
    credit = fields.Monetary(string='Credit', readonly=True, default=0.0)
    debit = fields.Monetary(string='Debit', readonly=True, default=0.0)
    date = fields.Date('Date', default=fields.Date.today, required=True)
    description = fields.Text("Description")
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)

    balance = fields.Float(string='Balance', compute='compute_ledger_balance', store=True)
    balance_str = fields.Char(string='Balance String', compute='compute_ledger_balance', store=True)
    slip_barcode = fields.Char(string='Barcode', compute='compute_slip_barcode', store=True)
    is_defer_entry = fields.Boolean('Is Defer Entry', default=False)
    to_be = fields.Boolean('To Be', default=False)

    refund_request_id = fields.Many2one('odoocms.fee.refund.request', 'Refund Request')

    # scholarship_id = fields.Many2one('odoocms.scholarship',string='Scholarship') Need to add in scholarship module

    @api.depends('credit', 'debit')
    def compute_ledger_balance(self):
        for rec in self:
            balance = 0
            lines = self.env['odoocms.student.ledger'].search([('student_id', '=', rec.student_id.id)])
            for line in lines:
                balance = round((line.debit - line.credit + balance), 4)
                if balance < 0:
                    line.balance = balance
                    line.balance_str = "(" + str(abs(balance)) + ")"
                else:
                    line.balance_str = str(balance)
                    line.balance = balance

    @api.depends('invoice_id', 'payment_id')
    def compute_slip_barcode(self):
        for rec in self:
            rec.slip_barcode = rec.invoice_id.barcode and rec.invoice_id.barcode or ''

    def unlink(self):
        for rec in self:
            # users = self.env['res.groups'].search([('name', '=', 'Odoo CMS Super')]).users
            if not self.env.user.id==2:
                raise UserError('You Cannot Delete this record, Please Contact the System Administrator.')
            rec.action_create_ledger_deletion_log()
            return super(OdooCMSStudentFeeLedger, self).unlink()

    def action_create_ledger_deletion_log(self):
        for rec in self:
            values = {
                'name': rec.name,
                'ledger_id': rec.id,
                'invoice_id': rec.invoice_id and rec.invoice_id.id or False,
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
            self.env['odoocms.student.fee.ledger.deletion.log'].create(values)

    def write(self, values):
        ledger_change_id = False
        new_debit = 0
        new_credit = 0
        new_balance = ''
        if values.get('debit', False) or values.get('credit', False):
            old_debit = self.debit
            old_credit = self.credit
            old_balance = self.balance_str

            if values.get('debit', False):
                new_debit = values['debit']
            if values.get('credit', False):
                new_credit = values['credit']

            change_log_values = {
                'name': self.name,
                'invoice_id': self.invoice_id and self.invoice_id.id or False,
                'student_id': self.student_id and self.student_id.id or False,
                'session_id': self.student_id.session_id and self.student_id.session_id.id or False,
                'career_id': self.student_id.career_id and self.student_id.career_id.id or False,
                'institute_id': self.student_id.institute_id and self.student_id.institute_id.id or False,
                'campus_id': self.student_id.campus_id and self.student_id.campus_id.id or False,
                'program_id': self.student_id.program_id and self.student_id.program_id.id or False,
                'discipline_id': self.student_id.discipline_id and self.student_id.discipline_id.id or False,
                'term_id': self.student_id.term_id and self.student_id.term_id.id or False,
                'semester_id': self.student_id.semester_id and self.student_id.semester_id.id or False,
                'ledger_id': self.id,
                'old_debit': old_debit,
                'old_credit': old_credit,
                'old_balance': old_balance,
                'new_debit': new_debit,
                'new_credit': new_credit,
            }
            ledger_change_id = self.env['odoocms.student.fee.ledger.changes.log'].create(change_log_values)

        res = super(OdooCMSStudentFeeLedger, self).write(values)
        if ledger_change_id:
            ledger_change_id.new_balance = self.balance_str
        return res

    @api.model
    def create(self, values):
        res = super(OdooCMSStudentFeeLedger, self).create(values)
        if not res.sequence:
            res.name = self.env['ir.sequence'].next_by_code('odoocms.student.ledger')
        return res
