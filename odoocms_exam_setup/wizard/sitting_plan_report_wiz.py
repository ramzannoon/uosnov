from odoo import api, fields, models, _, tools
import logging

_logger = logging.getLogger(__name__)


class SittingPlanReportWiz(models.TransientModel):
    _name = 'sitting.plan.wiz'
    _description = 'Sitting Plan Wiz'

    center_id = fields.Many2one('odoocms.exam.center',string='Center')
    date = fields.Date(string='Date')

    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'form': data
        }
        return self.env.ref('odoocms_exam_setup.action_report_exam_sitting_plan').with_context(landscape=True).report_action(self, data=datas,config=False)






