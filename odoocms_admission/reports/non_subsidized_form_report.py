import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date , datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)

class NonSubsidizedFormReport(models.AbstractModel):
    _name = 'report.odoocms_admission.non_subsidized_form_report'
    _description = 'Non SubSidized Form Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
         
        application_id = data['form']['application_id'] and data['form']['application_id'][0] or False
        if  application_id:
            pref = ''
            acadmics = ''
            table1_line_ids = []
            table1_res = {}
            table2_line_ids = []
            table2_res = {}

            application = self.env['odoocms.application'].search([('id','=',application_id)])
            acadmics = self.env['odoocms.application.academic'].search([('application_id','=',application.id)],order='id')
            pref_ids = self.env['odoocms.application.preference'].search([('application_id','=',application.id)], order='id')
            
            name = application.name.upper() + " " + application.last_name.upper()
            bio_data = {'name':name,'father':application.father_name,'mobile':application.mobile,'domicile_id':application.domicile_id or "",'gender': application.gender}
            application_no = list(application.application_no)

            i = 1
            for pref_id in pref_ids:
                if i <=9:
                    table1_line_ids.append({'program':pref_id.program_id.name})
                else:
                    table2_line_ids.append({'program': pref_id.program_id.name})
                i += 1

            if len(table1_line_ids) < 10:
                for j in range(len(table1_line_ids),9):
                    table1_line_ids.append({'program':'X'})

            if len(table2_line_ids) < 10:
                for j in range(len(table2_line_ids), 9):
                    table2_line_ids.append({'program': 'X'})

            table1_res = table1_line_ids
            table2_res = table2_line_ids
            
        report = self.env['ir.actions.report']._get_report_from_name('odoocms_admission.non_subsidized_form_report')
        application_docs = self.env['odoocms.application']
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'docs': application_docs,
            'acadmics' : acadmics,
            'preferences': pref_ids,
            'bio_data' : bio_data,
            'application' : application,
            'application_no' : application_no,
            'table1' : table1_res,
            'table2' : table2_res,
            'date': str(fields.Datetime.now())
        }
        return docargs
