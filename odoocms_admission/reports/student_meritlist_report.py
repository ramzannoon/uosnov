import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date , datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class StudentMeritListReport(models.AbstractModel):
    _name = 'report.odoocms_admission.student_merit_list_report'
    _description = 'Student Merit List Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        if data.get('form', False):
            merit_register_id = data['form']['merit_register_id'] and data['form']['merit_register_id'][0] or False
            merit_register = self.env['odoocms.merit.register'].browse(merit_register_id)
        elif docsid:
            merit_register = self.env['odoocms.merit.register'].browse(docsid[0])
        
        line_ids = []
        if merit_register:
            for rec in merit_register.merit_application_ids.sorted(key=lambda l: l.total_aggregates, reverse=True):
                line = {
                    'entryID' : rec.application_id.entryID or rec.application_id.application_no,
                    'name' : rec.application_id.name + " " + (rec.application_id.last_name or ''),
                    'father_name' : rec.application_id.father_name,
                    'total_aggregates' : rec.application_id.total_aggregates,
                    # 'score' : rec.application_id.merit_score,
                    # 'program' : rec.program_id.name,
                    # 'campus': rec.program_id.department_id.institute_id.campus_id.code,
                    # 'date_interview' : rec.date_interview,
                    # 'amount': rec.amount,
                    # 'preference': rec.preference,
                    # 'remarks' : merit_register.remarks,
                    # 'locked': rec.prev_merit_app_id and rec.prev_merit_app_id.locked or False,
                }

                line_ids.append(line)
        res = {
            'lines': line_ids,
            'register': merit_register.register_id.name,
            'session': merit_register.register_id.academic_session_id.name,
            'merit_list': merit_register.merit_list_id.name,
        }
        report = self.env['ir.actions.report']._get_report_from_name('odoocms_admission.student_merit_list_report')
        application_docs = self.env['odoocms.application.merit']
        docargs = {
            'rep_data': res or False,
        }
        return docargs
