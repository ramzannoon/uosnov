import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date , datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class StudentPreferenceReport(models.AbstractModel):
    _name = 'report.odoocms_admission.student_preference_report'
    _description = 'Student Preference Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        
        line_ids = []
        register_id = data['form']['register_id'] and data['form']['register_id'][0] or False
        if register_id:
            app_recs = self.env['odoocms.application'].search([('register_id','=',register_id)],order='entryID')
            for rec in app_recs:
                pref = ''
                pref_ids = self.env['odoocms.application.preference'].search([('application_id','=',rec.id)], order='preference')
                for p_id in pref_ids:
                    pref = pref + p_id.program_id.code + ", "
                line = {
                    'entryID' : rec.entryID,
                    'name' : rec.name, # + " " + (rec.last_name or ''),
                    'father_name' : rec.father_name,
                    'domicile_id' : rec.domicile_id.name or "",
                    'ssc' : rec.ssc_marks,
                    'inter' : rec.inter_marks,
                    'test' : rec.entry_score,
                    'pref' : pref,
                }

                line_ids.append(line)
        res = {
            'lines': line_ids,
        }
        report = self.env['ir.actions.report']._get_report_from_name('odoocms_admission.student_preference_report')
        application_docs = self.env['odoocms.application']
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'docs': application_docs,
            'rep_data': res or False,
        }
        return docargs
