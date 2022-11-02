import pdb
from odoo import api, fields, models, _


class StudentCurriculum(models.TransientModel):
    _name = 'odoocms.student.curriculm.wiz'
    _description = 'Student Curriculum Wizard'

    batch_curriculm_id = fields.Many2one('odoocms.batch', 'Student')

    def print_pdf_report(self):
        return self.env.ref('odoocms_academic.action_report_student_curriculum_batches').report_action(self)
