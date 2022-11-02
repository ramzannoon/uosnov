import pdb
import time
from odoo import api, fields, models, _, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class GPAWiseStudentReportWiz(models.TransientModel):
    _name = 'gpa.wise.student.wiz'
    _description = 'GPA Wise Students Wiz'

    career_id = fields.Many2one('odoocms.career', 'Academic Level', required=True)
    program_id = fields.Many2one('odoocms.program', 'Program')
    gpa = fields.Integer("GPA Threshold", required=True)

    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'form': data
        }
        return self.env.ref('odoocms_exam.action_report_gpa_wise_student').with_context(landscape=True).report_action(self, data=datas,config=False)





