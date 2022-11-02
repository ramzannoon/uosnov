import pdb
import time
from odoo import api, fields, models,_, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class StudentPreferenceWizard(models.TransientModel):
    _name = 'student.preference.wizard'
    _description = 'Student Preference Wizard'
    
    register_id = fields.Many2one('odoocms.admission.register', 'Admission Register', required=True)


    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'odoocms.application',
            'form': data
        }

        return self.env.ref('odoocms_admission.action_report_student_preference').with_context(landscape=True).report_action(self, data=datas, config=False)





