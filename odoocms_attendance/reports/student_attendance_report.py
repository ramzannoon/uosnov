import pdb
from odoo import api, fields, models, _
from odoo.osv import expression
from datetime import date


class StudentAttendanceReport(models.AbstractModel):
    _name = 'report.odoocms_attendance.student_attendance_report'
    _description = 'Students Attendance Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        company_id = self.env.user.company_id
        student_id = data['form']['student_id'] and data['form']['student_id'][0] or False
        term_id = data['form']['term_id'] and data['form']['term_id'][0] or False
        detail = data['form'].get('detail',False)

        today = date.today().strftime("%B %d, %Y")

        domain = [('id', '=', student_id)]
        student = self.env['odoocms.student'].search(domain)
        term = self.env['odoocms.student.term'].search([('id','=',term_id)])
        courses = []
        for course in student.enrolled_course_ids.filtered(lambda l: l.student_term_id.id == term_id).mapped('component_ids'):
            present = len(course.att_line_ids.filtered(lambda l: l.state != 'draft' and
                    (l.present == True or (l.present == False and l.reason_id and l.reason_id.present == True))))
            absent = len(course.att_line_ids.filtered(lambda l: l.state != 'draft' and l.present == False and
                    (l.reason_id == False or (l.reason_id and l.reason_id.absent == True))))
            total = present + absent
            data = {
                'name': course.class_id.name,
                'code': course.class_id.code,
                'total': total,
                'present': present,
                'absent': absent,
                'left_early': len(course.att_line_ids.filtered(lambda l: l.left_early == True)),
                'came_late': len(course.att_line_ids.filtered(lambda l: l.came_late == True)),
                'percentage': course.attendance_percentage,
            }
            courses.append(data)
        
        report = self.env['ir.actions.report']._get_report_from_name('odoocms_attendance.student_attendance_report')
        docargs = {
            'student': student or False,
            'courses': courses,
            'company_id':company_id or False,
            'detail': detail or False,
            'today':today or False,
            'term': term.term_id,
        }
        return docargs
