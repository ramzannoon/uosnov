import pdb
from odoo import api, fields, models, _
from odoo.osv import expression
from datetime import date


class ClassAttendanceReport(models.AbstractModel):
    _name = 'report.odoocms_attendance.class_attendance_report'
    _description = 'Class Attendance Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        company_id = self.env.user.company_id
        primary_class_id = data['form']['primary_class_id'] and data['form']['primary_class_id'][0] or False

        today = date.today().strftime("%B %d, %Y")

        domain = [('id', '=', primary_class_id)]
        primary_class = self.env['odoocms.class.primary'].search(domain)
        courses = []
        # components = primary_class.class_ids
        for course in primary_class.registration_ids:
            data = {
                'name': course.student_id.name,
                'code': course.student_id.code,
                'component_percentage': [component.attendance_percentage for component in course.component_ids],
                'percentage': course.attendance_percentage,
            }
            courses.append(data)
            
        report = self.env['ir.actions.report']._get_report_from_name('odoocms_attendance.student_attendance_report')
        docargs = {
            'primary_class': primary_class,
            'components': [component.class_id.component for component in course.component_ids] or False,
            'courses': courses,
            'company_id':company_id or False,
            'today':today or False,
        }
        return docargs
