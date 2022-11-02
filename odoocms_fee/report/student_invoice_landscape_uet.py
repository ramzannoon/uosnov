import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class StudentInvoiceLandscape(models.AbstractModel):
    _name = 'report.odoocms_fee.student_invoice_landscape'
    _description = 'Student Fee Invoice in Landscape Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        invoice_rec = self.env['account.move'].browse(docsid)

        payment_terms = self.env['odoocms.payment.terms'].search([])
        docargs = {
            'invoice_rec':invoice_rec or False,
            'payment_terms': payment_terms or False,
        }
        return docargs
