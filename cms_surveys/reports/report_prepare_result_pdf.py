import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging

_logger = logging.getLogger(__name__)


class PrepareResultReport(models.AbstractModel):
    _name = 'report.cms_surveys.report_prepare_result_pdf'
    _description = 'Prepare Result Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        if docsid:
            result_summary = {}
            docamatrix = []
            docfree_text = []
            survey_sudo = self.env['survey.survey'].sudo().search([('state', '!=', 'draft'), ('id', 'in', docsid)])
            for survey in survey_sudo:
                question_sudo = self.env['survey.question'].sudo().search([('survey_id', '=', survey.id)])
                for question in question_sudo:
                    if question.question_type != 'free_text':
                        docamatrix.append(survey.prepare_result(question))
                    else:
                        docfree_text.append(survey.prepare_result(question))
            report = self.env['ir.actions.report']._get_report_from_name('cms_surveys.report_prepare_result_pdf')
            result_summary = {
                'doc_ids': [],
                'doc_model': report.model,
                'surveys': survey_sudo,
                'question_matrix': docamatrix,
                'question_free_text': docfree_text,
            }
            # 'questions': question,
            return result_summary
