import pdb
from odoo import api, fields, models, _
from odoo.osv import expression
from datetime import date


class ComponentAttendanceReport(models.AbstractModel):
    _name = 'report.odoocms_attendance.component_attendance_report'
    _description = 'Component Attendance Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        company_id = self.env.user.company_id
        class_id = data['form']['class_id'] and data['form']['class_id'][0] or False
        detail = data['form'].get('detail',False)

        today = date.today().strftime("%B %d, %Y")

        domain = [('id', '=', class_id)]
        component = self.env['odoocms.class'].search(domain)
        courses = []
        for course in component.registration_component_ids:
            present = len(course.att_line_ids.filtered(lambda l: l.state != 'draft' and
                    (l.present == True or (l.present == False and l.reason_id and l.reason_id.present == True))))
            absent = len(course.att_line_ids.filtered(lambda l: l.state != 'draft' and l.present == False and
                    (l.reason_id == False or (l.reason_id and l.reason_id.absent == True))))
            data = {
                'name': course.student_id.name,
                'code': course.student_id.code,
                'present': present,
                'absent': absent,
                'left_early': len(course.att_line_ids.filtered(lambda l: l.left_early == True)),
                'came_late': len(course.att_line_ids.filtered(lambda l: l.came_late == True)),
                'percentage': course.attendance_percentage,
            }
            courses.append(data)
            
        report = self.env['ir.actions.report']._get_report_from_name('odoocms_attendance.component_attendance_report')
        docargs = {
            'component': component or False,
            'courses': courses,
            'company_id':company_id or False,
            'detail': detail or False,
            'today':today or False,
        }
        return docargs
