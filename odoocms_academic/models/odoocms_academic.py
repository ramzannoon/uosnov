
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import pdb
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval
import numpy as np
import pandas as pd
import math
from datetime import date, datetime

import plotly.figure_factory as ff
import plotly
#import plotly.express as px
import plotly.graph_objs as go

import tempfile
import binascii
import xlrd

import logging
_logger = logging.getLogger(__name__)

def round_half_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n*multiplier + 0.5) / multiplier

import io

try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')

try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')

try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')
    
READONLY_STATES = {
    'draft': [('readonly', False)],
    'current': [('readonly', True)],
    'lock': [('readonly', True)],
    'submit': [('readonly', True)],
    'disposal': [('readonly', True)],
    'approval': [('readonly', True)],
    'done': [('readonly', True)],
}

READONLY_STATES2 = {
    'draft': [('readonly', False)],
    'current': [('readonly', False)],
    'lock': [('readonly', True)],
    'submit': [('readonly', True)],
    'disposal': [('readonly', True)],
    'approval': [('readonly', True)],
    'done': [('readonly', True)],
}


class OdooCMSAssessmentTemplate(models.Model):
    _name = 'odoocms.assessment.template'
    _description = 'Assessment Template'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence'
    
    sequence = fields.Integer('Sequence')
    name = fields.Char('Template Name', required=True)
    code = fields.Char('Template Code', required=True)
    domain = fields.Char('Domain')
    component_id = fields.Many2one('odoocms.components', ondelete='cascade')
    # component = fields.Selection([
    #     ('lab', 'Lab'),
    #     ('lecture', 'Lecture'),
    #     ('studio', 'Studio'),
    # ], string='Component',required=True)
   
    line_ids = fields.One2many('odoocms.assessment.template.line','template_id','Distribution Lines')
    total = fields.Float('Total',compute='_get_total', store=True)
    detail_ids = fields.One2many('odoocms.assessment.template.detail','template_id','Distribution Template')
    load_ids = fields.One2many('odoocms.assessment.template.load', 'template_id', 'Minimum Load')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', "Template Name already exists!"),
        ('code_uniq', 'unique(code)', "Template Code already exists!"),
    ]
    
    @api.depends('line_ids','line_ids.weightage')
    def _get_total(self):
        for rec in self:
            total = 0
            for line in rec.line_ids:
                total += line.weightage
            if total > 100:
                raise ValidationError('Weightage for %s can not be greater than 100' % (rec.name))
            rec.total = total
            

#Quiz=10, Assignments=15, Mid=25, Final=50  (Master)
class OdooCMSAssessmentTemplateLine(models.Model):
    _name = 'odoocms.assessment.template.line'
    _description = 'Assessment Type'
    _order = 'sequence'
    
    sequence = fields.Integer('Sequence')
    name = fields.Char('Assessment Name', required=True)
    code = fields.Char('Assessment Code', required=True)
    weightage = fields.Float('Weightage (%)',required=True)
    min = fields.Float('Min (%)',required=True)
    max = fields.Float('Max (%)',required=True)
    final = fields.Boolean('Final',default=False)
    
    template_id = fields.Many2one('odoocms.assessment.template','Distribution Template',ondelete='cascade')
    component_id = fields.Many2one('odoocms.components', ondelete='cascade')

    @api.constrains('min','max','weightage')
    def validate_range(self):
        for rec in self:
            if rec.min < 0:
                raise ValidationError(_('Min must be a Positive value'))
            if rec.max > 100:
                raise ValidationError(_('Max must be <= 100'))
            if rec.weightage < rec.min or rec.weightage > rec.max:
                raise ValidationError(_('Weightage must be in Min & Max range'))


class OdooCMSAssessmentTemplateLoad(models.Model):
    _name = 'odoocms.assessment.template.load'
    _description = 'Assessments Load'
    _order = 'sequence'

    template_id = fields.Many2one('odoocms.assessment.template', 'Assessment Template')
    assessment_type_id = fields.Many2one('odoocms.assessment.template.line', 'Assessment Type')
    
    weightage = fields.Integer('Weightage', required=True)
    min_assessments = fields.Integer('Min Assessments', required=True)
    min = fields.Integer('Min (Demo)', required=True)
    max = fields.Integer('Max (Demo)', required=True)
    event = fields.Selection([('mid','Mid'),('final','Final')],default='final',string='Before')
    sequence = fields.Integer('Sequence')
    
    
class OdooCMSAssessmentTemplateDetail(models.Model):
    _name = 'odoocms.assessment.template.detail'
    _description = 'Assessment Template Detail'
    _rec_name = 'assessment_type_id'
    _order = 'sequence'

    template_id = fields.Many2one('odoocms.assessment.template','Assessment Template')
    assessment_type_id = fields.Many2one('odoocms.assessment.template.line','Assessment Type')
    assessment_name = fields.Char('Assessment Name')
    assessment_code = fields.Char('Assessment Code')
    max_marks = fields.Float('Max Marks')
    weightage = fields.Float('Weightage')
    sequence = fields.Integer('Sequence')
    
    
#Quiz=10, Assignments=15, Mid=25, Final=50  (Class Level)
class OdooCMSAssessmentComponent(models.Model):
    _name = 'odoocms.assessment.component'
    _description = 'Assessment Class'
    _rec_name = 'assessment_type_id'
    _order = 'assessment_type_id'

    class_id = fields.Many2one('odoocms.class','Class')
    assessment_type_id = fields.Many2one('odoocms.assessment.template.line','Assessment Type')
    assessment_type_name = fields.Char(related='assessment_type_id.name', store=True)
    final = fields.Boolean(related='assessment_type_id.final', store=True)

    weightage = fields.Float('Weightage (%)')
    min = fields.Float('Min (%)')
    max = fields.Float('Max (%)')
    assessment_ids = fields.One2many('odoocms.assessment', 'assessment_component_id','Assessments')
    primary_class_id = fields.Many2one('odoocms.class.primary', 'Class Primary', related='class_id.primary_class_id')
    to_be = fields.Boolean(default=False)
    
    def create(self,vals):
        recs = super(OdooCMSAssessmentComponent,self).create(vals)
        # assessments = [[5]]
        for rec in recs:
            for assessment in rec.assessment_type_id.template_id.detail_ids.filtered(lambda l: l.assessment_type_id.id == rec.assessment_type_id.id):
                data = {
                    'name': assessment.assessment_name,
                    'code': assessment.assessment_code,
                    'weightage': assessment.weightage,
                    'max_marks': assessment.max_marks,
                    'class_id': rec.class_id.id,
                    'assessment_component_id': rec.id
                }
                self.env['odoocms.assessment'].create(data)
        
    @api.constrains('weightage', 'scheme_line_id')
    def validate_sum(self):
        for rec in self:
            recs = self.env['odoocms.assessment.component'].search([('class_id', '=', rec.class_id.id)])
            total = 0
            for rec in recs:
                if rec.weightage < rec.min or rec.weightage > rec.max:
                    raise ValidationError(_('Weightage for %s must be in range %s - %s') % (rec.assessment_type_name, rec.min, rec.max))
                else:
                    total += rec.weightage
  

