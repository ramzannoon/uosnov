import pdb
import time
from odoo import api, fields, models, _, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class StudentWarningLetterReportWiz(models.TransientModel):
    _name = 'student.dues.warning.letter.wiz'
    _description = 'Student Dues Warning Letter Wiz'

    @api.model
    def _get_program(self):
        student_id = self.env['odoocms.student'].browse(self._context.get('active_id', False))
        if student_id:
            return student_id.id
        return True

    student_id = fields.Many2one('odoocms.student', 'Student', default=_get_program)


    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'odoocms.batch',
            'form': data
        }

        return self.env.ref('odoocms_fee.action_report_student_dues_warning_letter').with_context(landscape=False).report_action(self, data=datas,config=False)





