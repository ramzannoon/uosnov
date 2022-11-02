import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class StudentWarningLetter(models.AbstractModel):
    _name = 'report.odoocms_fee.student_dues_warning_letter_report'
    _description = 'Student Warning Letter For Outstanding Dues Report'

    @api.model
    def _get_report_values(self, docsid, data=None):


        student_id = data['form']['student_id'] and data['form']['student_id'][0] or False
        student = self.env['odoocms.student'].search([])

        today = date.today()
        today = today.strftime("%B %d, %Y")

        total_amount = 0

        if student_id:
            student = self.env['odoocms.student'].search([('id', '=', student_id)])

        invoice = self.env['account.move'].search([('student_id', '=', student_id), ('state', '=', 'open')])
        for inv in invoice:
            total_amount+= sum(inv.residual for i in inv)

        report = self.env['ir.actions.report']._get_report_from_name('odoocms_fee.student_dues_warning_letter_report')
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'student': student[0] or False,
            'today':today or False,
            'total_amount':total_amount or False,
        }
        return docargs