class OdooCMSAssessment(models.Model):
    _name = 'odoocms.assessment'
    _description = 'Assessment'
    _order = 'date_assessment, assessment_component_id'

    name = fields.Char('Name', required=True, states=READONLY_STATES2)
    code = fields.Char('Code',required=True, states=READONLY_STATES2)
    assessment_component_id = fields.Many2one('odoocms.assessment.component', 'Assessment Class', states=READONLY_STATES2)

    class_id = fields.Many2one('odoocms.class', 'Class', states=READONLY_STATES2)
    primary_class_id = fields.Many2one('odoocms.class.primary', 'Class Primary', related='class_id.primary_class_id',store=True)
    term_id = fields.Many2one('odoocms.academic.term', 'Term', related='class_id.term_id', store=True)

    date_assessment = fields.Date('Assessment Date', states=READONLY_STATES2)
    max_marks = fields.Float('Max Marks', states=READONLY_STATES2)
    weightage = fields.Float('Weightage (%)')
    assessment_lines = fields.One2many('odoocms.assessment.line', 'assessment_id', 'Student Assessments', states=READONLY_STATES2)
    average = fields.Float('Average',compute='_get_average',store=True)
    can_delete = fields.Boolean(compute='_can_delete',store=False)
    state = fields.Selection(related='class_id.state',store=True)
    is_visible = fields.Boolean('Visibility',default=True)

    parent_id = fields.Many2one('odoocms.assessment', string='Parent Assessment')
    child_ids = fields.One2many('odoocms.assessment', 'parent_id', string='Sub Assessments',)
    to_be = fields.Boolean(default=False)
    
    @api.depends('max_marks','assessment_lines','assessment_lines.obtained_marks')
    def _get_average(self):
        for rec in self:
            total = 0
            if rec.parent_id:
                for child in rec.parent_id.child_ids:
                    total += child.max_marks
                rec.parent_id.max_marks = total
            
            total = 0
            for line in rec.assessment_lines:
                total += line.obtained_marks
                if rec.parent_id:
                    total2 = 0
                    for assessment in rec.parent_id.child_ids:
                        cass = assessment.assessment_lines.filtered(lambda l: l.student_id.id == line.student_id.id)
                        total2 += cass.obtained_marks
                    cass = rec.parent_id.assessment_lines.filtered(lambda l: l.student_id.id == line.student_id.id)
                    cass.obtained_marks = total2
            rec.average = round_half_up(total / (len(rec.assessment_lines) or 1),2)
            
    @api.depends('assessment_lines','average')
    def _can_delete(self):
        for rec in self:
            if rec.average > 0 or rec.child_ids:
                rec.can_delete = False
            else:
                rec.can_delete = True
            
    @api.constrains('max_marks')
    def check_max_marks(self):
        for rec in self:
            if rec.max_marks <= 0:
                raise ValidationError(_('Max Marks must be greater than Zero'))
        
    def name_get(self):
        res = []
        for record in self:
            name = (record.name or '') + ' - ' + (record.code or '')
            res.append((record.id, name))
        return res

    def generate_sheet(self):
        for reg in self.class_id.primary_class_id.registration_ids:
            data = {
                'assessment_id': self.id,
                'student_id': reg.student_id.id,
                'obtained_marks': 0,
            }
            self.env['odoocms.assessment.line'].create(data)
            
    def assessment_result(self):
        form_view = self.env.ref('odoocms_academic.odoocms_assessment_form')
        domain = [('id', 'in', self.ids)]
        return {
            'name': _('Assessment Result'),
            'domain': domain,
            'res_model': 'odoocms.assessment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'form',
            'view_type': 'form',
            'views': [
                (form_view and form_view.id or False, 'form'),
            ],
            'res_id': self.id,
        }


class OdooCMSAssessmentLine(models.Model):
    _name = 'odoocms.assessment.line'
    _description = 'Assessment Line'
    _order = 'student_id'

    assessment_id = fields.Many2one('odoocms.assessment', 'Assessment',ondelete='cascade')
    class_id = fields.Many2one('odoocms.class', 'Class', related="assessment_id.class_id", store=True)
    student_id = fields.Many2one('odoocms.student', 'Student')
    summary_id = fields.Many2one('odoocms.assessment.summary', 'Assessment Summary',compute='_get_summary_id',store=True)
    assessment_component_id = fields.Many2one('odoocms.assessment.component', 'Assessment Type', related='assessment_id.assessment_component_id', store=True)
    max_marks = fields.Float('Max Marks', related='assessment_id.max_marks', store=True)
    weightage = fields.Float('Weightage (%)',related='assessment_id.weightage',store=True)
    obtained_marks = fields.Float('Obtained Marks')
    percentage = fields.Float('Percentage', compute='_get_percentage', store=True)
    main_assessment = fields.Boolean(compute='_test_main_assessment', store=True)
    can_edit = fields.Boolean(compute='_test_main_assessment', store=True)
    to_be = fields.Boolean(default=False)

#     _sql_constraints = [
#         ('Unique Assessment', 'unique(assessment_id,student_id)', 'Record already exist'),
#     ]
    
    @api.depends('obtained_marks')
    def _get_summary_id(self):
        for rec in self:
            if rec.main_assessment:
                summary_rec = self.env['odoocms.assessment.summary'].search(
                    [('class_id', '=', rec.class_id.id), ('student_id', '=', rec.student_id.id),
                     ('assessment_component_id', '=', rec.assessment_component_id.id)])
            
                if not summary_rec:
                    summary_vals = {
                        'class_id': rec.class_id.id ,
                        'student_id': rec.student_id.id,
                        'assessment_component_id': rec.assessment_component_id.id,
                    }
                    summary_rec = self.env['odoocms.assessment.summary'].create(summary_vals)
                rec.summary_id = summary_rec.id
            else:
                rec.summary_id = False
    
    @api.depends('assessment_id','assessment_id.parent_id','weightage')
    def _test_main_assessment(self):
        for rec in self:
            if rec.assessment_id.parent_id:
                rec.main_assessment = False
                rec.can_edit = True
            else:
                rec.main_assessment = True
                if rec.assessment_id.child_ids:
                    rec.can_edit = False
                else:
                    rec.can_edit = True
        
    @api.depends('max_marks', 'obtained_marks')
    def _get_percentage(self):
        for rec in self:
            if rec.assessment_id and rec.can_edit and rec.obtained_marks > rec.max_marks:
                raise UserError('Obtained Marks cannot be greater than Assessment Max. Marks')
            rec.percentage = (rec.obtained_marks or 0) / (rec.max_marks or 1) * 100
    
    
class OdooCMSGradeMethod(models.Model):
    _name = 'odoocms.grade.method'
    _description = 'Grade Method'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence'
    
    name = fields.Char('Grading', required=True)
    code = fields.Char('Code', required=True)
    sequence = fields.Integer('Sequence')
    method = fields.Char('Method to Call', required=True)
    notes = fields.Html('Notes')
    grade_id = fields.Many2one('odoocms.grade','Grade Scheme')
    # grade_class_ids = fields.One2many('odoocms.class.grade','grade_method_id','Grade Classes')


