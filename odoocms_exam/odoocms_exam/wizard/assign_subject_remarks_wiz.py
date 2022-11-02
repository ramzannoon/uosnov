import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
from datetime import date , datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time


class OdooCMSExamAssignSubjectRemarksWiz(models.TransientModel):
    _name = 'odoocms.exam.assign.subject.remarks.wiz'
    _description = 'Exam Assign Subject Remarks'


    batch_id = fields.Many2one('odoocms.batch', string='Batch', required=True)
    term_id = fields.Many2one('odoocms.academic.term','Academic Semester')
    

    def assign_remarks(self):
        self.ensure_one()
        student_subject_ids = self.env['odoocms.student.course'].search([
            ('batch_id','=',self.batch_id.id),('term_id','=',self.academic_semester_id.id)
                                                                        ])
        for rec in student_subject_ids:
            if rec.grade == 'XF':
                rec.remarks = 'Not Cleared'
            else:
                rec.remarks = 'Pass'
        return True



