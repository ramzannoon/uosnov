import pdb
import time
from odoo import api, fields, models, _, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class StudentProvisionalCertificateReportWiz(models.TransientModel):
    _name = 'student.provisional.certificate.wiz'
    _description = 'Student Provisional Certificate Wiz'

    @api.model
    def _get_student(self):
        student_id = self.env['odoocms.student'].browse(self._context.get('active_id', False))
        if student_id:
            return student_id.id
        return True

    student_id = fields.Many2one('odoocms.student', 'Student', default=_get_student, required=True)


    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'form': data
        }

        return self.env.ref('odoocms_exam.action_report_student_provisional_certificate').with_context(landscape=False).report_action(self, data=datas,config=False)





