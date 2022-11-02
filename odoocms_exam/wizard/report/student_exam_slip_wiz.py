import pdb
import time
from odoo import api, fields, models, _, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class StudentExamSlipWiz(models.TransientModel):
    _name = 'student.exam.slip.wiz'
    _description = 'Students Exam Slip Wiz'

    batch_id = fields.Many2one('odoocms.batch', 'Batch')
    term_id = fields.Many2one('odoocms.academic.term', 'Academic Term', required=True)
    student_id = fields.Many2one('odoocms.student', 'Student')

    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'form': data
        }
        return self.env.ref('odoocms_exam.action_report_student_exam_slip').with_context(landscape=False).report_action(self, data=datas,config=False)





