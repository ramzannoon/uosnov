import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging

_logger = logging.getLogger(__name__)


class ReceiptReceivedDetailReport(models.AbstractModel):
    _name = 'report.odoocms_fee.receipt_received_detail_report'
    _description = 'Receipt Received Detail Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        date_from = data['form']['date_from'] and data['form']['date_from'] or False
        date_to = data['form']['date_to'] and data['form']['date_to'] or False
        total_amount = 0
        total_inv_amount = 0
        date_to = fields.Date.from_string(date_to)
        res = {}
        lines = []

        if date_from and date_to:
            date_from = fields.Date.from_string(date_from)
            date_to = fields.Date.from_string(date_to)
            if date_from > date_to:
                raise ValidationError(_('Start Date must be Anterior to End Date'))

            # invoice = self.env['account.move'].search([('payment_date', '>=', date_from), ('payment_date', '<=', date_to), ('invoice_payment_state', '=', 'paid')])
            payment_registers = self.env['odoocms.fee.payment.register'].search([('date', '>=', date_from), ('date', '<=', date_to)])
            if payment_registers:
                for payment_register in payment_registers:
                    for fee_payment_id in payment_register.fee_payment_ids:
                        total_amount += fee_payment_id.received_amount
                        total_inv_amount += fee_payment_id.amount
                        inv_type = ''
                        flag = False
                        if fee_payment_id.invoice_id.donor_id:
                            inv_type = 'ScholarShip Fee'
                            flag = True
                        if not flag and fee_payment_id.invoice_id.receipt_type_ids.filtered(lambda aa: aa.name=='Semester Fee'):
                            inv_type = 'Semester Fee'
                            flag = True
                        if not flag and fee_payment_id.invoice_id.receipt_type_ids.filtered(lambda aa: aa.name=='Hostel Fee'):
                            inv_type = 'Hostel Fee'
                            flag = True
                        if not flag and fee_payment_id.invoice_id.receipt_type_ids.filtered(lambda aa: aa.name=='Adhoc Charges'):
                            inv_type = 'Adhoc Charges'
                            flag = True

                        line = {
                            'student_code': fee_payment_id.student_id.code,
                            'student_name': fee_payment_id.student_id.name,
                            'inv_date': fee_payment_id.invoice_id.invoice_date.strftime('%d-%m-%Y'),
                            'inv_no': fee_payment_id.invoice_id.name,
                            'inv_barcode': fee_payment_id.invoice_id.barcode,
                            'inv_type': inv_type,
                            'inv_amount': fee_payment_id.amount,
                            'received_amount': fee_payment_id.received_amount,
                            'diff': round(fee_payment_id.amount - fee_payment_id.received_amount, 2),
                        }
                        lines.append(line)
            res = lines
            report = self.env['ir.actions.report']._get_report_from_name('odoocms_fee.receipt_received_detail_report')
            docargs = {
                'doc_ids': [],
                'doc_model': report.model,
                'data': data['form'],
                'invoice': res or [],
                'total_amount': round(total_amount, 2) or '',
                'total_inv_amount': round(total_inv_amount, 2) or '',
                'date_from': date_from or False,
                'date_to': date_to or False,
                'amount_diff': round(total_inv_amount - total_amount, 2),
            }
            return docargs
