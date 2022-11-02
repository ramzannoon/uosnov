import pdb
import time
from odoo import api, fields, models,_, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class StudentFinalMeritListWizard(models.TransientModel):
    _name = 'student.final.merit.list.wizard'
    _description = 'Student Final Merit List Wizard'

    @api.model
    def _get_register(self):
        if self.env.context.get('active_model', False) == 'odoocms.admission.register' and \
                self.env.context.get('active_id',False):
            return self.env['odoocms.admission.register'].browse(self._context.get('active_id', False))
            
    register_id = fields.Many2one('odoocms.admission.register', 'Admission Register', required=True, default=_get_register)


    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'odoocms.application.merit',
            'form': data
        }

        # need to be reviewd
        return self.env.ref('odoocms_admission.action_report_student_final_merit_list').with_context(landscape=True).report_action(self, data=datas, config=False)





