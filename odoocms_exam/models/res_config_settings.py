# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval

from odoo import api, fields, models
import pdb


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    excluded_grades = fields.Char(string='Grages Excluded in CGPA', config_parameter='odoocms_exam.excluded_grades',default = 'W,I,F,RW' )
    minimum_cgpa_required = fields.Float(string='Minimum CGPA Required', config_parameter='odoocms_exam.minimum_cgpa_required', default=2.0)

    freshman_grading = fields.Boolean(string='Freshman Grading', config_parameter='odoocms_exam.freshman_grading', default=False)
    freshman_semesters = fields.Many2many('odoocms.semester', 'freshman_semesters_table', related='company_id.freshman_semesters', readonly=False,
        default=lambda self: self.env.user.company_id.freshman_semesters.ids, string="Freshman Semesters")
    freshman_passing_grades = fields.Many2many('odoocms.grade.gpa', 'freshman_passing_grades_table', related='company_id.freshman_passing_grades', readonly=False,
        default=lambda self: self.env.user.company_id.freshman_passing_grades.ids, string="Freshman Passing Grades")
    freshman_exculded_grades = fields.Many2many('odoocms.grade.gpa', 'freshman_exculded_grades_table', related='company_id.freshman_exculded_grades', readonly=False,
        default=lambda self: self.env.user.company_id.freshman_exculded_grades.ids, string="Freshman Excluded Grades")

    gradpoints_method = fields.Selection([('grade','GPA Based on Grade'),('marks','GPA Based on Marks')],string='Grade Point Method', default= 'grade', config_parameter='odoocms_exam.gradpoints_method')
    grading_method = fields.Selection([('absolute','Absolute'),('relative','Relative'),('grade_curve','Grade Curve')],string='Grading Method', default= 'relative', config_parameter='odoocms_exam.grading_method')
    assign_grade_portal = fields.Selection([('portal','Portal'),('cms-user','CMS User'),('both','Both')],string='Grade Assigning Allowed From', default= 'portal', config_parameter='odoocms_exam.assign_grade_portal ')

    @api.depends('assign_grade_portal')
    def onchagene_assign_grade_portal(self):
        class_ids = self.env['odoocms.class'].search([('state','not in',('draft','submit','disposal','approval','done'))])
        for rec in class_ids:
            rec.assign_grade_option = self.assign_grade_portal



class ResCompany(models.Model):
    _inherit = "res.company"
    
    freshman_semesters = fields.Many2many('odoocms.semester', 'freshman_semesters_table')
    freshman_passing_grades = fields.Many2many('odoocms.grade.gpa', 'freshman_passing_grades_table')
    freshman_exculded_grades = fields.Many2many('odoocms.grade.gpa', 'freshman_excluded_grades_table')
