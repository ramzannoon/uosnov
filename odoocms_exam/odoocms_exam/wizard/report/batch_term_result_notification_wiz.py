import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date , datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time


class BatchTermResultNotification(models.TransientModel):
    _name = 'batch.term.result.notification.wiz'
    _description = 'Batch Term Result Notification'

    batch_id = fields.Many2one('odoocms.batch', string='Batch', required=True)
    term_id = fields.Many2one('odoocms.academic.term', string='Academic Term', required=True)
    notification = fields.Char(string='Notification', required=True)

    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'batch.term.result.notification.wiz',
            'form': data
        }
        return self.env.ref('odoocms_exam.action_report_batch_term_result_notification').with_context(landscape=False).report_action(self, data=datas,config=False)





