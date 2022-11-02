import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class ShortAttendanceReport(models.AbstractModel):
    _name = 'report.odoocms_attendance.short_attendance_report'
    _description = 'Short Attendance Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        company_id = self.env.user.company_id
        batch_id = data['form']['batch_id'] and data['form']['batch_id'][0] or False
        term_id = data['form']['term_id'] and data['form']['term_id'][0] or False
        attendance_percentage = data['form'].get('attendance_percentage',75)
        today = date.today().strftime("%B %d, %Y")

        domain = [('batch_id', '=', batch_id),('term_id','=',term_id)]
        
        list = []
        courses = self.env['odoocms.student.course'].search(domain).filtered(
            lambda l: l.attendance_percentage < attendance_percentage).sorted(key=lambda r: r.student_id.code)
        for course in courses:
            line = {
                'name': course.student_id.name,
                'code': course.student_id.code,
                'course_code': course.course_code,
                'course_name': course.course_name,
                'percentage': course.attendance_percentage,
            }
            list.append(line)

        report = self.env['ir.actions.report']._get_report_from_name('odoocms_attendance.short_attendance_report')
        docargs = {
            'courses': list or False,
            'company_id': company_id or False,
            'today': "Date: "+today or False,
        }
        return docargs
