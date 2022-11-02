import pdb
from odoo import api, fields, models, _
from odoo.osv import expression
from datetime import date


class GradeWiseCourseReport(models.AbstractModel):
    _name = 'report.odoocms_exam.grade_wise_course_report'
    _description = 'GPA wise Course Report'

    @api.model
    def _get_report_values(self, docsid, data=None):

        company_id = self.env.user.company_id
        batch_id = data['form']['batch_id'] and data['form']['batch_id'][0] or False
        term_id = data['form']['term_id'] and data['form']['term_id'][0] or False
        grade = data['form']['grade'] and data['form']['grade'] or False

        today = date.today().strftime("%B %d, %Y")

        domain = [('grade', '=', grade.upper()), ('term_id', '=', term_id)]
        if batch_id:
            domain = expression.AND([domain, [('batch_id', '=', batch_id)]])
        student_courses = self.env['odoocms.student.course'].search(domain).sorted(key=lambda r: r.student_id)

        report = self.env['ir.actions.report']._get_report_from_name('odoocms_exam.grade_wise_course_report')
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'student': student_courses[0].student_id,
            'student_courses': student_courses or False,
            'company_id':company_id or False,
            'grade': grade or False,
            'today': today or False,
        }
        return docargs
