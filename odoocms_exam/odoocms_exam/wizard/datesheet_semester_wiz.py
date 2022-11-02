import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date , datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time


class DateSheetSemesterWiz(models.TransientModel):
    _name = 'datesheet.semester.wiz'
    _description = 'DateSheet Report Wizard'

    # @api.model
    # def _get_class(self):
    #     class_id = self.env['odoocms.class'].browse(self._context.get('active_id', False))
    #     if class_id:
    #         return class_id.id
    #     return True

    semester_id = fields.Many2one('odoocms.semester', string='Semester', required=True)
    term_id = fields.Many2one('odoocms.academic.term', string='Academic Semester', required=True)
    exam_type_id = fields.Many2one('odoocms.exam.type','Exam Type',required=True)


    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'datesheet.semester.wiz',
            'form': data
        }
        return self.env.ref('odoocms_exam.action_report_datesheet_semester').with_context(landscape=True).report_action(self, data=datas,config=False)





