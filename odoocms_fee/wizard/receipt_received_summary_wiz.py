import pdb
import time
from odoo import api, fields, models, _, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class ReceiptReceivedReportWiz(models.TransientModel):
    _name = 'receipt.received.summary.wiz'
    _description = 'Receipt Received Summary Report'

    # @api.model
    # def _get_program(self):
    #     program_id = self.env['odoocms.program'].browse(self._context.get('active_id', False))
    #     if program_id:
    #         return program_id.id
    #     return True

    date_from = fields.Date('Date From',required = True,  default=(fields.Date.today() - relativedelta(days=30)))
    date_to = fields.Date('Date To', required = True,  default=lambda self: fields.Date.today())


    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'odoocms.batch',
            'form': data
        }

        return self.env.ref('odoocms_fee.action_report_receipt_received_summary').with_context(landscape=True).report_action(self, data=datas,config=False)





