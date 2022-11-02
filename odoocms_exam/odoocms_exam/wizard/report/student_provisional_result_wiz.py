import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date , datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time


class StudentProvResult(models.TransientModel):
    _name = 'student.provisional.result'
    _description = 'Student Provisional Result'

    batch_id = fields.Many2one('odoocms.batch', string='Batch', required=True)
    student_id = fields.Many2one('odoocms.student', string='Student', required=True)

    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'student.provisional.result',
            'form': data
        }
        return self.env.ref('odoocms_exam.action_report_student_provisional_result').with_context(landscape=False).report_action(self, data=datas,config=False)





