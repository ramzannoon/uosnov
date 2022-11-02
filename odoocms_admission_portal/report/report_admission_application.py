import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time

from odoo import http
import logging
_logger = logging.getLogger(__name__)


class AdmissionFinalReport(models.AbstractModel):
    _name = 'report.odoocms_admission_portal.report_admission'
    _description = 'Admission Final Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        company_id = self.env.user.company_id
        application = self.env['odoocms.application'].browse(docsid)
        register = self.env['odoocms.admission.register'].sudo().search([('state', '=', 'application')])
        matric_education = http.request.env['odoocms.application.academic'].sudo().search(
            [('application_id', '=', application.id), ('degree_level', 'in', ('Matric', 'O-Level'))])
        inter_education = http.request.env['odoocms.application.academic'].sudo().search(
            [('application_id', '=', application.id), ('degree_level', 'in', ('A-Level', 'Intermediate', 'DAE'))])
        program_preferences_ordered = http.request.env['odoocms.application.preference'].sudo().search([('application_id', '=', application.id)], order='preference asc')
        application_documents = http.request.env['odoocms.application.documents'].sudo().search([('application_id', '=', application.id)])
        docargs = {
            'application_ids':application or False,
            'company_id': company_id,
            'matric_education': matric_education,
            'inter_education': inter_education,
            'program_preferences_ordered': program_preferences_ordered or False,
            'application_documents': application_documents or False,
            'register': register[0],
            'today': date.today() or False,
        }
        return docargs
