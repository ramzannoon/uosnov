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


class ProgramFinSummaryReport(models.AbstractModel):
    _name = 'report.odoocms_fee.program_wise_fin_summary_report'
    _description = 'Program Wise Financial Summary Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        program_id = data['form']['program_id'] and data['form']['program_id'][0] or False

        invoice = self.env['account.move'].search([('invoice_payment_state', 'in', ('open', 'unpaid'))])
        program = self.env['odoocms.program'].search([])
        total_amount = 0
        if program_id:
            program_invoices = self.env['account.move'].search([('program_id', '=', program_id), ('invoice_payment_state', 'in', ('open', 'unpaid'))])
            program = self.env['odoocms.program'].search([('id', '=', program_id)])

        for invoice in program_invoices:
            total_amount += invoice.amount_residual

        report = self.env['ir.actions.report']._get_report_from_name('odoocms_fee.program_wise_fin_summary_report')
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'invoice': program_invoices or False,
            'program': program[0] or False,
            'total_amount': total_amount or False,
            'company': request.env.user.company_id
        }
        return docargs
