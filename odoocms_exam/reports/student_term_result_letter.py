import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging

_logger = logging.getLogger(__name__)


class StudentTermResultLetter(models.AbstractModel):
    _name = 'report.odoocms_exam.student_term_result_letter'
    _description = 'Student Semester Result Letter'

    @api.model
    def _get_report_values(self, docsid, data=None):
        # if data and data.get('form', False):

        student_id = data['form']['student_id'] and data['form']['student_id'][0] or False
        batch_id = data['form']['batch_id'] and data['form']['batch_id'][0] or False
        student_term_id = data['form']['student_term_id'] and data['form']['student_term_id'][0] or False

        term = False
        student = self.env['odoocms.student'].browse(0)
        if student_id and batch_id and student_term_id:
            student = self.env['odoocms.student'].browse(student_id)
            student_term = student.term_ids.filtered(lambda l: l.id == student_term_id)

        current_user = self.env.user
        docargs = {
            'doc_ids': [],
            'data': data['form'],
            'date': str(date.today()),
            'student': student or False,
            'student_term': student_term or False,
            'current_user':current_user or False,
        }
        return docargs