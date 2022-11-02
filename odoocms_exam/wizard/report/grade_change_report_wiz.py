import pdb
import time
from odoo import api, fields, models, _, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class GradeChangeTermWiseReportWiz(models.TransientModel):
    _name = 'grade.change.term.wiz'
    _description = 'Term Wise Grade Change Wiz'

    term_id = fields.Many2one('odoocms.academic.term', 'Academic Term', required=True)

    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'form': data
        }

        return self.env.ref('odoocms_exam.action_report_grade_change_term').with_context(landscape=True).report_action(self, data=datas,config=False)


class GradeChangeDepartmentWiseReportWiz(models.TransientModel):
    _name = 'grade.change.department.wiz'
    _description = 'Department Wise Grade Change Wiz'

    session_id = fields.Many2one('odoocms.academic.session', 'Academic Session', required=True)
    department_id = fields.Many2one('odoocms.department', 'Department', required=True)

    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'form': data
        }

        return self.env.ref('odoocms_exam.action_report_grade_change_department').with_context(landscape=True).report_action(self, data=datas,config=False)





