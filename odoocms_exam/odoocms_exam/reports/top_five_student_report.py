import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class StudentExamTopFiveStudents(models.AbstractModel):
    _name = 'report.odoocms_exam.top_five_student_report'
    _description = 'Top Five Students'

    @api.model
    def _get_report_values(self, docsid, data=None):
        company_id = self.env.user.company_id
        batch_id = data['form']['batch_id'] and data['form']['batch_id'][0] or False
        term_id = data['form']['term_id'] and data['form']['term_id'][0] or False
        number = data['form']['number'] and data['form']['number'] or False

        today = date.today()

        number_of_records = 1
        student_term = self.env['odoocms.student.term'].search([('batch_id', '=', batch_id), ('term_id', '=', term_id)])
        student_term = student_term.sorted(key=lambda r: r.sgpa,reverse=True)

        if number > number_of_records:
            number_of_records = number
        if len(student_term) >= number_of_records:
            student_term = student_term[:number_of_records]

        batch_id = self.env['odoocms.batch'].search([('id', '=', batch_id)])
        term_id = self.env['odoocms.academic.term'].search([('id', '=', term_id)])

        docargs = {
            'doc_ids': [],
            'data': data['form'],
            'company_id':company_id or False,
            'today':"Date: "+ str(today) or False,
            'student_term':student_term or False,
            'batch_id': batch_id or False,
            'term_id': term_id or False,
            'len_student_term': len(student_term) or 0
        }
        return docargs
