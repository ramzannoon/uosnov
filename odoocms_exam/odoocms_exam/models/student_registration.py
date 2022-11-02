from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools.safe_eval import safe_eval
from odoo.osv import expression

import pdb


class OdooCMSStudentCourse(models.Model):
    _inherit = "odoocms.student.course"

    is_deficient = fields.Boolean('Is Deficient Course?',default=False)


class OdooCMSStudentTerm(models.Model):
    _inherit = 'odoocms.student.term'

    deficient_course_ids = fields.One2many('odoocms.student.course', 'student_term_id', 'Deficient Courses', domain=[('state', '=', 'done'), ('is_deficient', '=', True)])
    disposal_type_id = fields.Many2one('odoocms.exam.disposal.type', string='Disposal Type')
    rule_line_id = fields.Many2one('exam.disposal.rule.line', 'Rule Line')