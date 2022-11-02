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


class MonthlyHeadWiseFeeChargedSummaryReport(models.AbstractModel):
    _name = 'report.odoocms_fee.monthly_head_wise_fee_charged_summary_report'
    _description = 'Monthly Head Wise Fee Charged Summary Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        fee_head_id = data['form']['fee_head_id'] and data['form']['fee_head_id'][0] or False
        is_hostel_fee = data['form']['is_hostel_fee']
        fee_head_merge_rec = self.env['odoocms.fee.head.merge'].browse(fee_head_id)
        fee_heads = fee_head_merge_rec and fee_head_merge_rec.name or " "

        res = {}
        lines = []
        total_amount = 0
        total_waiver_amount = 0
        total_student_count = 0

        institute_ids = self.env['odoocms.institute'].search([])
        if institute_ids:
            for institute_id in institute_ids:
                amt = 0
                waiver_amount = 0
                adjustment_amount = 0
                prev_arrears_amount = 0
                student_count = 0
                if not is_hostel_fee:
                    move_lines = self.env['account.move.line'].search([('fee_head_id', 'in', fee_head_merge_rec.fee_heads.ids),
                                                                       ('move_id.institute_id', '=', institute_id.id),
                                                                       ('move_id.invoice_date', '>=', date_from),
                                                                       ('move_id.invoice_date', '<=', date_to),
                                                                       ('move_id.invoice_payment_state', '!=', 'cancel'),
                                                                       ('move_id.is_hostel_fee', '!=', True),
                                                                       ('move_id.amount_total', '>', 0),
                                                                       ('move_id.reversed_entry_id', '=', False)])

                    # Fetch Previous Arrears that are not included in above lines
                    move_lines2 = self.env['account.move.line'].search([('name', 'in', ('Previous Arrears ', 'Previous Arrears', ' Previous Arrears')),
                                                                        ('move_id.institute_id', '=', institute_id.id),
                                                                        ('move_id.invoice_date', '>=', date_from),
                                                                        ('move_id.invoice_date', '<=', date_to),
                                                                        ('move_id.invoice_payment_state', '!=', 'cancel'),
                                                                        ('move_id.is_hostel_fee', '!=', True),
                                                                        ('move_id.amount_total', '>', 0),
                                                                        ('move_id.reversed_entry_id', '=', False),
                                                                        ('move_id', 'not in', move_lines.mapped('move_id').ids)])
                    if move_lines2:
                        move_lines = move_lines + move_lines2

                if is_hostel_fee:
                    move_lines = self.env['account.move.line'].search([('fee_head_id', 'in', fee_head_merge_rec.fee_heads.ids),
                                                                       ('move_id.institute_id', '=', institute_id.id),
                                                                       ('move_id.invoice_date', '>=', date_from),
                                                                       ('move_id.invoice_date', '<=', date_to),
                                                                       ('move_id.invoice_payment_state', '!=', 'cancel'),
                                                                       ('move_id.is_hostel_fee', '=', True),
                                                                       ('move_id.amount_total', '>', 0),
                                                                       ('move_id.reversed_entry_id', '=', False)])

                    # Fetch Previous Arrears that are not included in above lines
                    move_lines2 = self.env['account.move.line'].search([('name', 'in', ('Previous Arrears ', 'Previous Arrears', ' Previous Arrears')),
                                                                        ('move_id.institute_id', '=', institute_id.id),
                                                                        ('move_id.invoice_date', '>=', date_from),
                                                                        ('move_id.invoice_date', '<=', date_to),
                                                                        ('move_id.invoice_payment_state', '!=', 'cancel'),
                                                                        ('move_id.is_hostel_fee', '=', True),
                                                                        ('move_id.amount_total', '>', 0),
                                                                        ('move_id.reversed_entry_id', '=', False),
                                                                        ('move_id', 'not in', move_lines.mapped('move_id').ids)])
                    if move_lines2:
                        move_lines = move_lines + move_lines2
                fee_moves = move_lines.mapped('move_id')

                if fee_moves:
                    if len(fee_moves)==1:
                        self.env.cr.execute("select distinct student_id from account_move where id = %s" % fee_moves.id)
                    else:
                        self.env.cr.execute("select distinct student_id from account_move where id in %s" % (tuple(fee_moves.ids),))
                    rslt = self.env.cr.dictfetchall()
                    if rslt is not None:
                        student_count = len(rslt)

                    semester_fee = self.env['odoocms.fee.head'].search([('name', '=', 'Semester Fee')])
                    # waiver_amount calculation
                    if not semester_fee:
                        semester_fee = self.env['odoocms.fee.head'].search([('id', '=', 47)])
                    if semester_fee.id in fee_head_merge_rec.fee_heads.ids:
                        if len(fee_moves.ids)==1:
                            self.env.cr.execute("select sum(waiver_amount) as waiver_amount from account_move where id = %s" % (fee_moves.id))
                        else:
                            self.env.cr.execute("select sum(waiver_amount) as waiver_amount from account_move where id in %s" % (tuple(fee_moves.ids),))

                        result2 = self.env.cr.dictfetchall()
                        if result2[0]['waiver_amount'] is not None:
                            waiver_amount = result2[0]['waiver_amount']

                            # Adjustment Calculations
                            if len(fee_moves.ids)==1:
                                self.env.cr.execute("select sum(price_subtotal) as adjustment_amount from account_move_line where name='Adjustment' and move_id = %s" % (fee_moves.id))
                            else:
                                self.env.cr.execute("select sum(price_subtotal) as adjustment_amount from account_move_line where name='Adjustment' and move_id in %s" % (tuple(fee_moves.ids),))
                            result3 = self.env.cr.dictfetchall()
                            if result3[0]['adjustment_amount'] is not None:
                                adjustment_amount = result3[0]['adjustment_amount']

                            # Previous Arrears Calculations
                            if len(fee_moves.ids)==1:
                                self.env.cr.execute("select sum(price_subtotal) as prev_arrears_amount from account_move_line where name in ('Previous Arrears ','Previous Arrears',' Previous Arrears') and move_id = %s" % (fee_moves.id))
                            else:
                                self.env.cr.execute("select sum(price_subtotal) as prev_arrears_amount from account_move_line where name in ('Previous Arrears ','Previous Arrears',' Previous Arrears') and move_id in %s" % (tuple(fee_moves.ids),))
                            result4 = self.env.cr.dictfetchall()
                            if result4[0]['prev_arrears_amount'] is not None:
                                prev_arrears_amount = result4[0]['prev_arrears_amount']

                    if fee_head_id:
                        self.env.cr.execute("select sum(price_subtotal) as amount from account_move_line where move_id in %s and fee_head_id in %s", (tuple(fee_moves.ids), tuple(fee_head_merge_rec.fee_heads.ids)))
                        result = self.env.cr.dictfetchall()
                        if result[0]['amount'] is not None:
                            amt = result[0]['amount'] + prev_arrears_amount - abs(adjustment_amount) - waiver_amount
                            line = ({'institute': institute_id.name,
                                     'institute_code': institute_id.code,
                                     'student_count': student_count,
                                     'amount': amt,
                                     'waiver_amount': waiver_amount})
                            lines.append(line)
                            total_amount += amt
                            total_waiver_amount += waiver_amount
        res = lines
        report = self.env['ir.actions.report']._get_report_from_name('odoocms_fee.monthly_head_wise_fee_charged_summary_report')
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'company': request.env.user.company_id,
            'total_amount': total_amount,
            'total_waiver_amount': total_waiver_amount,
            'res': res,
            'fee_heads': fee_heads,
        }
        return docargs
