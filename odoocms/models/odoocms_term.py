import pdb

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class OdooCMSAcademicSession(models.Model):
    _name = 'odoocms.academic.session'
    _description = 'Academic Session'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence'

    # def unlink(self):
    #     for rec in self:
    #         raise ValidationError(_("Academic Session can not be deleted, You only can Archive it."))

    def copy(self):
        for rec in self:
            raise ValidationError(_("Academic Session can not duplicated. Create a new One"))

    name = fields.Char(string='Name', required=1, help='Name of Academic Session')
    code = fields.Char(string='Code', required=1, help='Code of Academic Session')
    description = fields.Text(string='Description', help="Description about the Academic Session")
    sequence = fields.Integer(string='Sequence', required=True, default=10)
    
    active = fields.Boolean('Active', default=True,
                            help="If Unchecked, it will allow you to hide the Academic Session without removing it.")
    
    _sql_constraints = [
        ('code', 'unique(code)', "Code already exists for another Academic Session!"),
        ('name', 'unique(name)', "Name already exists for another Academic Session!"),
    ]


class OdooCMSAcademicTerm(models.Model):
    _name = 'odoocms.academic.term'
    _description = 'Academic Term'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence desc'
    
#    def unlink(self):
 #       for rec in self:
  #          raise ValidationError(_("Academic Term can not be deleted, You only can Archive it."))

    name = fields.Char(string='Name', required=True, help='Name of Term',copy=False)
    code = fields.Char(string='Code', required=True, help='Code of Term', tracking=True,copy=False)
    sequence = fields.Integer(string='Sequence', required=True, default=50)
    short_code = fields.Char('Short Code',copy=False)
    number = fields.Integer('Number')
    type = fields.Selection([('regular', 'Regular'), ('summer', 'Summer'), ('special', 'Special')],
        string='Type', default='regular')
    enrollment_active = fields.Boolean('Enrollment Active?', default=False)

    # date_start = fields.Date(string='Date Start', required=True, help='Starting Date of Term')
    # date_end = fields.Date(string='Date End', help='Ending of Term')
    
    description = fields.Text(string='Description', help="Description about the Term")
    short_description = fields.Text(string='Short Description', help="Short Description about the Term")
    term_lines = fields.One2many('odoocms.academic.term.line', 'term_id', string='Term Lines',copy=True)
    
    _sql_constraints = [
        ('code', 'unique(code)', "Code already exists for another Term!"),
        ('name', 'unique(name)', "Name already exists for another Term!"),
    ]

    # @api.constrains('date_start', 'date_end')
    # def validate_date(self):
    #     for rec in self:
    #         start_date = fields.Date.from_string(rec.date_start)
    #         end_date = fields.Date.from_string(rec.date_end)
    #         if start_date >= end_date:
    #             raise ValidationError(_('Start Date must be Anterior to End Date'))
    
    
class OdooCMSAcademicTermLine(models.Model):
    _name = 'odoocms.academic.term.line'
    _description = 'Term Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence'

    # def copy(self):
    #     for rec in self:
    #         raise ValidationError(_("Academic Term detail can not duplicated. Create a new One"))
    #
    # def unlink(self):
    #     for rec in self:
    #         raise ValidationError(_("Academic Term Detail can not be deleted, You only can Archive it."))

    term_id = fields.Many2one('odoocms.academic.term', string='Term', required=True, help='Academic Term')
    name = fields.Char(string='Name', required=True,)
    # description = fields.Text(string='Description', help="Description about the Term")
    # type = fields.Selection([('regular', 'Regular'), ('summer', 'Summer'), ('special', 'Special')], string='Type',
    #                         default='regular')
    sequence = fields.Integer(string='Sequence', required=True, default=10)
    planning_ids = fields.One2many('odoocms.academic.term.planning', 'term_line_id', string='Plannings', copy=True )
    campus_ids = fields.Many2many('odoocms.campus', 'campus_term_rel',
        'term_line_id', 'campus_id', string='Campuses',copy=True)
    institute_ids = fields.Many2many('odoocms.institute', 'institute_term__rel',
        'term_line_id', 'institut_id', string='Schools',copy=True)
    career_ids = fields.Many2many('odoocms.career', 'career_term_rel',
        'term_line_id', 'career_id', string='Careers',copy=True)
    program_ids = fields.Many2many('odoocms.program', 'program_term_rel',
        'term_line_id', 'program_id', string='Program',copy=True)
    batch_ids = fields.Many2many('odoocms.batch', 'batch_term_rel',
        'term_line_id','batch_id',string='Batches',copy=True)

    date_start = fields.Date(string='Date Start', required=True, help='Starting Date of Term')
    date_end = fields.Date(string='Date End', required=True, help='Ending of Term')
    active = fields.Boolean('Active', default=True,
                            help="If Unchecked, it will allow you to hide the Term without removing it.")
    domain = fields.Char('Domain')

    # _sql_constraints = [
    #     ('code', 'unique(code)', "Code already exists for another Term!"),
    #     ('name', 'unique(name)', "Name already exists for another Term!"),
    #     ('short_code', 'unique(short_code)', "Short Code already exists for another Term!"),
    # ]

    @api.constrains('date_start', 'date_end')
    def validate_date(self):
        for rec in self:
            start_date = fields.Date.from_string(rec.date_start)
            end_date = fields.Date.from_string(rec.date_end)
            if start_date >= end_date:
                raise ValidationError(_('Start Date must be Anterior to End Date'))


class OdooCMSAcademicTermPlanning(models.Model):
    _name = 'odoocms.academic.term.planning'
    _description = 'Term Planning'
    _order = 'sequence desc'
    
    term_line_id = fields.Many2one('odoocms.academic.term.line', string='Term Line')

    name = fields.Char(string='Label', required=True, help='Name of Calendar Activity')
    type = fields.Selection([
        ('enrollment', 'Course Enrollment'),
        ('duesdate', 'Dues Date'),
        ('drop_w', 'Course Drop(W)'),
        ('drop_f', 'Delete Course Drop(F)'),
        ('i-grade', 'I Grade'),
        ('cancellation', 'Cancellation'),
        ('rechecking', 'Rechecking'),
        ('midterm', 'Mid Term'),
        ('finalterm', 'Finals'),
        ('full_refund', 'Full (100%) Refund'),
        ('half_refund', 'Half (50%) Refund'),
        ('classes_convene', 'Convene of Classes'),
        ('other', 'Other')
    ], string='Type')
    date_start = fields.Date(string='Date Start', required=True, help='Starting Date of Activity')
    date_end = fields.Date(string='Date End', required=True, help='Ending of Activity')
    sequence = fields.Integer(string='Sequence', required=True, default=50)

    # campus_ids = fields.Many2many('odoocms.campus', string='Campus')

    @api.constrains('date_start', 'date_end')
    def validate_date(self):
        for rec in self:
            start_date = fields.Date.from_string(rec.date_start)
            end_date = fields.Date.from_string(rec.date_end)
            if start_date >= end_date:
                raise ValidationError(_('Start Date must be Anterior to End Date'))


class OdooCMSSemester(models.Model):
    _name = "odoocms.semester"
    _description = "Semester"
    _order = 'sequence'

    name = fields.Char("Semester", required=True)
    code = fields.Char('Code')
    number = fields.Integer('Number', required=True)
    sequence = fields.Integer('Sequence')
    color = fields.Integer('Semester Color')