class OdooCMSClass(models.Model):
    _inherit = 'odoocms.class'
    
    # Assessments Planned
    assessment_template_id = fields.Many2one('odoocms.assessment.template', 'Assessment Template', states=READONLY_STATES)
    assessment_component_ids = fields.One2many('odoocms.assessment.component', 'class_id', 'Assessment Types',
        compute='_compute_assessment_component_ids', store=True, readonly=False)
    activities_sum = fields.Integer('Sum of Assessments', compute='_get_planned_activities_sum',store=True)

    assessment_ids = fields.One2many('odoocms.assessment', 'class_id', 'Assessments',domain=[('parent_id','=',False)])
    assessment_ids2 = fields.One2many('odoocms.assessment', 'class_id', 'Sub Assessments',domain=[('parent_id','!=',False)])
    
    assessment_summary_ids = fields.One2many('odoocms.assessment.summary', 'class_id', 'Assessment Summary')
    have_assessment = fields.Boolean(compute='_have_assessments',store=True)

    def action_marge_class(self):
        for assessment_summary in self.assessment_summary_ids:
            assessment_summary.unlink()
        for assessment in (self.assessment_ids + self.assessment_ids2):
            assessment.assessment_lines.unlink()
            assessment.unlink()
        for assessment_component in self.assessment_component_ids:
            assessment_component.unlink()
            
        for reg in self.registration_component_ids:
            reg.class_id = self.merge_id.id
        self.state = 'merge'
        self.active = False
        
        
    @api.depends('assessment_component_ids', 'assessment_component_ids.weightage')
    def _get_planned_activities_sum(self):
        for rec in self:
            total = 0
            for assessment in rec.assessment_component_ids:
                total += assessment.weightage
            rec.activities_sum = total
    
    # Check with Sarfraz method odoocms.class.validate_sum: @constrains parameter 'assessment_component_ids.weightage' is not a field name
    @api.constrains('assessment_component_ids')
    def validate_sum(self):
        for rec in self:
            total = sum(ass.weightage for ass in rec.assessment_component_ids)
            if total > 100:
                raise ValidationError('Weightage for %s can not be greater than 100' % (rec.name,))
            elif total > 0 and total < 100:
                raise ValidationError('Weightage for %s can not be less than 100' % (rec.name,))

    @api.depends('assessment_ids.assessment_lines')
    def _have_assessments(self):
        for rec in self:
            lines = rec.assessment_ids.mapped('assessment_lines')
            rec.have_assessment = True if lines else False
    
    @api.depends('assessment_template_id')
    def _compute_assessment_component_ids(self):
        for rec in self:
            rec.assessment_ids = False
            template = rec.assessment_template_id
            components = [[5]]
            for component in template.line_ids:
                cdata = {
                    'assessment_type_id': component.id,
                    'weightage': component.weightage,
                    'min': component.min,
                    'max': component.max,
                }
                components.append((0, 0, cdata))
            rec.assessment_component_ids = components

    def convert_to_current(self):
        for rec in self:
            if rec.assessment_component_ids and rec.state == 'draft':
                rec.state = 'current'
                rec.primary_class_id.state = 'current'
                rec.primary_class_id.grade_class_id.state = 'current'

    def set_to_current(self):
        for rec in self:
            rec.state = 'current'
            rec.primary_class_id.state = 'current'
            rec.primary_class_id.grade_class_id.state = 'current'

    def get_sheet_titles(self):
        return ['Assessment Type','Assessment Name','Assessment Code','Max Marks','Weightage','Visibility']

    def get_sheet_headers(self, assessment):
        return [assessment.code, assessment.max_marks, assessment.weightage, assessment.is_visible]
    
    def obe_hook(self, assessment_vals, header_data,col_num):
        return assessment_vals
   
    def assessment_sheet_excel(self):
        workbook = xlwt.Workbook(encoding="utf-8")
        worksheet = workbook.add_sheet("Assessment Report")
    
        style_title = xlwt.easyxf("font:height 300; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour white;")
        style_table_header_top = xlwt.easyxf("font:height 400; font: name Liberation Sans, bold on,color cyan_ega; align: horiz center;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid;")
        style_table_header = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour cyan_ega;")
        style_table_header2 = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour silver_ega;alignment: wrap True;")
        style_date_col = xlwt.easyxf("font:height 180; font: name Liberation Sans,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")

        
        assessment_ids = self.assessment_ids
    
        current_user = self.env.user
        company = ""
        if current_user and current_user.company_id:
            company = current_user.company_id.name

        length = 8
        if len(assessment_ids) > 8:
            length = 1 + len(assessment_ids)
        worksheet.write_merge(0, 0, 0, length, company, style=style_table_header_top)
        worksheet.row(0).height = 256 * 3
    
        worksheet.write_merge(1, 1, 0, 8, "Faculty Member: " + (self.faculty_staff_id.name or "----"), style=style_title)
        worksheet.row(1).height = 256 * 2

        row = 2
        column = 0
        worksheet.write_merge(row, row + 1, column, column, self.name, style=style_table_header2)
        worksheet.write(row + 2, column, self.code, style=style_table_header2)
    
        i = 0
        sheet_titles = self.get_sheet_titles()
        sheet_titles.append('Date')
        for title in sheet_titles:
            worksheet.write(row + i, column + 1, title, style=style_table_header)
            i = i + 1
            
        worksheet.write(row + len(sheet_titles), column + 0, "Reg No", style=style_table_header)
        worksheet.write(row + len(sheet_titles), column + 1, "Name", style=style_table_header)

        col = 2
        col0 = col
        worksheet.col(column + 0).width = 256 * 25
        worksheet.col(column + 1).width = 256 * 30

        date_format = xlwt.XFStyle()
        date_format.num_format_str = 'dd/mm/yyyy'
        
        for assessment_component_id in self.assessment_component_ids:
            assessment_components = self.assessment_ids.filtered(lambda l: l.assessment_component_id.id == assessment_component_id.id)
            for ac in assessment_components:
                if ac.child_ids:
                    col1 = col
                    for sac in self.assessment_ids2.filtered(lambda l: l.parent_id.id == ac.id):
                        j = 1
                        sheet_headers = self.get_sheet_headers(sac)
                        for header in sheet_headers:
                            worksheet.write(row + j + 1, column + col, header, style=style_date_col)
                            j = j + 1
                        worksheet.write(row + j + 1, column + col, sac.date_assessment, date_format)
                        col += 1
                    worksheet.write_merge(row+1, row+1, column + col1, column + col - 1, ac.name, style=style_date_col)
                    
                else:
                    j = 1
                    sheet_headers = self.get_sheet_headers(ac)
                    for header in sheet_headers:
                        worksheet.write(row + j + 1, column + col, header, style=style_date_col)
                        j = j + 1
                    worksheet.write(row + j + 1, column + col, ac.date_assessment, date_format)
                    worksheet.write(row + 1, column + col, ac.name, style=style_date_col)
                    col += 1
                    
            if assessment_components:
                worksheet.write_merge(row, row, column + col0, column + col-1, assessment_component_id.assessment_type_id.name, style=style_table_header)
                col0 = col
        
        for ac in self.assessment_component_ids.filtered(lambda l: l not in assessment_ids.mapped('assessment_component_id')):
            worksheet.write(row + 0, column + col, ac.assessment_type_id.name, style=style_date_col)
            col += 1
        
        row_st = len(sheet_titles) + 1
        students = self.registration_component_ids

        # For grouping of Classes (Grage Class)
        # if self.group_class:
        # 	students = class_id.primary_class_id.grade_class_id.primary_class_ids.mapped('class_ids')\
        # 		.mapped('registration_component_ids')

        for student_component in students.sorted(key=lambda r: r.student_id.code):
            worksheet.write(row + row_st, column + 0, student_component.student_id.code, style=style_date_col)
            worksheet.write(row + row_st, column + 1, student_component.student_id.name, style=style_date_col)

            col_st = column + 2
            for assessment_component_id in self.assessment_component_ids:
                for ac in self.assessment_ids.filtered(lambda l: l.assessment_component_id.id == assessment_component_id.id):
                    if ac.child_ids:
                        for sac in self.assessment_ids2.filtered(lambda l: l.parent_id.id == ac.id):
                            assessment_line = self.env['odoocms.assessment.line'].search([
                                ('assessment_id', '=', sac.id), ('student_id', '=', student_component.student_id.id)])

                            worksheet.write(row + row_st, col_st, assessment_line.obtained_marks, style=style_date_col)
                            col_st += 1

                    else:
                        assessment_line = self.env['odoocms.assessment.line'].search([
                            ('assessment_id', '=', ac.id), ('student_id', '=', student_component.student_id.id)])

                        worksheet.write(row + row_st, col_st, assessment_line.obtained_marks, style=style_date_col)
                        col_st += 1

            row_st += 1
        

        # date_format = xlwt.XFStyle()
        # date_format.num_format_str = 'dd/mm/yyyy'
        #
        # count = 0
        # for cl in class_ids:
        # 	col_ass = 2
        # 	assessment_search = self.env['odoocms.assessment'].search([('class_id', '=', cl.id)])
        # 	for assessment in assessment_search:
        # 		if assessment.date_assessment and count == 0:
        # 			worksheet.write(row_start+6, column_start+col_ass,assessment.date_assessment, date_format)
        #
        # 		row_st = count+8
        # 		for assessment_line in assessment.assessment_lines.sorted(key=lambda r: r.student_id.id_number):
        # 			worksheet.write(row_start+row_st, column_start+col_ass, assessment_line.obtained_marks, style=style_date_col)
        # 			row_st += 1
        # 		col_ass += 1
        # 	count += len(cl.registration_ids)

        file_data = io.BytesIO()
        workbook.save(file_data)
        return file_data

    def assessment_import_excell(self,file_content):
        fp = tempfile.NamedTemporaryFile(suffix=".xls")
        #fp.write(binascii.a2b_base64(self.file))
        fp.write(file_content)
        fp.seek(0)

        workbook = xlrd.open_workbook(fp.name)

        sheet = workbook.sheet_by_index(0)

        header_data = []

        for row_index in range(sheet.nrows):
            row = []
            for col_index in range(sheet.ncols):
                valor = sheet.cell(row_index, col_index).value
                if valor == '':
                    for crange in sheet.merged_cells:
                        rlo, rhi, clo, chi = crange
                        if rlo <= row_index and row_index < rhi and clo <= col_index and col_index < chi:
                            valor = sheet.cell(rlo, clo).value
                            break
                row.append(valor)
            header_data.append(row)


        if header_data[4][1] == 'Rubrics':
            class_code = header_data[4][0]
            class_id = self.env['odoocms.class'].search([('code', '=', class_code)])

            if not class_id:  # or class_id.id != self.id:
                raise UserError('Class not Found')
            if class_id.state not in ('draft', 'current'):
                raise UserError('You can not import Assessments to this Class. (at Stage: %s)' % (class_id.state,))
            if len(class_id.assessment_component_ids) == 0:
                raise UserError("Assessment Types are not defined for %s Class" % (str(class_id.name)))
            col = 0
            row = 10
            for i in range(6, sheet.nrows):
                if header_data[i][0]:
                    break
            row = i + 1

            students = class_id.registration_component_ids.mapped('student_id').mapped('id_number')
            all_students = sheet.col_values(col, row)
            prev_header_0 = ''
            prev_header_1 = ''
            for col_num in range(2, sheet.ncols):  # From Column 2 to Last Column
                headers = sheet.col_values(col_num, 2, row -1)  # Quiz, Quiz 1, Q1, 10, 25, CLO-1, 2019-01-01
                if headers[0] != '' and headers[1] != '':
                    prev_header_0 = headers[0]
                    prev_header_1 = headers[1]
                if headers[0] == '' and headers[1] == '':
                    headers[0] = prev_header_0
                    headers[1] = prev_header_1
                # if col_num == 3:
                #     header_data[2][col_num]
                if not headers[0]:
                    continue
                marks = sheet.col_values(col_num, row)

                assessment = self.env['odoocms.assessment'].search([('name', '=', headers[0]), ('class_id', '=', class_id.id)])
                for i in range(len(students)):
                    if students[i] in all_students:
                        index = all_students.index(students[i])
                        student = self.env['odoocms.student'].search([('code', '=', students[i])])
                        student_rubric = self.env['odoocms.obe.student.rubrics'].search([('student_id', '=', student.id), ('assessment_id', '=', assessment.id)])
                        student_marks=self.env['odoocms.obe.student.rubrics.marks'].search(
                            [('student_rubrics', '=', student_rubric.id), ('question_id.q_id', '=', headers[3])])
                        marks_data = {
                            'obtained_marks': marks[index],
                        }
                        self.env['odoocms.obe.student.rubrics.marks'].search([('id','=',student_marks.id)]).sudo().write(marks_data)
                        obt_marks = 0
                        total_marks = 0
                        for qes in student_rubric.question_marks:
                            obt_marks = int(obt_marks) + int(qes.obtained_marks)
                            total_marks = float(total_marks) + float(qes.max_marks)
                        total_asst_marks = (float(obt_marks) / float(total_marks)) * float(student_rubric.assessment_id.max_marks)
                        rubic_data = {
                            'total_marks':total_asst_marks,
                        }
                        student_rubric.write(rubic_data)

                        assesment_line = self.env['odoocms.assessment.line'].search([
                            ('student_id', '=', student_rubric.student_id.id), ('assessment_id', '=', student_rubric.assessment_id.id)])
                        if assesment_line:
                            data = {
                                'obtained_marks': student_rubric.total_marks,
                            }
                            self.env['odoocms.assessment.line'].search([('id', '=', assesment_line.id)]).write(data)
                        else:
                            data = {
                                'student_id': student_rubric.student_id.id,
                                'obtained_marks': student_rubric.total_marks,
                                'assessment_id': student_rubric.assessment_id.id
                            }
                            self.env['odoocms.assessment.line'].create(data)
            return True


        else:
            class_code = header_data[4][0]
            class_id = self.env['odoocms.class'].search([('code', '=', class_code)])

            if not class_id:  # or class_id.id != self.id:
                raise UserError('Class not Found')
            if class_id.state not in ('draft', 'current'):
                raise UserError('You can not import Assessments to this Class. (at Stage: %s)' % (class_id.state,))
            if len(class_id.assessment_component_ids) == 0:
                raise UserError("Assessment Types are not defined for %s Class" % (str(class_id.name)))

            col = 0
            row = 10
            for i in range(6, sheet.nrows):
                if header_data[i][0]:
                    break
            row = i + 1

            students = class_id.registration_component_ids.mapped('student_id').mapped('id_number')
            all_students = sheet.col_values(col, row)

            for col_num in range(2, sheet.ncols):  # From Column 2 to Last Column
                headers = sheet.col_values(col_num, 4, row - 1)  # Quiz, Quiz 1, Q1, 10, 25, CLO-1, 2019-01-01
                if not headers[0]:
                    continue

                assessment_date = str(fields.Date.today())
                if sheet.cell(row - 2, col_num).ctype == 3:  # Date
                    date_value = xlrd.xldate_as_tuple(sheet.cell_value(row - 2, col_num), workbook.datemode)
                    assessment_date = date(*date_value[:3]).strftime('%Y-%m-%d')

                marks = sheet.col_values(col_num, row)

                col2 = col_num
                atype = header_data[2][col2]
                while atype == '':
                    col2 = col2-1
                    atype = header_data[2][col2]
                    
                assessment_type = self.env['odoocms.assessment.template.line'].search(
                    [('name', '=', atype), ('template_id', '=', class_id.assessment_template_id.id)])
                if not assessment_type:
                    raise UserError("%s is not valid Assessment Types." % (str(atype)))
                if assessment_type:
                    assessment_component_id = self.env['odoocms.assessment.component'].search(
                        [('class_id', '=', class_id.id), ('assessment_type_id', '=', assessment_type.id)])

                    if not assessment_component_id:
                        raise UserError(
                            "%s is not Assessment Type of Class %s" % (str(assessment_type.name), str(class_id.name)))

                    assessment_rec = assessment_component_id.assessment_ids.filtered(
                        lambda l: l.code == header_data[4][col_num])
                    family = parent_rec = False
                    if header_data[3][col_num - 1] == header_data[3][col_num] or (
                            col_num < sheet.ncols - 1 and header_data[3][col_num] == header_data[3][col_num + 1]):
                        family = True
                        parent_rec = assessment_component_id.assessment_ids.filtered(
                            lambda l: l.parent_id.id == False and l.name == header_data[3][col_num])
                        if not parent_rec:
                            parent_vals = [{
                                'name': header_data[3][col_num],
                                'code': str(header_data[4][col_num][0]) + '-' + str(header_data[4][col_num][-1]),
                                'assessment_component_id': assessment_component_id and assessment_component_id.id or False,
                                'class_id': class_id.id,
                                'date_assessment': assessment_date,
                                'max_marks': 0,
                                'weightage': header_data[6][col_num],
                                'parent_id': False,
                                'is_visible': header_data[7][col_num],
                            }]
                            parent_rec = self.env['odoocms.assessment'].create(parent_vals)
                        else:
                            parent_rec = parent_rec[0]
                            parent_rec.parent_id = False

                    if not assessment_rec:
                        assessment_vals = {
                            'name': header_data[3][col_num],
                            'code': header_data[4][col_num],
                            'assessment_component_id': assessment_component_id and assessment_component_id.id or False,
                            'class_id': class_id.id,
                            'parent_id': parent_rec and parent_rec.id or False,
                            'date_assessment': assessment_date,
                            'max_marks': header_data[5][col_num],
                            'weightage': parent_rec and 100 or header_data[6][col_num],
                            'is_visible': header_data[7][col_num],
                        }
                        if class_id.obe_hook:
                            assessment_vals = class_id.obe_hook(assessment_vals, header_data, col_num)
                        assessment_rec = self.env['odoocms.assessment'].create(assessment_vals)
                    else:
                        assessment_vals = {
                            'parent_id': parent_rec and parent_rec.id or False,
                            'date_assessment': assessment_date,
                            'max_marks': header_data[5][col_num],
                            'weightage': parent_rec and 100 or header_data[6][col_num],
                            'is_visible': header_data[7][col_num],
                        }
                        if class_id.obe_hook:
                            assessment_vals = class_id.obe_hook(assessment_vals, header_data, col_num)
                        assessment_rec.write(assessment_vals)

                    for i in range(len(students)):
                        if students[i] in all_students:
                            index = all_students.index(students[i])
                            student = self.env['odoocms.student'].search([('code', '=', students[i])])
                            if not student:
                                raise UserError("%s is not valid Student Code!" % (str(students[i])))

                            # For Summarization of Quizes, Assignments. Mid & Final
                            # summary_rec = self.env['odoocms.assessment.summary'].search(
                            #     [('class_id', '=', class_id.id), ('student_id', '=', student.id),
                            #      ('assessment_component_id', '=', assessment_component_id.id)])
                            #
                            # if not summary_rec:
                            #     summary_vals = {
                            #         'class_id': class_id.id,
                            #         'student_id': student.id,
                            #         'assessment_component_id': assessment_component_id.id,
                            #     }
                            #     summary_rec = self.env['odoocms.assessment.summary'].create(summary_vals)

                            if marks[index] == "":
                                marks[index] = 0

                            if headers[1] == "":
                                raise UserError("Max marks are not defined!")

                            if type(marks[index]) == str:
                                raise UserError("%s is not a Numerical Number" % (marks[index]))

                            if marks[index] > headers[1]:
                                raise UserError(
                                    "Obtained Marks %s can't be Greater than Max %s Marks\n Student: %s - Assessment: %s" %
                                    (str(marks[index]), str(headers[1]), student.code, assessment_rec.name))

                            assessment_line = self.env['odoocms.assessment.line'].search([
                                ('student_id', '=', student.id), ('assessment_id', '=', assessment_rec.id)
                            ])

                            if assessment_line:
                                line_data = {
                                    'obtained_marks': marks[index],
                                    # 'summary_id': (not family) and summary_rec.id or False,
                                }
                                assessment_line.write(line_data)
                            else:
                                line_data = {
                                    'student_id': student.id,
                                    'assessment_id': assessment_rec.id,
                                    'obtained_marks': marks[index],
                                    # 'summary_id': (not assessment_rec.parent_id) and summary_rec.id or False,
                                }
                                assessment_line = self.env['odoocms.assessment.line'].create(line_data)

                            assessment_line._get_percentage()

            if class_id.state == 'draft':
                class_id.state = 'current'
                class_id.primary_class_id.state = 'current'
                class_id.primary_class_id.grade_class_id.state = 'current'
            return True
    

