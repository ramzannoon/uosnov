from odoo import api, fields, models, _, tools
import logging

_logger = logging.getLogger(__name__)


class CenterStudentReportWiz(models.TransientModel):
    _name = 'center.student.wiz'
    _description = 'Center Student Wiz'

    center_ids = fields.Many2many('odoocms.exam.center',string='Center')

    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'form': data
        }
        return self.env.ref('odoocms_exam_setup.action_report_exam_center_student').with_context(landscape=True).report_action(self, data=datas,config=False)






