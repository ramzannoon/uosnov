import pdb
import time
from odoo import api, fields, models, _, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class StudentDMCWiz(models.TransientModel):
    _name = 'student.dmc.wiz'
    _description = 'Student DMC Wizard'

    @api.model
    def _get_student(self):
        student_id = self.env['odoocms.student'].browse(self._context.get('active_id', False))
        if student_id:
            return student_id.id
        return True

    @api.model
    def _get_student_batch(self):
        student_id = self.env['odoocms.student'].browse(self._context.get('active_id', False))
        if student_id and student_id.batch_id:
            return student_id.batch_id.id
        return True

    student_id = fields.Many2one('odoocms.student', 'Applicant', default=_get_student, required = True)
    # batch_id = fields.Many2one('odoocms.batch', 'Batch', default=_get_student_batch, required = True)
    student_term_id = fields.Many2one('odoocms.student.term', 'Student Term', required = True)


    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'odoocms.student',
            'form': data
        }
        return self.env.ref('odoocms_exam.action_report_student_dmc').report_action(self, data=datas, config=False)