class OdooCMSClassGrade(models.Model):
    _inherit = 'odoocms.class.grade'

    grade_method_id = fields.Many2one('odoocms.grade.method', 'Grading', ondelete='restrict', tracking=True)
    max_marks = fields.Float('Max Marks')
    # grading_method = fields.Char('Grading Method')

    grade_assigned = fields.Boolean(string='Grade Assigned?', default=False)
    assign_grade_option = fields.Selection([('portal', 'Portal'), ('cms-user', 'CMS User'), ('both', 'Both')], string='Grade Assigning Allowed From', default='portal', config_parameter='odoocms_academic.assign_grade_portal ')

    grade_calculation_date = fields.Date('Grade Calculation Date', readonly=True, tracking=True)
    grade_upload_date = fields.Date('Grade Upload Pre Date', readonly=True, tracking=True)
    grade_upload_date2 = fields.Date('Grade Upload Date', readonly=True, tracking=True)
    histo_ids = fields.One2many('odoocms.grade.histo','grade_class_id','Histogram')
    dbs_id = fields.Many2one('odoocms.dbs','DBS')
    dbs_action = fields.Selection([('approve','Approved'),('revise','Revision'),('new','New'),('approve2','Revision-Approve')],'DBS Action',default='new')
    fbs_id = fields.Many2one('odoocms.fbs', 'FBS')
    fbs_action = fields.Selection([('approve', 'Approved'), ('revise', 'Revision'), ('new', 'New')], 'FBS Action', default='new')
    plotly_chart = fields.Text(string='Plotly Chart', compute='_compute_plotly_chart',)
    plotly_error = fields.Text()
    
    def assign_grades(self):
        view = self.env.ref('odoocms_academic.odoocms_assign_grades_wiz_form')
        return {
            'name': 'Assign Grades',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'odoocms.assign.grades.wiz',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': self.env.context,
        }

    def get_hist_data(self,event='final'):
        grade_class = self.sudo()
        excluded_histogram_grades = (self.env['ir.config_parameter'].sudo().get_param('odoocms.excluded_histogram_grades') or 'I,W,XF').replace(' ','').split(',')
        grades = grade_class.career_id.grades.replace(' ','').split(',')
        factor = list(map(float, grade_class.career_id.factor.replace(' ','').split(',')))
        disabled = False if grade_class.state in ('draft','current','lock') else True
        
        res = []
        dict = {
            'SCode':[],
            'SName':[],
            'Program':[],
            'Session':[],
            'Obtained':[],
            'Grade':[],
            'colc':[],
            'dropped':[],
        }
        data = {
            'course_code': grade_class.code,
            'course_name': grade_class.name,
            'career': grade_class.career_id.name,
            'term': grade_class.term_id.name,
            'faculty': grade_class.grade_staff_id.name,
            'total': len(grade_class.registration_ids),
            'grade_wf': len(grade_class.registration_ids.filtered(lambda l: l.dropped == True)),
            'grade_i': len(grade_class.registration_ids.filtered(lambda l: l.grade == 'I')),
            'grade_xf': len(grade_class.registration_ids.filtered(lambda l: l.grade == 'XF')),
        }
        
        regs = grade_class.primary_class_ids.mapped('registration_ids')
        for reg in regs:
            if reg.grade not in excluded_histogram_grades and not reg.dropped:  #  and not reg.course_id_1
                res.append(reg.total_marks if event == 'final' else reg.r_total_marks)
            dict['SCode'].append(reg.student_id.code)
            dict['SName'].append(reg.student_id.name)
            dict['Program'].append(reg.student_id.program_id.name)
            dict['Session'].append(reg.student_id.session_id.name)
            dict['Obtained'].append(reg.total_marks)
            dict['Grade'].append(reg.grade or '-')
            dict['colc'].append('&#9608;&#9608;&#9608;')
            dict['dropped'].append(reg.dropped)
            
        return res, grades, dict, data, factor, disabled

    def save_hist_data(self, grades,event='final'):
        grade_class = self.sudo()
        grade_class.grade_method_id = self.env['odoocms.grade.method'].search([('code', '=', 'histogram')]).id
        excluded_histogram_grades = (self.env['ir.config_parameter'].sudo().get_param('odoocms.excluded_histogram_grades') or 'I,W,XF').replace(' ','').split(',')
        for grade, val in grades.items():
            odoo_filter = [("grade_class_id", "=", self.id), ('name', '=', grade),('event','=',event)]
            rec = self.env['odoocms.grade.histo'].sudo().search(odoo_filter)
            if rec:
                rec.write({'low_per': val[0], 'high_per': val[1], 'cnt':0})
            else:
                hist_data = {
                    'low_per': val[0], 'high_per': val[1],
                    'grade_class_id': self.id, 'name': grade, 'cnt': 0, 'event': event,
                }
                self.env['odoocms.grade.histo'].sudo().create(hist_data)

        for registration in grade_class.primary_class_ids.mapped("registration_ids").filtered(
                lambda l: l.grade not in excluded_histogram_grades and not l.dropped):   #  and not l.course_id_1
            if event == 'final':
                registration.normalized_marks = registration.total_marks
                marks = registration.total_marks
            else:
                registration.mid_total_marks = registration.r_total_marks
                for component in registration.component_ids:
                    component.mid_total_marks = component.r_total_marks
                marks = registration.mid_total_marks
                
            grade_rec = self.env['odoocms.grade.histo'].sudo().search([
                ('low_per', '<=', marks),
                ('high_per', '>', marks if marks < 100 else 99),
                ('event','=',event),
                ('grade_class_id', '=', grade_class.id),
            ])
            if event == 'final':
                grade_rec.cnt += 1
            
            if not grade_rec:
                grade_rec = self.env['odoocms.grade.histo'].sudo().search([
                    ('low_per', '<=', marks),
                    ('high_per', '>=', marks if marks < 100 else 99),
                    ('event', '=', event),
                    ('grade_class_id', '=', False)
                ])
            if event == 'final':
                registration.grade = grade_rec[0].name
            else:
                registration.mid_grade = grade_rec[0].name
        
        # This is for repeat course
        # for registration in grade_class.primary_class_ids.mapped("registration_ids").filtered(
        #         lambda l: l.grade not in excluded_histogram_grades and not l.dropped and l.course_id_1):
        #     if event == 'final':
        #         registration.normalized_marks = registration.total_marks
        #         marks = registration.total_marks
        #     else:
        #         registration.mid_total_marks = registration.r_total_marks
        #         for component in registration.component_ids:
        #             component.mid_total_marks = component.r_total_marks
        #         marks = registration.mid_total_marks
        #
        #     if registration.course_id_1.primary_class_id.grade_class_id.grade_method_id.code == 'histogram':
        #         grade_rec = self.env['odoocms.grade.histo'].sudo().search([
        #             ('low_per', '<=', marks),
        #             ('high_per', '>=', marks if marks < 100 else 99),
        #             ('event', '=', event),
        #             ('grade_class_id', '=', registration.course_id_1.primary_class_id.grade_class_id.id),
        #         ])
        #         if not grade_rec:
        #             grade_rec = self.env['odoocms.grade.histo'].sudo().search([
        #                 ('low_per', '<=', marks),
        #                 ('high_per', '>=', marks if marks < 100 else 99),
        #                 ('event', '=', event),
        #                 ('grade_class_id', '=', False)
        #             ])
        #         if event == 'final':
        #             registration.grade = grade_rec[0].name
        #         else:
        #             registration.mid_grade = grade_rec[0].name
        #
        #     else:
        #         grade_rec = self.env['odoocms.grade'].sudo()
        #         for grade in self.env['odoocms.grade'].sudo().search([]):
        #             domain = expression.AND([safe_eval(grade.domain), [('id', '=', registration.student_id.program_id.id)]]) if grade.domain else []
        #             program = self.env['odoocms.program'].search(domain)
        #             if program:
        #                 grade_rec = grade
        #
        #         grade_line = grade_rec.line_ids.filtered(lambda g: g.low_per <= marks <= g.high_per)
        #         if not registration.grade in ('I', 'W', 'RW') and grade_line:
        #             if event == 'final':
        #                 registration.grade = grade_line[0].name
        #             else:
        #                 registration.mid_grade = grade_line[0].name

        if event == 'final':
            grade_class.grade_assigned = True
            # grade_class.state = 'lock'
            # grade_class.primary_class_ids.state = 'lock'
            # grade_class.primary_class_ids.mapped('class_ids').state = 'lock'
        return 1

    def test_minimum_assessments(self,event='final'):
        for primary_class in self.primary_class_ids:
            for component_class in primary_class.class_ids:
                for load_line in component_class.assessment_template_id.load_ids.filtered(
                        lambda l: l.event == event and l.weightage == component_class.weightage):

                    done_assessments = len(component_class.assessment_ids.filtered(lambda l: l.assessment_component_id.assessment_type_id == load_line.assessment_type_id))
                    if done_assessments < load_line.min_assessments:
                        return "%s: Conducted %s, while required %s" % (load_line.assessment_type_id.name,done_assessments,load_line.min_assessments)
        return "Pass"
        
    def assign_histogram_grades(self, event='final'):
        self.grade_method_id = self.env['odoocms.grade.method'].search([('code', '=', 'histogram')]).id
        result = self.test_minimum_assessments(event=event)
        if result != 'Pass':
            raise UserError(result)
        
        data, grades, tdict, mydata, factors, disabled = self.get_hist_data(event=event)
        mu = np.mean(data)
        sigma = np.std(data)  #  , ddof=1

        sigmas = []
        for factor in factors:
            val = factor * sigma
            if val > mu:
                raise UserError('Histogram not Possible:- MU: %s, STD: %s' % (round_half_up(mu, 2), round_half_up(sigma, 2)))

            try:
                val2 = int(round_half_up(mu + val, 0))
            except:
                val2 = 0
            
            if val2 <= 0:
                val2 = 1
            sigmas.append(val2)

        grades_dict = {}
        sigmas2 = [0] + sigmas + [100]
        i = 0
        for grade in grades:
            grades_dict[grades[i]] = [sigmas2[i], sigmas2[i + 1]]
            i = i + 1
            
        self.save_hist_data(grades=grades_dict,event=event)
        
    def assign_normalized_grades(self, course_id=False,event='final'):
        marks_rounding = int(self.env['ir.config_parameter'].sudo().get_param('odoocms.marks_rounding') or '0')
        result = self.test_minimum_assessments(event=event)
        if result != 'Pass':
            raise UserError(result)
        # if course_id:
        #     rw_request = self.env['odoocms.student.course.waiting'].search([('student_course_id', '=', course_id)])
        #     if self.grading_method:
        #         rw_request.student_course_id.normalized_marks = rw_request.student_course_id.total_marks / rw_request.student_course_id.max_marks * 100.0
        #         grade_rec = self.env['odoocms.exam.grade'].search([
        #             ('low_per', '<='
        #             , rw_request.student_course_id.normalized_marks), ('high_per', '>=', rw_request.student_course_id.normalized_marks)])
        #         rw_request.student_course_id.grade = grade_rec.name
        #     else:
        #         rw_request.student_course_id.grade = ''
        #
        if not course_id:
            self.grade_method_id = self.env['odoocms.grade.method'].search([('code','=','normalized')]).id
            max_marks = 0
            for registration in self.primary_class_ids.mapped('registration_ids'):
                if not registration.course_id_1 and registration.total_marks > max_marks:
                    max_marks = registration.total_marks
            self.max_marks = round_half_up(max_marks,marks_rounding)

            for registration in self.primary_class_ids.mapped('registration_ids'):
                if not registration.course_id_1:
                    registration.normalized_marks = round_half_up(round(registration.total_marks / (max_marks or 1.00) * 100.0,2),marks_rounding)
                else:
                    registration.normalized_marks = round_half_up(round(registration.total_marks / (registration.course_id_1.max_marks or 1.00) * 100.0,2),marks_rounding)
    
                grade_rec = self.env['odoocms.grade']
                for grade in self.env['odoocms.grade'].search([],order='sequence'):
                    domain = expression.AND([safe_eval(grade.domain), [('id','=',registration.student_id.program_id.id)]]) if grade.domain else []
                    program = self.env['odoocms.program'].search(domain)
                    if program:
                        grade_rec = grade
                        break
                
                grade_line = grade_rec.line_ids.filtered(lambda g: g.low_per <= registration.normalized_marks <= g.high_per)
                if not registration.grade in ('I', 'W', 'RW') and grade_line:
                    if event == 'final':
                        registration.grade = grade_line[0].name
                    else:
                        registration.mid_grade = grade_line[0].name

        self.grade_assigned = True
        # self.state = 'lock'
        # self.primary_class_ids.state = 'lock'
        # self.primary_class_ids.mapped('class_ids').state = 'lock'
        
    def assign_absolute_grades(self,event='final'):
        # self.grade_method_id = self.env['odoocms.grade.method'].search([('code', '=', 'absolute')]).id
        result = self.test_minimum_assessments(event=event)
        if result != 'Pass':
            raise UserError(result)
        
        grade_rec = self.grade_method_id.grade_id
        
        for registration in self.primary_class_ids.mapped('registration_ids'):
            registration.normalized_marks = registration.total_marks

            #grade_rec = self.env['odoocms.grade']
            # for grade in self.env['odoocms.grade'].search([],order='sequence'):
            #     domain = expression.AND([safe_eval(grade.domain), [('id', '=', registration.student_id.program_id.id)]]) if grade.domain else []
            #     program = self.env['odoocms.program'].search(domain)
            #     if program:
            #         grade_rec = grade
            #         break

            grade_line = grade_rec.line_ids.filtered(lambda g: g.low_per <= registration.normalized_marks <= g.high_per)
            if not registration.grade in ('I', 'W', 'RW','XF') and grade_line:
                if event == 'final':
                    registration.grade = grade_line[0].name
                else:
                    registration.mid_grade = grade_line[0].name

        self.grade_assigned = True
        # self.state = 'lock'
        # self.primary_class_ids.state = 'lock'
        # self.primary_class_ids.mapped('class_ids').state = 'lock'
        
    def submit_result(self):
        grade_class = self.sudo()
        if grade_class.state in ('lock','current'):
            if not grade_class.primary_class_ids.mapped('registration_ids'):
                raise UserError('No Student registered for this Class')

            for registration in grade_class.primary_class_ids.mapped('registration_ids'):
                if not registration.grade:
                    raise UserError('Please Assign Grades before Submitting the Result')
        
            if grade_class.dbs_id and grade_class.dbs_id.state == 'done':
                activity = self.env.ref('odoocms_academic.mail_act_result_submit')
                grade_class.activity_schedule('odoocms_academic.mail_act_result_submit', user_id=activity._get_role_users(grade_class.program_id))
            else:
                #department_id = grade_class.study_scheme_line_id.department_id and grade_class.study_scheme_line_id.department_id.id or grade_class.department_id.id
                department_id = grade_class.department_id.id or (grade_class.study_scheme_line_id.department_id and grade_class.study_scheme_line_id.department_id.id)
                dbs_id = self.env['odoocms.dbs'].sudo().search([
                    ('department_id','=',department_id),
                    ('career_id','=',grade_class.career_id.id),
                    ('term_id','=', grade_class.term_id.id),
                    ('state','=', 'new'),
                ])
                if not dbs_id:
                    data = {
                        'department_id': department_id,
                        'career_id': grade_class.career_id.id,
                        'term_id': grade_class.term_id.id,
                        'state': 'new',
                    }
                    dbs_id = self.env['odoocms.dbs'].sudo().create(data)
                dbs_id.assign_dbs()
                grade_class.dbs_action = 'new'
                
            grade_class.state = 'submit'
            grade_class.primary_class_ids.state = 'submit'
            grade_class.primary_class_ids.mapped('class_ids').state = 'submit'
        return 1

    def _compute_plotly_chart(self):
        def create_hist_data(df, bin_range, binNOF):
            arr_hist, edges = np.histogram(df, bins=binNOF, range=bin_range)
            arr_df = pd.DataFrame({'count': arr_hist, 'left': edges[:-1], 'right': edges[1:]})
            arr_df['f_count'] = ['%d' % count for count in arr_df['count']]
            arr_df['f_interval'] = ['%d to %d ' % (left, right) for left, right in zip(arr_df['left'], arr_df['right'])]
            return arr_df
        
        for rec in self:
            if rec.state in ('draft','current') or rec.grade_method_id.code != 'histogram':
                rec.plotly_chart = False
                continue
                
            data, grades, tdict, mydata, factors, disabled = self.get_hist_data(event='final')
            rec.plotly_error = 'no'
            mu = np.mean(data)
            sigma = np.std(data)  # , ddof=1
            dataCount = len(data)
            dataMin = math.floor(min(data))
            dataMax = math.ceil(max(data))
            binNOF = dataMax - dataMin   #+ 1
            bin_range = [min(data), max(data)]

            if mu < 5:
                rec.plotly_chart = False
                rec.plotly_error = 'Histogram not Possible:- MU: %s, STD: %s' % (round_half_up(mu, 2), round_half_up(sigma, 2))
                return
            # Standard Sigmas
            sigmas = []
            for factor in factors:
                val = factor * sigma
                if val > mu:
                    rec.plotly_chart = False
                    rec.plotly_error = 'Histogram not Possible:- MU: %s, STD: %s' % (round_half_up(mu,2),round_half_up(sigma,2))
                    continue
                    
                val2 = int(round_half_up(mu + val,0))
                if val2 <= 0:
                    val2 = 1
                if val2 >= 100:
                    val2 = 99
                sigmas.append(val2)

            grades_dict = {}
            if not rec.histo_ids:
                grade_bin = [0] + sigmas + [100 if dataMax < 100 else 101]
                unique_grade_bin = list(set(grade_bin))
                if len(unique_grade_bin) != len(grade_bin):
                    rec.plotly_chart = False
                    rec.plotly_error = 'Histogram not Possible:- MU: %s, STD: %s, BIN: %s' % (round_half_up(mu, 2), round_half_up(sigma, 2),grade_bin)
                    continue
                
                i = 0
                for grade in grades:
                    grades_dict.update({grades[i]: [grade_bin[i], grade_bin[i + 1]]})
                    i = i + 1
            
            else:
                # Apply from DB
                grade_recs = rec.histo_ids.sorted(key=lambda r: r.low_per)
                grade_bin = []
                for grade_rec in grade_recs:
                    grades_dict.update({grade_rec.name: [int(grade_rec.low_per), int(grade_rec.high_per)]})
                    grade_bin.append(int(grade_rec.low_per))
                grade_bin.append(101)
                #     grades_dict[rec.name] = [int(rec.low_per), int(rec.high_per)]

            sigmas3 = []
            sigmas4 = []
            for grade, val in grades_dict.items():
                if grade != 'F':
                    sigmas3.append(int(val[0]))
                    sigmas4.append(int(val[0]))
            sigmas3.append(100)
            sigmas3.sort()
            sigmas4.sort()
            
            bins = np.linspace(dataMin, dataMax, binNOF+1)
            # hist_src = create_hist_data(data, bin_range,binNOF)
            legend_cnt = pd.cut(data, bins=grade_bin,right=False).value_counts()
            # print("Legend")
            # print(legend_cnt)
            
            pdf = dataCount * 1 / (sigma * np.sqrt(2 * np.pi)) * np.exp(-(bins - mu) ** 2 / (2 * sigma ** 2))
            
            m1 = max(dataMin - 2, 0)
            m2 = min(dataMax + 2, 101)
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=data,
                #histnorm='percent',
                name='control',  # name used in legend and hover labels
                xbins=dict(  # bins used for histogram
                    start=m1,
                    end=m2,
                    size=1
                ),
                marker_color='#EB89B5',
                opacity=0.75
            ))
            
            #fig = px.histogram(data,nbins=38,title='Grading Histogram',width=1000, height=500)  #,
            fig.update_layout(
                xaxis_title_text='Grades',  # xaxis label
                yaxis_title_text='No. of Students',  # yaxis label
                width=900, height=500,
                bargap=0.2,  # gap between bars of adjacent location coordinates
                bargroupgap=0.1  # gap between bars of the same location coordinates
            )
            #fig.add_trace(output)
            colors = ["grey", "firebrick", "navy", "purple", "blue", "cyan", "magenta", "red"]
            i = 1

            fig.add_trace(go.Scatter(x=[m1, m1], y=[0, 0], mode="lines", name='%s: %s' % (grades[0], legend_cnt[0])))  # , showlegend=False
            for g in sigmas4:
                fig.add_trace(go.Scatter(x=[g, g], y=[4, 0], mode="lines", name='%s: %s' % (grades[i], legend_cnt[i]),
                    hovertext='%s: %s' % (grades[i], legend_cnt[i]), textposition="top center"))
                fig.add_annotation(
                    x=g,
                    y=4,
                    xref="x",
                    yref="y",
                    text='%s-%s\n%s' %(g,sigmas3[i],grades[i]),
                    showarrow=True,
                    font=dict(
                        family="Courier New, monospace",
                        size=14,
                        color="#000000"
                    ),
                    align="center",
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor="#636363",
                    ax=20,
                    ay=-30,
                    bordercolor="#c7c7c7",
                    borderwidth=2,
                    borderpad=4,
                    bgcolor="#ff7f0e",
                    opacity=0.8
                )
                i = i + 1
            
            
            fig.add_trace(go.Scatter(x=[m2, m2], y=[0, 0], mode="lines", name='.', showlegend=False))
            legend = 'MU: %s<br>STD: %s<br>Count: %s' % (round_half_up(mu,2),round_half_up(sigma,2),dataCount)
            fig.add_annotation(go.layout.Annotation(
                text=legend,
                align='left',
                showarrow=False,
                xref='paper',
                yref='paper',
                x=1.1,
                y=0.2,
                bordercolor='black',
                borderwidth=1
            ))
            rec.plotly_chart = plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')
           
    def disposal_send(self):
        for rec in self:
            rec.compute_result()
            rec.state = 'disposal'
            rec.primary_class_ids.state = 'disposal'
            rec.primary_class_ids.mapped('class_ids').state = 'disposal'
            
    def department_approve(self):
        self.dbs_action = 'approve2'
        self.disposal_send()
        
    def dbs_approve(self):
        self.dbs_action = 'approve'
        self.disposal_send()
    
    def dbs_approve_reload(self):
        self.dbs_approve()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
        
    def revisit_result(self):
        self.dbs_action = 'revise'
        self.state = 'current'
        self.primary_class_ids.state = 'current'
        self.primary_class_ids.mapped('class_ids').state = 'current'
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def fbs_approve(self):
        self.fbs_action = 'approve'
        self.state = 'verify'
        self.primary_class_ids.state = 'verify'
        self.primary_class_ids.mapped('class_ids').state = 'verify'
      
    def fbs_approve_reload(self):
        self.fbs_approve()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    

