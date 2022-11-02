import pdb
import time
from odoo import api, fields, models, _, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class GradeWiseCourseReportWiz(models.TransientModel):
    _name = 'grade.wise.course.wiz'
    _description = 'Grade Wise Course Wiz'

    batch_id = fields.Many2one('odoocms.batch', 'Batch')
    term_id = fields.Many2one('odoocms.academic.term', 'Academic Term', required=True)
    grade = fields.Char("Grade", required=True)

    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'form': data
        }
        return self.env.ref('odoocms_exam.action_report_grade_wise_course').with_context(landscape=True).report_action(self, data=datas,config=False)





