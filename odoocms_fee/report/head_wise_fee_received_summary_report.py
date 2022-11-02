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


class HeadWiseFeeReceivedSummaryReport(models.AbstractModel):
    _name = 'report.odoocms_fee.head_wise_fee_received_summary_report'
    _description = 'Head Wise Fee Received Summary Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        date_from = fields.Date.from_string(data['form']['date_from'])
        date_to = fields.Date.from_string(data['form']['date_to'])
        fee_head_id = data['form']['fee_head_id'] and data['form']['fee_head_id'][0] or False
        is_hostel_fee = data['form']['is_hostel_fee']
        fee_head_merge_rec = self.env['odoocms.fee.head.merge'].browse(fee_head_id)
        fee_heads = fee_head_merge_rec and fee_head_merge_rec.name or " "

        res = {}
        lines = []
        total_amount = 0
        date_from1 = date_from
        total_student_count = 0

        institute_ids = self.env['odoocms.institute'].search([])
        if institute_ids:
            for institute_id in institute_ids:
                amt = 0
                student_count = 0
                waiver_amount = 0
                adjustment_amount = 0
                prev_arrears_amount = 0
                amount_residual = 0
                fee_payments = False
                if not is_hostel_fee:
                    fee_payments = self.env['account.move'].search([('payment_date', '>=', date_from),
                                                                    ('payment_date', '<=', date_to),
                                                                    ('invoice_payment_state', 'in', ['in_payment', 'paid']),
                                                                    ('institute_id', '=', institute_id.id),
                                                                    ('is_scholarship_fee', '!=', True),
                                                                    ('is_hostel_fee', '!=', True)])
                    if fee_payments:
                        if fee_head_id:
                            semester_fee = self.env['odoocms.fee.head'].search([('name', '=', 'Semester Fee')])
                            # waiver_amount calculation
                            if not semester_fee:
                                semester_fee = self.env['odoocms.fee.head'].search([('id', '=', 47)])
                            if semester_fee.id in fee_head_merge_rec.fee_heads.ids:
                                if len(fee_payments)==1:
                                    self.env.cr.execute("select sum(waiver_amount) as waiver_amount from account_move where id = %s" % fee_payments.id)
                                if len(fee_payments) > 1:
                                    self.env.cr.execute("select sum(waiver_amount) as waiver_amount from account_move where id in %s" % (tuple(fee_payments.ids),))
                                result2 = self.env.cr.dictfetchall()
                                if result2[0]['waiver_amount'] is not None:
                                    waiver_amount = result2[0]['waiver_amount']

                                # Due Amount Calculation
                                residual_moves = fee_payments.filtered(lambda rm: rm.amount_residual > 0)
                                if residual_moves:
                                    for residual_move in residual_moves:
                                        amount_residual += residual_move.amount_residual

                                # Adjustment Calculations
                                if len(fee_payments)==1:
                                    self.env.cr.execute("select sum(price_subtotal) as adjustment_amount from account_move_line where name='Adjustment' and move_id = %s" % fee_payments.id)
                                if len(fee_payments) > 1:
                                    self.env.cr.execute("select sum(price_subtotal) as adjustment_amount from account_move_line where name='Adjustment' and move_id in %s" % (tuple(fee_payments.ids),))
                                result3 = self.env.cr.dictfetchall()
                                if result3[0]['adjustment_amount'] is not None:
                                    adjustment_amount = result3[0]['adjustment_amount']

                                # Previous Arrears Calculations
                                if len(fee_payments)==1:
                                    self.env.cr.execute("select sum(price_subtotal) as prev_arrears_amount from account_move_line where name in ('Previous Arrears ','Previous Arrears',' Previous Arrears') and move_id = %s" % fee_payments.id)
                                if len(fee_payments) > 1:
                                    self.env.cr.execute("select sum(price_subtotal) as prev_arrears_amount from account_move_line where name in ('Previous Arrears ','Previous Arrears',' Previous Arrears') and move_id in %s" % (tuple(fee_payments.ids),))
                                result4 = self.env.cr.dictfetchall()
                                if result4[0]['prev_arrears_amount'] is not None:
                                    prev_arrears_amount = result4[0]['prev_arrears_amount']

                if is_hostel_fee:
                    fee_payments = self.env['account.move'].search([('payment_date', '>=', date_from),
                                                                    ('payment_date', '<=', date_to),
                                                                    ('invoice_payment_state', 'in', ['in_payment', 'paid']),
                                                                    ('institute_id', '=', institute_id.id),
                                                                    ('is_scholarship_fee', '!=', True),
                                                                    ('is_hostel_fee', '=', True)])
                    # Due Amount Calculation
                    if fee_payments:
                        hostel_fee_head = self.env['odoocms.fee.head'].search([('name', '=', 'Hostel Fee')])
                        if hostel_fee_head and hostel_fee_head.id in fee_head_merge_rec.fee_heads.ids:
                            residual_moves = fee_payments.filtered(lambda rm: rm.amount_residual > 0)
                            if residual_moves:
                                for residual_move in residual_moves:
                                    amount_residual += residual_move.amount_residual

                            # Adjustment Calculations
                            if len(fee_payments)==1:
                                self.env.cr.execute("select sum(price_subtotal) as adjustment_amount from account_move_line where name='Adjustment' and move_id = %s" % fee_payments.id)
                            if len(fee_payments) > 1:
                                self.env.cr.execute("select sum(price_subtotal) as adjustment_amount from account_move_line where name='Adjustment' and move_id in %s" % (tuple(fee_payments.ids),))
                            result3 = self.env.cr.dictfetchall()
                            if result3[0]['adjustment_amount'] is not None:
                                adjustment_amount = result3[0]['adjustment_amount']

                            # Previous Arrears Calculations
                            if len(fee_payments)==1:
                                self.env.cr.execute("select sum(price_subtotal) as prev_arrears_amount from account_move_line where name in ('Previous Arrears ','Previous Arrears',' Previous Arrears') and move_id = %s" % fee_payments.id)
                            if len(fee_payments) > 1:
                                self.env.cr.execute("select sum(price_subtotal) as prev_arrears_amount from account_move_line where name in ('Previous Arrears ','Previous Arrears',' Previous Arrears') and move_id in %s" % (tuple(fee_payments.ids),))
                            result4 = self.env.cr.dictfetchall()
                            if result4[0]['prev_arrears_amount'] is not None:
                                prev_arrears_amount = result4[0]['prev_arrears_amount']

                if fee_payments:
                    self.env.cr.execute("select distinct student_id from account_move_line where move_id in %s and fee_head_id in %s", (tuple(fee_payments.ids), tuple(fee_head_merge_rec.fee_heads.ids)))
                    rslt = self.env.cr.dictfetchall()
                    if rslt is not None:
                        student_count = len(rslt)

                    self.env.cr.execute("select sum(price_subtotal) as amount from account_move_line where move_id in %s and fee_head_id in %s", (tuple(fee_payments.ids), tuple(fee_head_merge_rec.fee_heads.ids)))
                    result = self.env.cr.dictfetchall()
                    if result[0]['amount'] is not None:
                        amt = result[0]['amount'] + prev_arrears_amount - waiver_amount - amount_residual - abs(adjustment_amount)
                        line = ({'institute': institute_id.name,
                                 'institute_code': institute_id.code,
                                 'student_count': student_count,
                                 'amount': amt})
                        lines.append(line)
                        total_amount += amt
        res = lines
        report = self.env['ir.actions.report']._get_report_from_name('odoocms_fee.head_wise_fee_received_summary_report')
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'company': request.env.user.company_id,
            'total_amount': total_amount,
            'res': res,
            'fee_heads': fee_heads,
            'date_from': date_from1.strftime("%d-%b-%Y"),
            'date_to': date_to.strftime("%d-%b-%Y"),
        }
        return docargs
