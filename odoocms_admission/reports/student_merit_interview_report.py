import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date , datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)

# app_recs = app_recs[max(0,sr_from-1):min(sr_to,len(app_recs))]


class StudentMeritInterviewReport(models.AbstractModel):
    _name = 'report.odoocms_admission.student_merit_interview_report'
    _description = 'Student Merit Interview Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        if data.get('form',False):
            merit_register_id = data['form']['merit_register_id'] and data['form']['merit_register_id'][0] or False
            merit_register = self.env['odoocms.merit.register'].browse(merit_register_id)
        elif docsid:
            merit_register = self.env['odoocms.merit.register'].browse(docsid[0])
        
        line_ids = []
        if merit_register:
            for rec in merit_register.merit_application_ids:
                line = {
                    'entryID' : rec.application_id.entryID or rec.application_id.application_no,
                    'name' : rec.application_id.name + " " + (rec.application_id.last_name or ''),
                    'father_name' : rec.application_id.father_name,
                }
                line_ids.append(line)
        res = {
            'lines': line_ids,
            'session': merit_register.register_id.academic_session_id.name,
            'register': merit_register.register_id.name,
        }
        docargs = {
            'rep_data': res or False,
        }
        return docargs
