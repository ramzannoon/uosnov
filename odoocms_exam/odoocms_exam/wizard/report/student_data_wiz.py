import pdb
import time
from odoo import api, fields, models, _, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class StudentDataWiz(models.TransientModel):
    _name = 'student.data.wiz'
    _description = 'Student Data Wiz'
    
    term_id = fields.Many2one('odoocms.academic.term', 'Academic Term', required=True)
   

    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'form': data
        }
        return self.env.ref('odoocms_exam.action_student_grades').with_context(landscape=False).report_action(self, data=datas,config=False)


        