class OdooCMSAssessmentSummary(models.Model):
    _name = 'odoocms.assessment.summary'
    _description = 'CMS Assessmenmport Summary'
    _rec_name = 'assessment_component_id'

    class_id = fields.Many2one('odoocms.class', string='Class')
    # scheme_line_id = fields.Many2one('odoocms.study.scheme.line','Scheme Line',related='class_id.study_scheme_line_id',store=True)
    # course_id = fields.Many2one('odoocms.subject', 'Subject', related='scheme_line_id.course_id', store=True)
    term_id = fields.Many2one('odoocms.academic.term', string='Term', related='class_id.term_id', store=True)

    student_id = fields.Many2one('odoocms.student', string='Student')
    assessment_component_id = fields.Many2one('odoocms.assessment.component','Assessment Type')
    final = fields.Boolean('Final',related='assessment_component_id.final',store=True)
    registration_component_id = fields.Many2one('odoocms.student.course.component','Student Course Component',compute='_get_student_course_component',store=True)

    percentage = fields.Float('Percentage', compute='_get_percentage', store=True)
    percentaged_marks = fields.Float('Percentaged Marks', compute='_get_percentage', store=True) #added by Mazhar. Need cron job for previous results
    assessment_lines = fields.One2many('odoocms.assessment.line','summary_id','Assessment Lines',)
    # company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get())
    to_be = fields.Boolean(default=False)
    
    @api.depends('class_id', 'student_id')
    def _get_student_course_component(self):
        for result in self:
            if result.student_id and result.class_id:
                component_id = self.env['odoocms.student.course.component'].with_context(dict(active_test=True)).search([
                    ('student_id','=',result.student_id.id),('class_id','=',result.class_id.id)])
                result.registration_component_id = component_id.id

    @api.depends('assessment_lines', 'assessment_lines.percentage','assessment_lines.weightage')
    def _get_percentage(self):
        for result in self:
            percentage = cnt = weightage = 0
            for assessment in result.assessment_lines.filtered(lambda l: l.main_assessment == True):
                # percentage += assessment.percentage
                # cnt += 1
                percentage += (assessment.percentage * (assessment.weightage / 100.0))
                weightage += assessment.weightage
                
            result.percentage = percentage / (weightage or 1) * 100
            result.percentaged_marks = result.percentage*result.assessment_component_id.weightage #added by Mazhar. Need cron job for previous results


