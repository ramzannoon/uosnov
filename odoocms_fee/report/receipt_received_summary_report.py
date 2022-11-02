import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging

_logger = logging.getLogger(__name__)


class ReceiptReceivedSummaryReport(models.AbstractModel):
    _name = 'report.odoocms_fee.receipt_received_summary_report'
    _description = 'Receipt Received Summary Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        date_from = data['form']['date_from'] and data['form']['date_from'] or False
        date_to = data['form']['date_to'] and data['form']['date_to'] or False
        total_amount = 0
        date_wise_amount = []
        current_user = self.env.user

        if date_from and date_to:
            date_from = fields.Date.from_string(date_from)
            date_to = fields.Date.from_string(date_to)
            if date_from > date_to:
                raise ValidationError(_('Start Date must be Anterior to End Date'))
            else:
                start_date = date_from
                while start_date <= date_to:
                    rec_amount = 0
                    total_rec = 0
                    # total_rec = self.env['odoocms.fee.payment.register'].search_count([('date', '=', start_date), ('state', 'in', ('Draft', 'Posted'))])
                    # if total_rec > 0:
                    invoice = self.env['odoocms.fee.payment.register'].search([('date', '=', start_date), ('state', 'in', ('Draft', 'Posted'))])
                    for inv in invoice:
                        # rec_amount += inv.amount
                        total_rec += inv.total_receipts
                        rec_amount += inv.total_received_amount
                    line = {
                        "date": start_date,
                        "amount": round(rec_amount, 2),
                        "total_rec": total_rec,
                    }
                    total_amount += rec_amount
                    date_wise_amount.append(line)
                    start_date += relativedelta(days=1)

        report = self.env['ir.actions.report']._get_report_from_name('odoocms_fee.receipt_received_summary_report')
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'date_wise_amount': date_wise_amount or False,
            'total_amount': round(total_amount, 2) or False,
            'date_from': date_from or False,
            'date_to': date_to or False,
            'company': current_user.company_id or False,
        }
        return docargs
