import pdb
import calendar
from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class OdooCMSProgramStream(models.Model):
    _name = 'odoocms.program.stream'
    _description = 'Program Stream'
    
    name = fields.Char(string='Name', required=True, help="Stream Name")
    code = fields.Char(string="Code", required=True, help="Stream Code")
    
    
class OdooCMSCourseTag(models.Model):
    _name = 'odoocms.course.tag'
    _description = 'Course Tag'

    name = fields.Char(string='Name', required=True, help="Course Tag")
    code = fields.Char(string="Code", required=True)
    sequence = fields.Integer(string='Sequence')
    color = fields.Integer('Color')

    _sql_constraints = [
        ('code', 'unique(code)', "Another Tag already exists with this Code!"),
        ('name', 'unique(name)', "Another Tag already exists with this Name!"),
    ]
    

class OdooCMSCourse(models.Model):
    _name = 'odoocms.course'
    _description = 'CMS Course'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', help="Course Name", tracking=True)
    code = fields.Char(string="Code", help="Course Code", tracking=True)
    effective_date = fields.Date(string='Effective Date', help='Effective Date of Course')
    active = fields.Boolean('Active', default=True,
                            help="Current Status of Course")
    description = fields.Text(string='Description', help="Description about the Course")
    formal_description = fields.Text(string='Formal Description', help="Formal Description about the Course")
    career_id = fields.Many2one('odoocms.career', 'Academic Level')
    CourseID = fields.Char('CourseID')
    # type = fields.Selection([
    #     ('earned', 'Earned'),
    #     ('additional', 'Additional'),
    #     ('minor', 'Minor'),
    #     ('major', 'Major'),
    #     ('graded', 'Graded'),
    #     ('notgraded', 'NotGraded'),
    # ], string='Type', default="earned", help="Choose the type of the Course", tracking=True)

    prereq_course = fields.Boolean('Prerequisite Course', default=False, help="Prerequisite Course")
    prereq_operator = fields.Selection([('and','AND'),('or','OR')],'Prereq Operator',default='and')
    prereq_ids = fields.One2many('odoocms.course.prereq', 'course_id', string='PreRequisits', tracking=True)
    equivalent_ids = fields.One2many('odoocms.course.equivalent', 'course_id', string='Course Equivalent', tracking=True)
    component_lines = fields.One2many('odoocms.course.component', 'course_id', string='Course Components', tracking=True)
    credits = fields.Float('Credits',compute='_compute_credits',store=True)

    coreq_course = fields.Many2one('odoocms.course', 'Co-Requisite', tracking=True)
    tag_ids = fields.Many2many('odoocms.course.tag', 'course_tag_rel','course_id','tag_id','Tags', tracking=True)
    
    outline = fields.Html('Outline')
    suggested_books = fields.Text('Suggested Books')
    stream_id = fields.Many2one('odoocms.program.stream', 'Stream', tracking=True)
    major_course = fields.Many2one('odoocms.course.type',string="Course Type")
    self_enrollment = fields.Boolean('Self Enrollment', default=True)
    
    study_scheme_line_ids = fields.One2many('odoocms.study.scheme.line','course_id','Scheme Lines')
    
    _sql_constraints = [
        ('code', 'unique(code)', "Another Course already exists with this Code!"), ]

    @api.model
    def create(self, vals):
        if vals.get('code', False):
            course = self.env['odoocms.course'].search([('code','=',vals.get('code'))])
            if course:
                raise ValidationError('Course with same Code already exist!')
        res = super().create(vals)
        return res

    def write(self, vals):
        if vals.get('code', False):
            course = self.env['odoocms.course'].search([('id','!=',self.id),('code', '=', vals.get('code'))])
            if course:
                raise ValidationError('Course with same Code already exist!')
        res = super().write(vals)
        return res
    
    
        # if vals.get('state'):
        #     field_name_id = self.env['ir.model.fields'].search([('model','=',self._name),('name','=','state')])
        #     history_data = {
        #         'student_id': self.id,
        #         'field_name_id': field_name_id and field_name_id.id or False,
        #         'field_name': 'State',
        #         'changed_from': self.state,
        #         'changed_to': vals.get('state'),
        #         'changed_by': request.env.user.id,
        #         'date': datetime.now(),
        #     }
        #     self.env['odoocms.student.history'].create(history_data)
        #
        # if vals.get('tag_ids'):
        #     to_be_removed = self.env['odoocms.student.tag']
        #     updated_tags  = self.env['odoocms.student.tag'].search([('id','in',vals.get('tag_ids')[0][2])])
        #     added_tags =  updated_tags - self.tag_ids
        #     for added_tag in added_tags:
        #         if added_tag.category_id and not added_tag.category_id.multiple:
        #             if len(added_tags.filtered(lambda l: l.category_id == added_tag.category_id)) == 1:
        #                 to_be_removed += (updated_tags - added_tags).filtered(lambda l: l.category_id == added_tag.category_id)
        #             else:
        #                 raise UserError('The following tags can not be used simultaneously %s' % (', '.join([k.name for k in added_tags.filtered(lambda l: l.category_id == added_tag.category_id)])))
        #     updated_tags -= to_be_removed
        #     vals.get('tag_ids')[0][2] = updated_tags.ids
        #
        # method = 'Manual'
        # if vals.get('tag_apply_method'):
        #     method = vals.get('tag_apply_method')
        #     vals.pop('tag_apply_method')
        # old_tags = self.tag_ids.mapped('name')
        # res = super(OdooCMSStudent, self).write(vals)
        #
        # new_tags = self.tag_ids.mapped('name')
        # if vals.get('tag_ids'):  # old_tags != new_tags
        #     history_data = {
        #         'student_id': self.id,
        #         'field_name': 'Tags',
        #         'changed_from': old_tags,
        #         'changed_to': new_tags,
        #         'changed_by': request.env.user.id,
        #         'date': datetime.now(),
        #         'method': method,
        #     }
        #     self.env['odoocms.student.history'].create(history_data)
        #
        # return res
    
    
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.code:
                name = record.code + ' - ' + name
            res.append((record.id, name))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            recs = self.search([('name', operator, name)] + (args or []), limit=limit)
            if not recs:
                recs = self.search([('code', operator, name)] + (args or []), limit=limit)
            return recs.name_get()
        return super().name_search(name, args=args, operator=operator, limit=limit)

    @api.depends('component_lines','component_lines.weightage')
    def _compute_credits(self):
        for rec in self:
            credits = 0
            for component in rec.component_lines:
                credits += component.weightage
            rec.credits = credits

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Courses'),
            'template': '/odoocms/static/xls/odoocms_course.xls'
        }]
    

