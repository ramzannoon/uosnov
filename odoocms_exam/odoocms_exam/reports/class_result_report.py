import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class StudentClassResult(models.AbstractModel):
    _name = 'report.odoocms_exam.class_result_report'
    _description = 'Class Term Result Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        primary_class_id = data['form']['primary_class_id'] and data['form']['primary_class_id'][0] or False

        today = date.today()
        today = today.strftime("%B %d, %Y")
        primary_class = self.env['odoocms.class.primary'].search([('id','=',primary_class_id)])

        report = self.env['ir.actions.report']._get_report_from_name('odoocms_exam.class_result_report')
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'primary_class': primary_class or False,
            'today':today or False,
        }
        return docargs
