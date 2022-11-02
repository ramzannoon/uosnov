import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class StudentProvisionalResultCertificate(models.AbstractModel):
    _name = 'report.odoocms_exam.student_provisional_result_report'
    _description = 'Student Provisional Result'

    @api.model
    def _get_report_values(self, docsid, data=None):
        company_id = self.env.user.company_id
        student_id = data['form']['student_id'] and data['form']['student_id'][0] or False

        student = self.env['odoocms.student'].search([])
        today = date.today()
        student_terms = False
        if student_id:
            student = self.env['odoocms.student'].search([('id', '=', student_id)])
            student_terms = self.env['odoocms.student.term'].search([('student_id', '=', student_id)])

        report = self.env['ir.actions.report']._get_report_from_name('odoocms_exam.student_provisional_result_report')
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'student': student[0] or False,
            'student_terms': student_terms or False,
            'company_id':company_id or False,
            'today':today or False,
        }
        return docargs
