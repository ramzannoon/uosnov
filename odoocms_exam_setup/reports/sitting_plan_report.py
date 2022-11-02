import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta

import logging
_logger = logging.getLogger(__name__)


class SittingPlanReport(models.AbstractModel):
    _name = 'report.odoocms_exam_setup.exam_sitting_plan_report'
    _description = 'Sitting Plan Report'


    @api.model
    def _get_report_values(self, docsid, data=None):
        company_id = self.env.user.company_id
        date = data['form']['date'] or False
        center_assigned = self.env['odoocms.exam.center.assignment'].search([('center_id','=',data['form']['center_id'][0])])
        sitting_plan = self.env['odoocms.exam.sitting'].search([('exam_center_id', '=', center_assigned.id),('date', '=', date)])
        sitting_plan_line = self.env['odoocms.exam.sitting.line'].search([('sitting_id','=',sitting_plan.id)])

        # exam_center_id = fields.Many2one('odoocms.exam.center.assignment', 'Examination Center')
        # student_id = fields.Many2one('odoocms.student', 'Student')
        # date = fields.Date('Date')
        # sitting_number = fields.Integer('Sitting Plan Number')
        # sitting_id = fields.Many2one('odoocms.exam.sitting', 'Exam Sitting')

        docargs = {
            'doc_ids': [],
            'data': data['form'],
            'company_id':company_id or False,
            'sitting_plan_line':sitting_plan_line or False,
            'sitting_plan':sitting_plan or False,
        }
        return docargs



