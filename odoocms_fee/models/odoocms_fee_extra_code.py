from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import pdb
from datetime import date

# This Code is Copied from odoocms_fee.py


class OdooCMSFeeStructureStudent(models.Model):
    _name = 'odoocms.fee.structure.student'
    _description = 'Fee Structure Student'

    category_id = fields.Many2one('odoocms.fee.category', string='Category', required=True)
    fee_head_id = fields.Many2one('odoocms.fee.head', string='Fee', required=True)
    fee_type = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage')], 'Type', default='fixed')
    amount = fields.Float('Amount', tracking=True)
    percentage = fields.Float('Percentage', )
    percentage_of = fields.Many2one('odoocms.fee.structure.head.line', '% Of')

    payment_type = fields.Selection([('admissiontime', 'Admission Time'),
                                     ('permonth', 'Per Month'),
                                     ('peryear', 'Per Year'),
                                     ('persemester', 'Per Semester'),
                                     ('persubject', 'Per Subject'),
                                     ('onetime', 'One Time'),
                                     ], string='Payment Type', related="fee_head_id.payment_type")
    fee_description = fields.Text('Description', related='fee_head_id.description_sale')
    note = fields.Char('Note')
    student_id = fields.Many2one('odoocms.student', 'Student')

    _sql_constraints = [('feehead_student', 'unique(fee_head_id,student_id)', "Another Fee Line already exists with this Head and Student!"), ]

    @api.onchange('student_id', 'fee_head_id')
    def onchange_fee_head(self):
        if self.student_id and self.fee_head_id:
            fee_structure = self.env['odoocms.fee.structure'].search(
                [('session_id', '=', self.student_id.session_id.id)])
            fee_line = fee_structure.line_ids.filtered(lambda l: l.fee_head_id.id==self.fee_head_id.id)
            # Now Search from Head Line
            if fee_line:
                self.amount = fee_line.amount  # or percentage


# class OdoocmsInvoice(models.Model):
#     _name = "odoocms.invoice"
#     _description = "Student Invoice"
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#
#     name = fields.Char('Receipt Number')
#     student_id = fields.Many2one('odoocms.student', string='Student', readonly=True, states={'draft': [('readonly', False)]})
#     student_name = fields.Char(string='Name', related='student_id.partner_id.name', store=True)
#     program_id = fields.Many2one(related='student_id.program_id',string='Program')
#     batch_id = fields.Many2one(related='student_id.batch_id', store=True)
#
#     fee_structure_id = fields.Many2one('odoocms.fee.structure', string='Fee Structure',readonly=True, states={'draft': [('readonly', False)]})
#
#     academic_semester_id = fields.Many2one('odoocms.academic.semester','Academic Term')
#     tag = fields.Char('Tag',help='Attach the tag',readonly=True)
#
#     date_invoice = fields.Date(string='Invoice Date', readonly=True, states={'draft': [('readonly', False)]}, index=True,
#         help="Keep empty to use the current date", copy=False)
#     date_due = fields.Date(string='Due Date', readonly=True, states={'draft': [('readonly', False)]}, index=True, copy=False,)
#     date_payment = fields.Date('Payment Date')
#
#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('unpaid', 'Unpaid'),
#         ('open', 'Open'),
#         ('in_payment', 'In Payment'),
#         ('paid', 'Paid'),
#         ('cancel', 'Cancelled'),
#     ], string='Status', index=True, readonly=True, default='draft',
#         track_visibility='onchange', copy=False,
#         help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
#              " * The 'Open' status is used when user creates invoice, an invoice number is generated. It stays in the open status till the user pays the invoice.\n"
#              " * The 'In Payment' status is used when payments have been registered for the entirety of the invoice in a journal configured to post entries at bank reconciliation only, and some of them haven't been reconciled with a bank statement line yet.\n"
#              " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
#              " * The 'Cancelled' status is used when user cancel invoice.")
#
#     line_ids = fields.One2many('odoocms.invoice.line', 'invoice_id', string='Receipt Lines', copy=True)
#     amount_total = fields.Monetary(string="Amount Total")
#     currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True, states={'draft': [('readonly', False)]},
#          track_visibility='always')
#
#
# class OdoosmsStudentFeeLine(models.Model):
#     _name = "odoocms.invoice.line"
#     _description = "Invoice Line"
#     _order = "invoice_id,id"
#
#     name = fields.Char(string='Description', required=True)
#     item_type = fields.Char('Item Type')
#     item_type_code = fields.Char('Item Type Code')
#     fee_head_id = fields.Many2one('odoocms.fee.head','Fee Head')
#     fee_category_id = fields.Many2one('odoocms.fee.category','Fee Category',related='fee_head_id.category_id',store=True)
#     amount = fields.Monetary(string='Item Amount', readonly=True)
#     paid_amount = fields.Monetary(string='Applied Amount', readonly=True)
#     balance = fields.Monetary(string='Balance', readonly=True, help="Total Balance")
#
#     account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
#     analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
#     invoice_id = fields.Many2one('odoocms.invoice',string='Student Invoice')
#     currency_id = fields.Many2one('res.currency', string='Currency', readonly=True, track_visibility='always')
#     prev_invoice_no = fields.Char()