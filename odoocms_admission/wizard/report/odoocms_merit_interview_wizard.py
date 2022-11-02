import pdb
import time
from odoo import api, fields, models,_, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class StudentMeritInterviewWizard(models.TransientModel):
    _name = 'student.merit.interview.wizard'
    _description = 'Student Merit Interview Wizard'
    
    @api.model
    def _get_register(self):
        if self.env.context.get('active_model', False) == 'odoocms.admission.register' and \
                self.env.context.get('active_ids', False):
            admission_register = self.env['odoocms.admission.register'].browse(self._context.get('active_ids'))
            if admission_register:
                return admission_register.id
    
    register_id = fields.Many2one('odoocms.admission.register', 'Admission Register', default=_get_register)
    merit_register_id = fields.Many2one('odoocms.merit.register', 'Merit Reister')
    
        

    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'odoocms.application.merit',
            'form': data
        }

        # need to be reviewd
        return self.env.ref('odoocms_admission.action_report_student_merit_interview').with_context(landscape=False).report_action(self, data=datas, config=False)





