import pdb
import time
from odoo import api, fields, models, _, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class StudentTaxCertificateReportWiz(models.TransientModel):
    _name = 'student.tax.certificate.report.wiz'
    _description = 'Student Tax Certificate Report'

    @api.model
    def _get_student(self):
        student_id = self.env['odoocms.student'].browse(self._context.get('active_id', False))
        return student_id and student_id.id or False

    @api.model
    def _get_term(self):
        term_id = False
        student_id = self.env['odoocms.student'].browse(self._context.get('active_id', False))
        if student_id:
            term_id = student_id.term_id
        return term_id and term_id.id or False

    student_id = fields.Many2one('odoocms.student', 'Student', default=_get_student)
    term_id = fields.Many2one('odoocms.academic.term', 'Term', default=_get_term)

    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'student.tax.certificate.report.wiz',
            'form': data
        }

        return self.env.ref('odoocms_fee.action_student_tax_certificate_report').with_context(landscape=False).report_action(self, data=datas, config=False)
