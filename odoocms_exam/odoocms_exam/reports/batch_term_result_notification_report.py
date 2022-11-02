import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class BatchTermResultNotification(models.AbstractModel):
    _name = 'report.odoocms_exam.batch_term_result_notification_report'
    _description = 'Batch Semester Restult Notification'

    @api.model
    def _get_report_values(self, docsid, data=None):

        company_id = self.env.user.company_id
        batch_id = data['form']['batch_id'] and data['form']['batch_id'][0] or False
        term_id = data['form']['term_id'] and data['form']['term_id'][0] or False
        notification = data['form']['notification'] and data['form']['notification'] or False

        student_terms = self.env['odoocms.student.term'].search([])
        academic_term = self.env['odoocms.academic.term'].search([('id','=',term_id)])
        batch = self.env['odoocms.batch'].search([('id', '=', batch_id)])

        today = date.today()
        if batch_id and term_id:
            student_terms = self.env['odoocms.student.term'].search([('batch_id', '=', batch_id),('term_id', '=', term_id)])

        report = self.env['ir.actions.report']._get_report_from_name('odoocms_exam.batch_term_result_notification_report')
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'student_terms': student_terms or False,
            'notification': notification or False,
            'term_name': academic_term.name or False,
            'batch':batch or False,
            'company_id':company_id or False,
            'today':today or False,
        }
        return docargs
