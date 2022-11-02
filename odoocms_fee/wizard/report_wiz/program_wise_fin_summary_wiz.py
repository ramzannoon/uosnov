import pdb
import time
from odoo import api, fields, models, _, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class ProgramFinancialReportWiz(models.TransientModel):
    _name = 'program.wise.fin.summary.wiz'
    _description = 'Program Financial Report'

    @api.model
    def _get_program(self):
        program_id = self.env['odoocms.program'].browse(self._context.get('active_id', False))
        if program_id:
            return program_id.id
        return True

    program_id = fields.Many2one('odoocms.program', 'Program', default=_get_program)

    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'odoocms.batch',
            'form': data
        }

        return self.env.ref('odoocms_fee.action_report_program_financial_summary').with_context(landscape=True).report_action(self, data=datas,config=False)





