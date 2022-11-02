import pdb
import time
from odoo import api, fields, models,_, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class ComponentAttendanceReportWizard(models.TransientModel):
    _name = 'component.attendance.report.wizard'
    _description = 'Component Attendance Report Wizard'

    batch_id = fields.Many2one('odoocms.batch', 'Batch', required=True)
    class_id = fields.Many2one('odoocms.class', 'Class', required=True)
    term_id = fields.Many2one('odoocms.academic.term', 'Term', required=True)
    
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'form': data
        }
        return self.env.ref('odoocms_attendance.action_report_component_attendance').with_context(landscape=False).report_action(self, data=datas, config=False)
