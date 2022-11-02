import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging

_logger = logging.getLogger(__name__)


class StudentDMCReport(models.AbstractModel):
    _name = 'report.odoocms_exam.student_term_dmc_report'
    _description = 'Student DMC Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        # if data and data.get('form', False):

        student_id = data['form']['student_id'] and data['form']['student_id'][0] or False
        # batch_id = data['form']['batch_id'] and data['form']['batch_id'][0] or False
        student_term_id = data['form']['student_term_id'] and data['form']['student_term_id'][0] or False

        term = False
        if student_id  and student_term_id:
            student = self.env['odoocms.student'].browse(student_id)
            term = student.term_ids.filtered(lambda l: l.id == student_term_id)

        docargs = {
            'doc_ids': [],
            'data': data['form'],
            'date': str(fields.Datetime.now()),
            'student': student or False,
            'term': term or False,
        }
        return docargs