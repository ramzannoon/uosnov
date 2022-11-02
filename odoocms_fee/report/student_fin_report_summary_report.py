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


class StudentFinancialReportSummaryReport(models.AbstractModel):
    _name = 'report.odoocms_fee.student_fin_report_summary_report'
    _description = 'Student Financial Report Summary'

    @api.model
    def _get_report_values(self, docsid, data=None):
        program_id = data['form']['program_id'] and data['form']['program_id'][0] or False

        partner = request.env.user.partner_id
        financial_summary_list = []
        program = self.env['odoocms.program'].search([('id', '=', program_id)])

        if program_id:
            invoice = self.env['account.move'].search([('program_id', '=', program_id), ('invoice_payment_state', '=', 'paid')])
            program = self.env['odoocms.program'].search([('id', '=', program_id)])
            if invoice:
                for inv in invoice:
                    domain = [('move_id', '=', inv.id)]
                    line = {
                        "student_id": inv.student_id.code,
                        "student_name": inv.student_id.first_name or "" + " " + inv.student_id.last_name or "",
                        "career": inv.program_id.career_id.name,
                        "program": inv.program_id.name,
                        "invoice_lines": [],
                    }
                    invoice_lines = self.env['account.move.line'].read_group(domain, ['price_unit'], ['fee_category_id'])
                    for l in range(0, len(invoice_lines)):
                        index = invoice_lines[l]['__domain'][1][2]
                        invoice = self.env['odoocms.fee.category'].search([('id', '=', index)])
                        invoice_line = {
                            "account": invoice.name,
                            "term": "term will be here",
                            "amount": invoice_lines[l]['price_unit'],
                        }
                        line['invoice_lines'].append(invoice_line)
                    financial_summary_list.append(line)

        report = self.env['ir.actions.report']._get_report_from_name('odoocms_fee.student_fin_report_summary_report')
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'financial_summary_list': financial_summary_list or False,
            'program': program or False,
            'partner': partner or False,
        }
        return docargs
