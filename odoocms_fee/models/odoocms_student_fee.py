from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import pdb
from datetime import date


class OdoosmsStudentFeeLedger(models.Model):
    _name = "odoocms.student.ledger"
    _description = "Student Ledger"
    _order = "invoice_id,id"

    name = fields.Char(string='Description', default=lambda self: self.env['ir.sequence'].next_by_code('odoocms.student.invoice'), copy=False, readonly=True)
    student_id = fields.Many2one('odoocms.student', string='Student')
    invoice_id = fields.Many2one('account.move', string='Student Invoice')
    payment_id = fields.Many2one('odoocms.fee.payment', string='Payment')
    credit = fields.Monetary(string='Credit', readonly=True, default=0.0)
    debit = fields.Monetary(string='Debit', readonly=True, default=0.0)
    date = fields.Date('Date', default=fields.Date.today, required=True)
    description = fields.Text("Description")
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)
    # scholarship_id = fields.Many2one('odoocms.scholarship',string='Scholarship') Need to add in scholarship module


class OdooCMSFeePayment(models.Model):
    _name = 'odoocms.fee.payment'
    _description = 'Fee Payment'

    name = fields.Char()
    date = fields.Date('Date', required=True, readonly=True, states={'draft': [('readonly', False)]})
    description = fields.Char('Description', readonly=True, states={'draft': [('readonly', False)]})
    amount = fields.Float('Amount', required=True, readonly=True, states={'draft': [('readonly', False)]})
    doc_no = fields.Text('DOC No', readonly=True, states={'draft': [('readonly', False)]})
    id_number = fields.Text('Student ID', readonly=True, states={'draft': [('readonly', False)]})
    receipt_number = fields.Text('Receipt No', required=True, readonly=True, states={'draft': [('readonly', False)]})
    journal_id = fields.Many2one('account.journal', 'Journal', required=True, readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done'), ('error', 'Error')], 'Status', default='draft', readonly=True, states={'draft': [('readonly', False)]})
    student_ledger_id = fields.Many2one('odoocms.student.ledger', String='Student Ledger')
    transaction_date = fields.Date('Transaction Date', default=fields.Date.today, required=True)
    tag = fields.Char('Batch-ID/Tag', help='Attach the tag', readonly=True)

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Student Fee Payments'),
            'template': '/odoocms_fee/static/xls/fee_collection.xlsx'
        }]
