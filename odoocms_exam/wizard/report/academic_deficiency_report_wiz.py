import pdb
import time
from odoo import api, fields, models, _, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class AcademicDeficiencyWarningReportWiz(models.TransientModel):
    _name = 'academic.deficiency.warning.wiz'
    _description = 'Academic Deficiency Warning Wiz'

    batch_id = fields.Many2one('odoocms.batch', 'Batch', required=True)

    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'form': data
        }
        return self.env.ref('odoocms_exam.action_report_academic_deficiency_warning').with_context(landscape=False).report_action(self, data=datas,config=False)


class AcademicDeficiencyProbationReportWiz(models.TransientModel):
    _name = 'academic.deficiency.probation.wiz'
    _description = 'Academic Deficiency Probation Wiz'

    batch_id = fields.Many2one('odoocms.batch', 'Batch', required=True)

    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'form': data
        }
        return self.env.ref('odoocms_exam.action_report_academic_deficiency_probation').with_context(landscape=False).report_action(self, data=datas,config=False)


class AcademicDeficiencySuspensionReportWiz(models.TransientModel):
    _name = 'academic.deficiency.suspension.wiz'
    _description = 'Academic Deficiency Suspension Wiz'

    batch_id = fields.Many2one('odoocms.batch', 'Batch', required=True)

    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'form': data
        }
        return self.env.ref('odoocms_exam.action_report_academic_deficiency_suspension').with_context(landscape=False).report_action(self, data=datas,config=False)


class AcademicDeficiencyWithdrawReportWiz(models.TransientModel):
    _name = 'academic.deficiency.withdraw.wiz'
    _description = 'Academic Deficiency Withdraw Wiz'

    batch_id = fields.Many2one('odoocms.batch', 'Batch', required=True)

    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'form': data
        }
        return self.env.ref('odoocms_exam.action_report_academic_deficiency_withdraw').with_context(landscape=False).report_action(self, data=datas,config=False)



