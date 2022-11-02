import pdb
import time
from odoo import api, fields, models,_, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class StudentMeritListWizard(models.TransientModel):
    _name = 'student.merit.list.wizard'
    _description = 'Student Merit List Wizard'

    @api.model
    def _get_register(self):
        if self.env.context.get('active_model', False) == 'odoocms.admission.register' and \
                self.env.context.get('active_ids', False):
            admission_register = self.env['odoocms.admission.register'].browse(self._context.get('active_ids'))
            if admission_register:
                return admission_register.id

    register_id = fields.Many2one('odoocms.admission.register', 'Admission Register', default=_get_register)
    merit_register_id = fields.Many2one('odoocms.merit.register', 'Merit Reister')
    
    remarks = fields.Char(string='Remarks' , default = 'Please bring your documents along with Fee')


    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'odoocms.application.merit',
            'form': data
        }

        # need to be reviewd
        return self.env.ref('odoocms_admission.action_report_student_merit_list').with_context(landscape=True).report_action(self, data=datas, config=False)