class OdooCMSStudentCourseComponent(models.Model):
    _inherit = "odoocms.student.course.component"

    assessment_summary_ids = fields.One2many('odoocms.assessment.summary', 'registration_component_id','Assessments')
    total_marks = fields.Float('Total Marks',compute='_get_total_marks',store=True)
    r_total_marks = fields.Float('R. Total Marks', compute='_get_total_marks', store=True)
    mid_total_marks = fields.Float('Mid Total Marks')
    
    @api.depends('assessment_summary_ids', 'assessment_summary_ids.percentage')
    def _get_total_marks(self):
        for reg in self:
            total = 0
            weightage = 0
            for rec in reg.assessment_summary_ids:
                total += rec.percentage * rec.assessment_component_id.weightage
                #total += rec.percentaged_marks
                weightage += rec.assessment_component_id.weightage
            reg.total_marks = total / 100.0
            reg.r_total_marks = total / (weightage or 1.0)
            
    
class OdooCMSStudentCourse(models.Model):
    _inherit = "odoocms.student.course"

    total_marks = fields.Float('Total Marks',compute='_get_total_marks',store=True, readonly=False)
    normalized_marks = fields.Float('Normalized Marks')
    grade = fields.Char('Grade',size=5)
    grade_date = fields.Date('Grade Date')

    r_total_marks = fields.Float('R. Total Marks',compute='_get_total_marks',store=True)
    mid_total_marks = fields.Float('Mid Total Marks')
    mid_grade = fields.Char('Mid Grade', size=5)
    mid_grade_date = fields.Date('Mid Grade Date')
   
    @api.depends('component_ids', 'component_ids.total_marks')
    def _get_total_marks(self):
        marks_rounding = int(self.env['ir.config_parameter'].sudo().get_param('odoocms.marks_rounding') or '0')
        for rec in self:
            total = r_total = 0
            # if rec.student_id.id == 99104:
            #     pdb.set_trace()
            #     b = 5
            for reg in rec.component_ids:
                total += reg.total_marks * (reg.class_id.weightage)
                r_total += reg.r_total_marks * (reg.class_id.weightage)
            rec.total_marks = round_half_up(round(total / (rec.primary_class_id.credits or 1),2),marks_rounding)
            rec.r_total_marks = round_half_up(round(r_total / (rec.primary_class_id.credits or 1),2), marks_rounding)
            
    def cron_total_marks(self,n=2000):
        recs_count = self.search_count([('to_be', '=', True)])
        courses = self.search([('to_be','=',True)],limit=n)
        for course in courses: #.with_progress(msg="Term Result ({})".format(recs_count)):
            course._get_total_marks()
            course.to_be = False

            
