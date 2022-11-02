import pdb
from odoo import api, fields, models, _
from odoo.osv import expression
from datetime import date


class GPAWiseStudentReport(models.AbstractModel):
    _name = 'report.odoocms_exam.gpa_wise_student_report'
    _description = 'GPA wise Students Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        company_id = self.env.user.company_id
        program_id = data['form']['program_id'] and data['form']['program_id'][0] or False
        gpa = data['form']['gpa'] and data['form']['gpa'] or False

        today = date.today().strftime("%B %d, %Y")

        domain = [('cgpa', '>', gpa)]
        if program_id:
            domain = expression.AND([domain, [('program_id', '=', program_id)]])
        student = self.env['odoocms.student'].search(domain)

        report = self.env['ir.actions.report']._get_report_from_name('odoocms_exam.gpa_wise_student_report')
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'student': student or False,
            'company_id':company_id or False,
            'gpa': gpa or False,
            'today':today or False,
        }
        return docargs
