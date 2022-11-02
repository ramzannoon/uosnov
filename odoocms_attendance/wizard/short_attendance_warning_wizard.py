import pdb
import time
from odoo import api, fields, models,_, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class ShortAttendanceWarningWizard(models.TransientModel):
    _name = 'short.attendance.warning.wizard'
    _description = 'Short Attendance Warning'

    batch_id = fields.Many2one('odoocms.batch', 'Batch', required=True)
    student_id = fields.Many2one('odoocms.student', 'Student', required=True)


    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'form': data
        }
        return self.env.ref('odoocms_attendance.action_report_short_attendance_warning').with_context(landscape=False).report_action(self, data=datas, config=False)