class OdooCMSCourseComponent(models.Model):
    _inherit = 'odoocms.course.component'

    assessment_template_id = fields.Many2one('odoocms.assessment.template', 'Assessment Template')
    

class OdooCMSStudySchemeLineComponent(models.Model):
    _inherit = 'odoocms.study.scheme.line.component'

    assessment_template_id = fields.Many2one('odoocms.assessment.template', 'Assessment Template')
    
    
class OdooCMSStudySchemeLine(models.Model):
    _inherit = 'odoocms.study.scheme.line'

    department_id = fields.Many2one('odoocms.department','Department')

    def component_hook(self,component_data):
        course_component = self.env['odoocms.course.component'].search([
            ('course_id', '=', self.course_id.id), ('component_id', '=', component_data['component_id'])
        ])
        if course_component:
            component_data['assessment_template_id'] = course_component.assessment_template_id and course_component.assessment_template_id.id or False
        return component_data
    

class OdooCMSBatch(models.Model):
    _inherit = "odoocms.batch"

    def component_hook(self,class_data,scheme_line):
        sl_component = self.env['odoocms.study.scheme.line.component'].search([
            ('scheme_line_id','=',scheme_line.id),('component_id','=',class_data['component_id'])
        ])
        if sl_component:
            class_data['assessment_template_id'] = sl_component.assessment_template_id and sl_component.assessment_template_id.id or False
        return class_data
    

