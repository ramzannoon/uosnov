import pdb
import time
from odoo import api, fields, models, _, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class ClassResultWiz(models.TransientModel):
    _name = 'class.result.wiz'
    _description = 'Class Result Wiz'

    batch_id = fields.Many2one('odoocms.batch', 'Batch', required=True)
    term_id = fields.Many2one('odoocms.academic.term', 'Academic Term', required=True)
    primary_class_id = fields.Many2one('odoocms.class.primary', 'Primary Class', required=True)

    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'form': data
        }
        return self.env.ref('odoocms_exam.action_report_class_result').with_context(landscape=False).report_action(self, data=datas,config=False)





