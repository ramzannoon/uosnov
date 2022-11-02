import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class GradeChangeTermWiseReport(models.AbstractModel):
    _name = 'reports.odoocms_exam.grade_change_term_report'
    _description = 'Term wise Grade Changed Report'

    @api.model
    def _get_report_values(self, docsid, data=None):

        company_id = self.env.user.company_id
        term_id = data['form']['term_id'] and data['form']['term_id'][0] or False

        today = date.today()
        if term_id :
            grade_change = self.env['odoocms.course.grade.change'].search([('term_id', '=', term_id),('state', '=', 'done') ])
            grade_change_line = self.env['odoocms.course.grade.change.line'].search([('grade_id', '=', grade_change.id)])

        report = self.env['ir.actions.report']._get_report_from_name('odoocms_exam.grade_change_term_report')
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'company_id':company_id or False,
            'grade_change': grade_change or False,
            'grade_change_line': grade_change_line or False,
            'today':today or False,
        }
        return docargs
    

class GradeChangeDepartmentWiseReport(models.AbstractModel):
    _name = 'reports.odoocms_exam.grade_change_department_report'
    _description = 'Department Wise Grade Changed Report'

    @api.model
    def _get_report_values(self, docsid, data=None):

        company_id = self.env.user.company_id
        academic_session_id = data['form']['academic_session_id'] and data['form']['academic_session_id'][0] or False
        department_id = data['form']['department_id'] and data['form']['department_id'][0] or False

        today = date.today()
        if academic_session_id and department_id:
            grade_change = self.env['odoocms.course.grade.change'].search([('program_id.department_id', '=', department_id),('state', '=', 'done') ])
            # grade_change = grade_change.filtered(lambda l: l.program_id.department_id.id == department_id)
            grade_change_line = self.env['odoocms.course.grade.change.line'].search([('grade_id', '=', grade_change.id),('session_id','=',academic_session_id)])

        report = self.env['ir.actions.report']._get_report_from_name('odoocms_exam.grade_change_department_report')
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'company_id':company_id or False,
            'grade_change': grade_change or False,
            'grade_change_line':grade_change_line or False,
            'today':today or False,
        }
        return docargs
