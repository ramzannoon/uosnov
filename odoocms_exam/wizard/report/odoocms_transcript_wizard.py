import pdb
import time
from odoo import api, fields, models,_, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class OdooCMSStudentTranscriptWizard(models.TransientModel):
    _name = 'odoocms.student.transcript.wizard'
    _description = 'Student Transcript Wizard'
    
    student_id = fields.Many2one('odoocms.student', 'Student', required=True)


    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'form': data
        }

        return self.env.ref('odoocms_exam.action_report_student_transcript_docp').with_context(landscape=False).report_action(self, data=datas, config=False)





