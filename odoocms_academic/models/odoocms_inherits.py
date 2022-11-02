
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import pdb

import logging
_logger = logging.getLogger(__name__)


class OdooCMSCareer(models.Model):
    _inherit = "odoocms.career"

    grades = fields.Char('Grades')
    factor = fields.Char('SD Factor')


class OdooCMSCourse(models.Model):
    _inherit = 'odoocms.course'
    
    grade_method_id = fields.Many2one('odoocms.grade.method', 'Grading', ondelete='restrict', tracking=True)
    

class OdooCMSStudySchemeLine(models.Model):
    _inherit = 'odoocms.study.scheme.line'

    grade_method_id = fields.Many2one('odoocms.grade.method', 'Grading', ondelete='restrict', tracking=True)
    
    def _compute_components(self):
        super()._compute_components()
        for rec in self:
            rec.grade_method_id = rec.course_id.grade_method_id and rec.course_id.grade_method_id.id or False
            
    
class OdooCMSProgram(models.Model):
    _inherit = "odoocms.program"

    @api.model
    def _get_defalult_method(self):
        grading_method_id = self.env['odoocms.grade.method'].search([],order='sequence',limit=1)
        if grading_method_id:
            return grading_method_id.id

    grade_method_id = fields.Many2one('odoocms.grade.method', 'Grading', ondelete='restrict', tracking=True, default=_get_defalult_method)
