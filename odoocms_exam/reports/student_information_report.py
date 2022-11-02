import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class StudentInformationReport(models.AbstractModel):
    _name = 'report.odoocms_exam.report_student_information'
    _description = 'Student Information Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        # batch_id = data['form']['batch_id'] and data['form']['batch_id'][0] or False
        # student = self.env['odoocms.student'].search([('batch_id', '=', batch_id)])

        today = date.today()
        st_data = []

        if docsid:
            students = self.env['odoocms.student'].browse(docsid)
        
        for student in students:
            rec = {
                'id_number': student.id_number,
                'name': student.name,
                'father_name': student.father_name,
                'blood_group': student.blood_group,
                'grade_points': student.grade_points,
                'earned_credits': student.earned_credits,
                'cgpa': student.cgpa,
            }
            st_data.append(rec)
        report = self.env['ir.actions.report']._get_report_from_name('odoocms_exam.report_student_information')
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'students': st_data or False,
            'today': today or False,
        }
        return docargs

