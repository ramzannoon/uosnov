import pdb
from odoo import api, fields, models, _
from datetime import date, datetime, timedelta

import logging

_logger = logging.getLogger(__name__)


class ReportStudentData(models.AbstractModel):
    _name = 'report.odoocms.report_student_data'
    _description = 'Student Data Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        # if data and data.get('form', False):
        #     partner_id = data['form']['partner_id'][0]
        #     plan_id = data['form']['plan_id'][0]
        #     date_from = data['form']['date_from']
        #     date_to = data['form']['date_to']
        #     docs = self.env['compensation.achievement'].search([
        #         ('partner_id', '=', partner_id), ('plan_id', '=', plan_id),
        #         ('date_from', '<=', date_to), ('date_to', '>=', date_from)
        #     ])
        # elif docids:
        
        students = self.env['odoocms.student'].browse(docids)
      
        report = self.env['ir.actions.report']._get_report_from_name('odoocms.odoocms.report_student_data')
        docargs = {
            # 'doc_ids': docids,
            'students': students,
            # 'doc_model': report.model,
            # 'data': data,
        }
        return docargs
