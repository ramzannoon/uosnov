import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class AcademicDeficiencyWarningReport(models.AbstractModel):
    _name = 'report.odoocms_exam.academic_deficiency_warning_report'
    _description = 'Academic Deficiency Warning'

    @api.model
    def _get_report_values(self, docsid, data=None):
        company_id = self.env.user.company_id
        batch_id = data['form']['batch_id'] and data['form']['batch_id'][0] or False

        today = date.today()

        # freshman_semesters = self.env.user.company_id.freshman_semesters
        student = self.env['odoocms.student'].search([('batch_id', '=', batch_id), ('remarks_type', '=', 'warning')])

        report = self.env['ir.actions.report']._get_report_from_name('odoocms_exam.academic_definciency_probation_report')
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'student': student or False,
            'company_id': company_id or False,
            'today': today or False,
        }
        return docargs


class AcademicDeficiencyProbationReport(models.AbstractModel):
    _name = 'report.odoocms_exam.academic_deficiency_probation_report'
    _description = 'Academic Deficiency Probation'

    @api.model
    def _get_report_values(self, docsid, data=None):
        company_id = self.env.user.company_id
        batch_id = data['form']['batch_id'] and data['form']['batch_id'][0] or False

        today = date.today()

        # freshman_semesters = self.env.user.company_id.freshman_semesters
        student = self.env['odoocms.student'].search([('batch_id','=',batch_id),('remarks_type','=','probation')])

        report = self.env['ir.actions.report']._get_report_from_name('odoocms_exam.academic_deficiency_probation_report')
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'student': student or False,
            'company_id':company_id or False,
            'today':today or False,
        }
        return docargs


class AcademicDeficiencySuspensionReport(models.AbstractModel):
    _name = 'report.odoocms_exam.academic_deficiency_suspension_report'
    _description = 'Academic Deficiency Suspension'

    @api.model
    def _get_report_values(self, docsid, data=None):
        company_id = self.env.user.company_id
        batch_id = data['form']['batch_id'] and data['form']['batch_id'][0] or False

        today = date.today()

        # freshman_semesters = self.env.user.company_id.freshman_semesters
        student = self.env['odoocms.student'].search([('batch_id','=',batch_id),('remarks_type','=','suspension')])

        report = self.env['ir.actions.report']._get_report_from_name('odoocms_exam.academic_deficiency_suspension_report')
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'student': student or False,
            'company_id':company_id or False,
            'today':today or False,
        }
        return docargs


class AcademicDeficiencyWithdrawReport(models.AbstractModel):
    _name = 'report.odoocms_exam.academic_deficiency_withdraw_report'
    _description = 'Academic Deficiency Withdraw'

    @api.model
    def _get_report_values(self, docsid, data=None):

        company_id = self.env.user.company_id
        batch_id = data['form']['batch_id'] and data['form']['batch_id'][0] or False

        today = date.today()

        # freshman_semesters = self.env.user.company_id.freshman_semesters
        student = self.env['odoocms.student'].search([('batch_id','=',batch_id),('remarks_type','=','withdraw')])

        report = self.env['ir.actions.report']._get_report_from_name('odoocms_exam.academic_deficiency_withdraw_report')
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'student': student or False,
            'company_id':company_id or False,
            'today':today or False,
        }
        return docargs
