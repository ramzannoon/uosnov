import pdb
import time
from odoo import api, fields, models, _, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class StudentExamTopFiveStudents(models.TransientModel):
    _name = 'student.exam.top.five.wiz'
    _description = 'Top Five Students Wiz'

    batch_id = fields.Many2one('odoocms.batch', 'Batch', required=True)
    term_id = fields.Many2one('odoocms.academic.term', 'Academic Term', required=True)
    number = fields.Integer('Number of Students', required=True, default=5)

    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'form': data
        }
        return self.env.ref('odoocms_exam.action_report_student_exam_top_five').with_context(landscape=False).report_action(self, data=datas,config=False)





