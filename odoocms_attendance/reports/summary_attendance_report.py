import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class SummaryAttendanceReport(models.AbstractModel):
    _name = 'report.odoocms_attendance.summary_attendance_report'
    _description = 'Summary Attendance Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        company_id = self.env.user.company_id
        batch_id = data['form']['batch_id'] and data['form']['batch_id'][0] or False
        section_id = data['form']['section_id'] and data['form']['section_id'][0] or False
        term_id = data['form']['term_id'] and data['form']['term_id'][0] or False
        attendance_percentage = data['form'].get('attendance_percentage',75)
        today = date.today().strftime("%B %d, %Y")
        
        section = self.env['odoocms.batch.section'].browse(section_id)
        batch = self.env['odoocms.batch'].browse(batch_id)
        courses = [course.course_id.code for course in
            section.primary_class_ids.filtered(lambda l: l.term_id.id == term_id).sorted(key=lambda r: r.id)
        ]
        
        students = batch.student_ids.sorted(key=lambda r: r.code)
        items = []
        for student in students:
            data = {
                'student_code': student.code,
                'student_name': student.name,
            }
            for course in section.primary_class_ids.filtered(lambda l: l.term_id.id == term_id).sorted(key=lambda r: r.id):
                data[course.course_id.code] = {}
                data[course.course_id.code]['percentage'] = ''
                data[course.course_id.code]['highlight'] = False
            items.append(data)
       
        student_lines = {}  #dict(map(lambda x: (x, []), students.ids))
        for item in items:
            student_lines[item['student_code']] = item

        for primary_class in section.primary_class_ids.filtered(lambda l: l.term_id.id == term_id):
            for course in primary_class.registration_ids:
                print(course.student_id.code, course.course_id.code, course.attendance_percentage)
                if student_lines.get(course.student_id.code,False):
                    student_lines[course.student_id.code][course.course_id.code]['percentage'] = course.attendance_percentage
                    if course.attendance_percentage < attendance_percentage:
                        student_lines[course.student_id.code][course.course_id.code]['highlight'] = True
        
        report = self.env['ir.actions.report']._get_report_from_name('odoocms_attendance.summary_attendance_report')
        docargs = {
            'courses': courses or False,
            'company_id': company_id or False,
            'today': "Date: "+today or False,
            'lines': [x[1] for x in student_lines.items()],
            'attendance_percentage': attendance_percentage,
        }
        return docargs
