from odoo import api, fields, models, _, tools
import logging

_logger = logging.getLogger(__name__)


class DateSheetReportWiz(models.TransientModel):
    _name = 'datesheet.wiz'
    _description = 'Date Sheet'

    batch_ids = fields.Many2many(comodel_name='odoocms.batch',string='Batch')
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'form': data
        }
        return self.env.ref('odoocms_exam_setup.action_report_exam_setup_datesheet').with_context(landscape=True).report_action(self, data=datas,config=False)






