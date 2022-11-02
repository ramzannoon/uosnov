import pdb
import time
from odoo import api, fields, models,_, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class ClassAttendanceReportWizard(models.TransientModel):
    _name = 'class.attendance.report.wizard'
    _description = 'Class Attendance Report Wizard'

    batch_id = fields.Many2one('odoocms.batch', 'Batch', required=True)
    primary_class_id = fields.Many2one('odoocms.class.primary', 'Class', required=True)
    term_id = fields.Many2one('odoocms.academic.term', 'Term', required=True)
    
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'form': data
        }
        return self.env.ref('odoocms_attendance.action_report_class_attendance').with_context(landscape=False).report_action(self, data=datas, config=False)
