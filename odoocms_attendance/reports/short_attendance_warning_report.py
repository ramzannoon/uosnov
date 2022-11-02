import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class StudentShortAttendanceWarning(models.AbstractModel):
    _name = 'report.odoocms_attendance.short_attendance_warning_report'
    _description = 'Short Attendance Warning'

    @api.model
    def _get_report_values(self, docsid, data=None):

        company_id = self.env.user.company_id
        batch_id = data['form']['batch_id'] and data['form']['batch_id'][0] or False
        student_id = data['form']['student_id'] and data['form']['student_id'][0] or False

        today = date.today()
        today = today.strftime("%B %d, %Y")

        list = []
        if student_id:
            student = self.env['odoocms.student'].search([('id', '=', student_id)])
            # student = self.env['odoocms.student'].search([('id', '=', student_id), ('attendance_id', '<', required)]) this will be for student whole attendance is short
            if student:
                line = {
                    "name":student.name,
                    "code":student.code,
                    "street":student.street,
                    "city":student.city,
                    "country":student.country_id.name,
                    "father":student.father_name,
                    "career":student.career_id.name,
                    "term":student.term_id.name,
                    "semester": student.semester_id.name,
                    "program":student.program_id.name,
                    "department": student.program_id.department_id.name,
                }
                list.append(line)

        report = self.env['ir.actions.report']._get_report_from_name('odoocms_attendance.short_attendance_warning_report')
        docargs = {
            'doc_ids': [],
            'data': data['form'],
            'lists': list or False,
            'company_id':company_id or False,
            'today':"Date: "+today or False,
        }
        return docargs
