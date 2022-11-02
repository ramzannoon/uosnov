import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo import http
from datetime import date , datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class StudentFinalMeritListReport(models.AbstractModel):
    _name = 'report.odoocms_admission.student_final_merit_list_report'
    _description = 'Student Final Merit List Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        if data.get('form', False):
            register_id = data['form']['register_id'] and data['form']['register_id'][0] or False
            register = self.env['odoocms.admission.register'].browse(register_id)
        elif docsid:
            register = self.env['odoocms.admission.register'].browse(docsid[0])
            
        if register:
            app_recs = register.application_ids.filtered(lambda l: l.program_id).sorted(key=lambda r: r.merit_number)
            apps = [
                {
                'application_id': app.id,
                'entryID': app.entryID or app.application_no,
                'name': app.name + " " + (app.last_name or ""),
                'father_name': app.father_name,
                'score': app.merit_score,
                'merit_number': app.merit_number,
                'lists': [
                    {
                        'program': '-',
                        'preference': '-',
                        'program_merit_number': '-',
                        'amount': '-',
                        'locked': False,
                        'state': 'draft',
                    }
                    for list in register.merit_register_ids.sorted(key=lambda r: r.merit_list_number)
                ],
                'P': 0, 'T': 0, 'L': 0, 'A': 0, 'V': 0, 'R': 0,
                }
                for app in app_recs
            ]
            
            app_lines = dict(map(lambda x: (x, []), app_recs.ids))
            for app in apps:
                app_lines[app['application_id']] = app
            
            for mregister in register.merit_register_ids.sorted(key=lambda r: r.merit_list_number):
                for merit in mregister.merit_application_ids:
                    app_lines[merit.application_id.id]['lists'][mregister.merit_list_number - 1]['program'] = \
                        merit.prev_merit_app_id and merit.prev_merit_app_id.locked and '.' or merit.program_id.code
                    app_lines[merit.application_id.id]['lists'][mregister.merit_list_number - 1]['preference'] = \
                        merit.preference
                    app_lines[merit.application_id.id]['lists'][mregister.merit_list_number - 1]['program_merit_number'] = \
                        merit.program_merit_number
                    app_lines[merit.application_id.id]['lists'][mregister.merit_list_number - 1]['amount'] = \
                        merit.amount
                    app_lines[merit.application_id.id]['lists'][mregister.merit_list_number - 1]['locked'] = \
                        merit.locked
                    app_lines[merit.application_id.id]['lists'][mregister.merit_list_number - 1]['state'] = \
                        merit.state.capitalize()[0]
                    if merit.state in ('cancel','reject','absent'):
                        for i in range(mregister.merit_list_number,len(register.merit_register_ids)):
                            app_lines[merit.application_id.id]['lists'][i]['program'] = 'X'
                            
          
        res = {
            'lines': list(app_lines.values()),
            'register': register.name,
            'session': register.academic_session_id.name,
        }
        report = self.env['ir.actions.report']._get_report_from_name('odoocms_admission.student_final_merit_list_report')
        application_docs = self.env['odoocms.application.merit']
        docargs = {
            'register': register,
            'rep_data': res or False,
        }
        return docargs
