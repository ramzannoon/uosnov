import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class StudentExamSlip(models.AbstractModel):
    _name = 'report.odoocms_exam.student_exam_slip_report'
    _description = 'Student Exam Slip Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        if docsid:
            students = self.env['odoocms.student'].browse(docsid)
            term_id = self.env['odoocms.datesheet'].search([],order='number desc',limit=1).term_id.id
        else:
            batch_id = data['form']['batch_id'] and data['form']['batch_id'][0] or False
            term_id = data['form']['term_id'] and data['form']['term_id'][0] or False
            student_id = data['form']['student_id'] and data['form']['student_id'][0] or False
            if batch_id:
                students = self.env['odoocms.student'].search([('batch_id', '=', batch_id)])
            elif student_id:
                students = self.env['odoocms.student'].search([('id', '=', student_id)])

        company_id = self.env.user.company_id
        today = date.today()
        today = today.strftime("%B %d, %Y")

        student_list = []
        for student in students:
            personal_info, course_list = student.get_datesheet(term_id)
            student_list.append({
                'personal_info': personal_info,
                'course_info': course_list,
            })
            
        report = self.env['ir.actions.report']._get_report_from_name('odoocms_exam.student_exam_slip_report')
        docargs = {
            'doc_ids': [],
            'data': data and data.get('form',False) or False,
            'company_id': company_id or False,
            'today':"Date: " + today or False,
            'students_list': student_list or False,
        }
        return docargs
