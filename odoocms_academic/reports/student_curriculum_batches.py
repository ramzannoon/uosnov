import time
from odoo import api, models, fields, _
from dateutil.parser import parse
from odoo.exceptions import UserError


class StudentCurriculumReport(models.AbstractModel):
    _name = 'report.odoocms_academic.report_student_curriculum_batches'
    _description = 'student curriculum batches Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        print(2222222222222222222222222222222222)
        docs = self.env['odoocms.student.curriculm.wiz'].browse(docids)
        print(33333333333333333333333333333333333333,docs)

        section_id = self.env['odoocms.class.primary'].search([('id', '=', docs.batch_curriculm_id.id)])
        print(444444444444444444444444444444444,section_id)

        batch_id = docs.batch_curriculm_id

        return {
            'docs': batch_id,
            'section_id': section_id,
        }
