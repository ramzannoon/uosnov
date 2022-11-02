import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
from odoo import http
import logging
_logger = logging.getLogger(__name__)

class StudentAdmissionInvoice(models.AbstractModel):
    _name = 'report.odoocms_admission_portal.report_admission_invoice'
    _description = 'Student Admission Invoice'

    @api.model
    def _get_report_values(self, docsid, data=None):
        application_ids = self.env['odoocms.application'].browse(docsid)

        docargs = {
            'application_ids':application_ids or False,
            'today': date.today() or False,
        }
        return docargs