class OdooCMSDBS(models.Model):
    _name = "odoocms.dbs"
    _description = "Department Board of Studies"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'
    
    def _get_waiting_domain(self):
        domain = [('state', 'in', ('draft','current','lock'))]
        return domain
    
    def _get_submitted_domain(self):
        domain = [('state', 'in', ('submit','disposal','approval','verify','done','notify'))]
        return domain
    
    name = fields.Char('Name',help='Number', copy=False, readonly=True)
    department_id = fields.Many2one('odoocms.department','Department')
    career_id = fields.Many2one('odoocms.career','Academic Level')
    term_id = fields.Many2one('odoocms.academic.term','Term')
    
    date = fields.Date()
    state = fields.Selection([('new','New'),('done','Done')],'Status',default='new')
    remarks = fields.Html('Minutes')
    grade_class_ids = fields.One2many('odoocms.class.grade','dbs_id','Submitted Result',
        domain = lambda self: self._get_submitted_domain())
    waiting_ids = fields.One2many('odoocms.class.grade', 'dbs_id', string='Waiting...',
        domain=lambda self: self._get_waiting_domain())
    completed = fields.Boolean('Completed',compute='_get_status',store=True)
    to_be = fields.Boolean(default=False)
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('odoocms.academic.dbs') or _('New')
        result = super().create(vals)
        return result
    
    @api.depends('grade_class_ids','grade_class_ids.dbs_action')
    def _get_status(self):
        for rec in self:
            if any([line.dbs_action == 'new' for line in rec.grade_class_ids]):
                rec.completed = False
            else:
                rec.completed = True

    def assign_dbs(self):
        for rec in self:
            if rec.state == 'new':
                grade_class_ids = self.env['odoocms.class.grade'].search(
                    [('department_id','=',rec.department_id.id),('career_id', '=', rec.career_id.id),('term_id', '=', rec.term_id.id),('dbs_id', '=', False)])
                for grade_class in grade_class_ids:
                    if grade_class.primary_class_ids:
                        grade_class.write({
                            'dbs_id': rec.id,
                            'dbs_action': 'new',
                        })
    
    def lock(self):
        self.waiting_ids.write({
            'dbs_id': False,
            'dbs_action': False,
        })
        self.state = 'done'


class OdooCMSFBS(models.Model):
    _name = "odoocms.fbs"
    _description = "Faculty Board of Studies"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    def _get_waiting_domain(self):
        domain = [('state', 'in', ('draft', 'current', 'lock','submit', 'disposal'))]
        return domain

    def _get_submitted_domain(self):
        domain = [('state', 'in', ('approval', 'verify', 'done', 'notify'))]
        return domain
    
    name = fields.Char('Name', help='Number', copy=False, readonly=True)
    institute_id = fields.Many2one('odoocms.institute', 'Institute')
    career_id = fields.Many2one('odoocms.career', 'Academic Level')
    term_id = fields.Many2one('odoocms.academic.term', 'Term')
    
    date = fields.Date()
    state = fields.Selection([('new', 'New'), ('done', 'Done')], 'Status', default='new')
    remarks = fields.Html('Minutes')
    grade_class_ids = fields.One2many('odoocms.class.grade', 'fbs_id', 'Submitted Result',
        domain=lambda self: self._get_submitted_domain())
    waiting_ids = fields.One2many('odoocms.class.grade', 'fbs_id', string='Waiting...',
        domain=lambda self: self._get_waiting_domain())
    completed = fields.Boolean('Completed', compute='_get_status', store=True)
    to_be = fields.Boolean(default=False)
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('odoocms.academic.fbs') or _('New')
        result = super().create(vals)
        return result
    
    @api.depends('grade_class_ids', 'grade_class_ids.fbs_action')
    def _get_status(self):
        for rec in self:
            if any([line.fbs_action == 'new' for line in rec.grade_class_ids]):
                rec.completed = False
            else:
                rec.completed = True
    
    def assign_fbs(self):
        for rec in self:
            if rec.state == 'new':
                grade_class_ids = self.env['odoocms.class.grade'].search(
                    [('institute_id', '=', rec.institute_id.id), ('career_id', '=', rec.career_id.id), ('term_id', '=', rec.term_id.id), ('fbs_id', '=', False)])
                for grade_class in grade_class_ids:
                    grade_class.write({
                        'fbs_id': rec.id,
                        'fbs_action': 'new',
                    })
    
    def lock(self):
        self.waiting_ids.write({
            'fbs_id': False,
            'fbs_action': False,
        })
        self.state = 'done'
        

class OdooCMSCourseDrop(models.Model):
    _inherit = "odoocms.student.course.drop"

    def action_approve(self):
        super().action_approve()
        for rec in self:
            for component in rec.registration_id.component_ids:
                assessments = self.env['odoocms.assessment.line'].search([
                    ('student_id','=',rec.student_id.id),
                    ('class_id','=',component.class_id.id)
                ])
                assessments.unlink()