class OdooCMSCourseComponent(models.Model):
    _name = 'odoocms.course.component'
    _description = 'CMS Course Component'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    course_id = fields.Many2one('odoocms.course', ondelete='cascade')
    component_id = fields.Many2one('odoocms.components', ondelete='cascade')
    # component = fields.Selection([
    #     ('lab', 'Lab'),
    #     ('lecture', 'Lecture'),
    #     ('studio', 'Studio'),
    # ], string='Component',required=True)
    weightage = fields.Float(string='Credit Hours', default=3.0, help="Weightage for this Course", tracking=True)
    contact_hours = fields.Float(string='Contact Hours', default=1.0, help="Contact Hours for this Course", tracking=True)

    _sql_constraints = [
        ('unique_course_component_id', 'unique(course_id,component_id)', "Component already exists in Course"), ]
    
    @api.constrains('weightage', 'lab', 'lecture')
    def check_weightage(self):
        for rec in self:
            if rec.weightage < 0:
                raise ValidationError(_('Weightage must be Positive'))
  
    
class OdooCMSCoursePreReq(models.Model):
    _name = 'odoocms.course.prereq'
    _description = 'CMS Course PreRequist'
    
    course_id = fields.Many2one('odoocms.course', string='Course')
    prereq_id = fields.Many2one('odoocms.course', string='PreRequist')
    effective_date = fields.Date(string='Effective Date', help='Effective Date of PreRequist')


class OdooCMSCourseEquivalent(models.Model):
    _name = 'odoocms.course.equivalent'
    _description = 'CMS Course Equivalent'
    _rec_name = 'course_id'
    
    course_id = fields.Many2one('odoocms.course', string='Course')
    equivalent_id = fields.Many2one('odoocms.course', string='Equivalent')
    effective_date = fields.Date(string='Effective Date', help='Effective Date of Equivalent')
    

class OdooCMSCourseHistory(models.Model):
    _name = 'odoocms.course.history'
    _description = 'Course History'
    _order = 'course_id'
    _rec_name = 'course_id'

    course_id = fields.Many2one('odoocms.course', 'Course', required=True)
    field_name_id = fields.Many2one('ir.model.fields', 'Change In Attribute')
    field_name = fields.Char('Change In')
    changed_from = fields.Text('Changed From')
    changed_to = fields.Text('Changed To')
    changed_by = fields.Many2one('res.users', 'Changed By')
    date = fields.Datetime('Changed At')
    method = fields.Char('By Method')