import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
from odoo.http import request

import logging

_logger = logging.getLogger(__name__)


class StudentTaxCertificateReport(models.AbstractModel):
    _name = 'report.odoocms_fee.student_tax_certificate_report'
    _description = 'Student Tax Certificate Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        if data is None:
            raise UserError(_("Please Select the Required Data form Report Extraction."))
        student_id = data['form']['student_id'] and data['form']['student_id'][0] or False
        term_id = data['form']['term_id'] and data['form']['term_id'][0] or False
        student = self.env['odoocms.student'].browse(student_id)
        term = self.env['odoocms.academic.term'].browse(term_id)

        report = self.env['ir.actions.report']._get_report_from_name('odoocms_fee.student_tax_certificate_report')
        current_time = fields.datetime.now() + relativedelta(hours=5)
        current_time = current_time.strftime('%d-%b-%Y %H:%M %p')
        payment_info = self.get_receipt_payment_detail_amount(student, term)
        student_cpr_line = self.env['odoocms.student.cpr.no'].search([('student_id', '=', student_id), ('term_id', '=', term_id)])

        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'company': request.env.user.company_id,
            'current_time': current_time,
            'student': student,
            # 'tax_amount': self.get_tax_amount(student, term),
            'tax_amount': student_cpr_line.tax_amount,
            'fee_amount': student_cpr_line.fee_amount,
            'receipt_amount': student_cpr_line.fee_amount,
            'company_name': 'IAC',
            'deposit_date': student_cpr_line.register_id.date,
            'bank': student_cpr_line.register_id.bank_name,
            'branch': student_cpr_line.register_id.branch_name,
            'cpr_no': student_cpr_line.register_id.cpr_no,
            'f_year': student_cpr_line.register_id.financial_year
        }
        return docargs

    def get_tax_amount(self, student_id, term_id):
        tax_amount = 0
        if student_id and term_id:
            tax_fee_head = self.env['odoocms.fee.head'].search([('name', 'in', ('Advance Tax', 'Tax'))])
            move_lines = self.env['account.move.line'].search([('move_id.term_id', '=', term_id.id),
                                                               ('fee_head_id', '=', tax_fee_head.id),
                                                               ('move_id.student_id', '=', student_id.id),
                                                               ('move_id.move_type', '=', 'out_invoice'),
                                                               ('move_id.reversed_entry_id', '=', False),
                                                               '|', ('move_id.invoice_payment_state', '!=', 'cancel'),
                                                               ('move_id.state', '!=', 'cancel')])
            if move_lines:
                for move_line in move_lines:
                    tax_amount += move_line.price_subtotal
        return tax_amount

    def get_receipt_total_amount(self, student_id, term_id):
        receipt_amount = 0
        if student_id and term_id:
            receipts = self.env['account.move'].search([('term_id', '=', term_id.id),
                                                        ('student_id', '=', student_id.id),
                                                        ('move_type', '=', 'out_invoice'),
                                                        ('reversed_entry_id', '=', False),
                                                        '|', ('invoice_payment_state', '!=', 'cancel'),
                                                        ('state', '!=', 'cancel')])
            if receipts:
                for receipt in receipts:
                    receipt_amount += receipt.amount_total
        return receipt_amount

    def get_receipt_payment_detail_amount(self, student_id, term_id):
        ret_dic = {'paid_date': '',
                   'bank': 'HBL',
                   'branch': 'NUST Sector H-12Islamabad',
                   'cpr_no': ''}
        for rec in self:
            if student_id and term_id:
                tax_fee_head = self.env['odoocms.fee.head'].search([('name', 'in', ('Advance Tax', 'Tax'))])
                move_line = self.env['account.move.line'].search([('move_id.term_id', '=', term_id.id),
                                                                  ('move_id.student_id', '=', student_id.id),
                                                                  ('move_id.move_type', '=', 'out_invoice'),
                                                                  ('fee_head_id', '=', tax_fee_head.id),
                                                                  ('move_id.reversed_entry_id', '=', False),
                                                                  ('move_id.invoice_payment_state', 'in', ('in_payment', 'paid')),
                                                                  ])
                if move_line:
                    move_line = move_line[0]
                    ret_dic['paid_date'] = move_line.move_id.payment_date
        return ret_dic
