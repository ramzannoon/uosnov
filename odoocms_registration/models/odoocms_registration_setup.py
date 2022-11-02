from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import pdb

READONLY_STATES = {
    'draft': [('readonly', False)],
    'current': [('readonly', True)],
    'lock': [('readonly', True)],
    'merge': [('readonly', True)],
    'submit': [('readonly', True)],
    'disposal': [('readonly', True)],
    'approval': [('readonly', True)],
    'done': [('readonly', True)],
}


class OdooCMSTermScheme(models.Model):
    _name = 'odoocms.term.scheme'
    _description = 'Term Scheme'
    _order = 'term_id,sequence'

    term_id = fields.Many2one('odoocms.academic.term', 'Academic Term', required=True)
    session_id = fields.Many2one('odoocms.academic.session','Academic Session')
    semester_id = fields.Many2one('odoocms.semester', string="Semester", required=True)
    state = fields.Selection([('draft','Draft'),('approve','Approved')],string='Status',default='draft')
    sequence = fields.Integer('Sequence')
    
    _sql_constraints = [
        ('session_term_unique', 'unique(session_id, term_id)', "Term Scheme already exists in Academic Term"),
    ]

    def name_get(self):
        return [(rec.id, rec.session_id.code + '-' + rec.term_id.code) for rec in self]
    
    def approve_scheme(self):
        for rec in self:
            study_schemes = self.env['odoocms.study.scheme'].search([('session_id','=',rec.session_id.id)])
            for study_scheme in study_schemes:
                for line in study_scheme.line_ids.filtered(lambda l: l.semester_id.id == rec.semester_id.id):
                    line.term_id = rec.term_id.id
            self.state = 'approve'

    def reset_draft(self):
        for rec in self:
            self.state = 'draft'
            
    def unlink(self):
        for rec in self:
            if rec.state == 'approve':
                raise ValidationError(_("Approved Term Scheme can not be deleted."))
        super(OdooCMSTermScheme, self).unlink()


class OdooCMSStudentRegistrationLoad(models.Model):
    _name = 'odoocms.student.registration.load'
    _description = 'Registration Load'
    _order = 'sequence'
    
    sequence = fields.Integer('Sequence')
    min = fields.Integer('Min Load')
    max = fields.Integer('Max Load')
    non = fields.Integer('Non-CR Load')
    repeat = fields.Integer('Repeat Load')
    type = fields.Selection([('regular','Regular Semester'),('summer','Summer Semester')])
    
    student_id = fields.Many2one('odoocms.student','Student')
    program_id = fields.Many2one('odoocms.program','Program')
    batch_id = fields.Many2one('odoocms.batch','Batch')
    career_id = fields.Many2one('odoocms.career','Academic Level')
    default_global = fields.Boolean('Global',default=False)

    _sql_constraints = [
        ('unique_rule', 'unique(default_global,career_id,batch_id,program_id,student_id)', "Rule already exists!"),
    ]
   

class OdooCMSCareer(models.Model):
    _inherit = "odoocms.career"

    registration_load_ids = fields.One2many('odoocms.student.registration.load', 'career_id', 'Registration Load')
    
    
class OdooCMSBatch(models.Model):
    _inherit = "odoocms.batch"

    registration_load_ids = fields.One2many('odoocms.student.registration.load','batch_id','Registration Load')
   
    section_ids = fields.One2many('odoocms.batch.section', 'batch_id', string='Sections')
    student_ids = fields.One2many('odoocms.student','batch_id','Students')
    allow_re_reg_wo_fee = fields.Boolean(string='Allow Course Re-Registration before Fee Submit', default = False)

    sequence_id = fields.Many2one('ir.sequence', string='ID Sequence',
        help="This field contains the information related to the registration numbering of the Student.",
        copy=False)
    sequence_number_next = fields.Integer(string='Next Number',
        help='The next sequence number will be used for the next Student Registration in the Batch.',
        compute='_compute_seq_number_next',
        inverse='_inverse_seq_number_next')

    grade_class_ids = fields.One2many('odoocms.class.grade', 'batch_id', string='Grade Classes',
        compute='_compute_grade_class_ids')

    def _compute_grade_class_ids(self):
        for rec in self:
            grade_classes = self.env['odoocms.class.grade'].search([('batch_id','=',rec.id),('term_id','=',rec.term_id.id)])
            rec.grade_class_ids = grade_classes.ids or False
            
    # do not depend on 'sequence_id.date_range_ids', because
    # sequence_id._get_current_sequence() may invalidate it!
    @api.depends('sequence_id.use_date_range', 'sequence_id.number_next_actual')
    def _compute_seq_number_next(self):
        for batch in self:
            if batch.sequence_id:
                sequence = batch.sequence_id._get_current_sequence()
                batch.sequence_number_next = sequence.number_next_actual
            else:
                batch.sequence_number_next = 1

    def _inverse_seq_number_next(self):
        for batch in self:
            if batch.sequence_id and batch.sequence_number_next:
                sequence = batch.sequence_id._get_current_sequence()
                sequence.sudo().number_next = batch.sequence_number_next

    @api.model
    def _get_sequence_prefix(self, code):
        prefix = code.upper()
        return prefix    # + '/%(range_year)s/'

    @api.model
    def _create_sequence(self, vals, refund=False):
        code = vals.get('code',False)
        if not code:
            code = self.code
        prefix = self._get_sequence_prefix(code)
        seq_name = code
        seq = {
            'name': _('%s Sequence') % seq_name,
            'implementation': 'no_gap',
            'prefix': prefix,
            'padding': 4,
            'number_increment': 1,
            #'use_date_range': True,
        }
        if 'company_id' in vals:
            seq['company_id'] = vals['company_id']
        seq = self.env['ir.sequence'].create(seq)
        #seq_date_range = seq._get_current_sequence()
        #seq_date_range.number_next = refund and vals.get('refund_sequence_number_next', 1) or vals.get('sequence_number_next', 1)
        seq.number_next = vals.get('sequence_number_next', 1)
        return seq
    
    # @api.model
    # def create(self, vals):
    #     if not vals.get('sequence_id'):
    #         vals.update({'sequence_id': self.sudo()._create_sequence(vals).id})
    #     batch = super(OdooCMSBatch, self).create(vals)
    #     return batch
    #
    def write(self, vals):
        for batch in self:
            batch = super(OdooCMSBatch, self).write(vals)
            if not self.sequence_id:
                self.sequence_id = self.sudo()._create_sequence(vals).id

    def unlink(self):
        for rec in self:
            if rec.section_ids:
                raise ValidationError(_("There are Sections mapped in this Batch, Batch can not be deleted; You only can Archive it."))
    
            if rec.student_ids:
                raise ValidationError(_("There are Students mapped in this Batch, Batch can not be deleted; You only can Archive it."))
        super(OdooCMSBatch, self).unlink()
    
    def component_hook(self,class_data,scheme_line):
        return class_data

    def batch_term_hook(self,batch_term_data):
        return batch_term_data
        

class OdooCMSBatchSection(models.Model):
    _name = "odoocms.batch.section"
    _description = "CMS Class Section"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence'
    
    sequence = fields.Integer('Sequence')
    name = fields.Char(string='Section Name', required=True, size=25)
    code = fields.Char(string='Code', compute='_section_code',store=True)
    color = fields.Integer(string='Color Index')
    strength = fields.Integer('Max Strength',default=45)
    batch_id = fields.Many2one('odoocms.batch','Program Batch', ondelete='cascade')

    primary_class_ids = fields.One2many('odoocms.class.primary','section_id','Primary Classes')
    student_ids = fields.One2many('odoocms.student', 'section_id', string='Students')
    student_count = fields.Integer(string='Students Count', compute='_get_student_count')
    room_id = fields.Many2one('odoocms.room','Room')
    to_be = fields.Boolean(default=False)
    
    _sql_constraints = [
        ('section_unique', 'unique(batch_id,name)', "Unique Section name is required for a Batch"), ]

    @api.depends('batch_id','batch_id.code','name')
    def _section_code(self):
        for rec in self:
            if rec.batch_id and rec.name:
                rec.code = rec.batch_id.code + '-' + rec.name
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            recs = self.search([('name', operator, name)] + (args or []), limit=limit)
            if not recs:
                recs = self.search([('code', operator, name)] + (args or []), limit=limit)
            return recs.name_get()
        return super(OdooCMSBatchSection, self).name_search(name, args=args, operator=operator, limit=limit)
    
    def _get_student_count(self):
        for rec in self:
            student_count = len(rec.student_ids)
            rec.update({
                'student_count': student_count
            })

    @api.constrains('strength')
    def validate_strength(self):
        for rec in self:
            if rec.strength < 0:
                raise ValidationError(_('Strength must be a Positive value'))

    def unlink(self):
        for rec in self:
            if rec.student_ids:
                raise ValidationError(_("There are Students mapped with this Section, Section can not be deleted; You only can Archive it."))
        super(OdooCMSBatchSection, self).unlink()


class OdooCMSClassGrade(models.Model):
    _name = "odoocms.class.grade"
    _description = "CMS Grading Class"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence'
    
    sequence = fields.Integer('Sequence')
    name = fields.Char(string='Class Name', required=True,states=READONLY_STATES)
    code = fields.Char(string='Code', copy=False, states=READONLY_STATES)

    term_id = fields.Many2one('odoocms.academic.term', 'Term', states=READONLY_STATES)
    batch_id = fields.Many2one('odoocms.batch', 'Program Batch', states=READONLY_STATES)
    career_id = fields.Many2one('odoocms.career', states=READONLY_STATES)
    program_id = fields.Many2one('odoocms.program', states=READONLY_STATES)
    department_id = fields.Many2one('odoocms.department', states=READONLY_STATES)
    institute_id = fields.Many2one('odoocms.institute', related='department_id.institute_id', store=True)
    study_scheme_id = fields.Many2one('odoocms.study.scheme', 'Study Scheme', states=READONLY_STATES)
    study_scheme_line_id = fields.Many2one('odoocms.study.scheme.line', 'Course', states=READONLY_STATES)

    batch_term_id = fields.Many2one('odoocms.batch.term','Batch Term', states=READONLY_STATES)
    primary_class_ids = fields.One2many('odoocms.class.primary','grade_class_id','Primary Classes', states=READONLY_STATES)
    grade_staff_id = fields.Many2one('odoocms.faculty.staff', string='Faculty for Grading', states=READONLY_STATES)
    registration_ids = fields.One2many('odoocms.student.course', 'grade_class_id', string='Students')
    student_count = fields.Integer(string='Students Count', compute='_get_student_count')
    
    state = fields.Selection([
        ('draft', 'Draft'), ('current', 'Current'), ('lock', 'Locked'),
        ('submit', 'Submitted'), ('disposal', 'Disposal'), ('approval', 'Approval'),
        ('verify','Verify'),('done', 'Done'), ('notify','Notify')
    ], 'Status', default='draft')
    to_be = fields.Boolean(default=False)
    
    _sql_constraints = [
        ('code', 'unique(code)', "Code already exists for another Grading Class"), ]

    def _get_student_count(self):
        for rec in self:
            student_count = len(rec.registration_ids)
            rec.update({
                'student_count': student_count
            })

    def name_get(self):
        return [(rec.id, (rec.code or '') + '-' + rec.name) for rec in self]
    
    def unlink(self):
        for rec in self:
            if rec.primary_class_ids:
                raise ValidationError(_("There are Classes mapped with this Grading Class, it can not be deleted; You only can Archive it."))
        super(OdooCMSClassGrade, self).unlink()

    def lock_class(self):
        self.state = 'lock'
        self.primary_class_ids.state = 'lock'
        self.primary_class_ids.mapped('class_ids').state = 'lock'
        
    def unlock_class(self):
        self.state = 'current'
        self.primary_class_ids.state = 'current'
        self.primary_class_ids.mapped('class_ids').state = 'current'
        

class OdooCMSClassPrimary(models.Model):
    _name = 'odoocms.class.primary'
    _description = 'CMS Primary Class'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'ac_sem_seq, ac_ses_seq'
    
    name = fields.Char(string='Name', required=True, help="Class Name", states=READONLY_STATES)
    code = fields.Char(string="Code", required=True, help="Code", states=READONLY_STATES)
    description = fields.Text(string='Description')

    class_type = fields.Selection([
        ('regular', 'Regular'), ('elective', 'Elective'), ('special', 'Special'), ('summer', 'Summer'), ('winter', 'Winter')
    ], 'Class Type', default='regular', states=READONLY_STATES)

    batch_id = fields.Many2one('odoocms.batch', 'Program Batch', states=READONLY_STATES)
    section_id = fields.Many2one('odoocms.batch.section', 'Class Section', states=READONLY_STATES)
    
    session_id = fields.Many2one('odoocms.academic.session', 'Academic Session')
    ac_ses_seq = fields.Integer('Session Seq.', related='session_id.sequence', store=True)

    career_id = fields.Many2one('odoocms.career', 'Academic Level', states=READONLY_STATES)
    program_id = fields.Many2one('odoocms.program', 'Program', states=READONLY_STATES)
    department_id = fields.Many2one('odoocms.department', string="Department", states=READONLY_STATES)
    institute_id = fields.Many2one("odoocms.institute", string="School", related='department_id.institute_id', store=True)
    campus_id = fields.Many2one('odoocms.campus', string='Campus', related='institute_id.campus_id', store=True)
    
    grade_class_id = fields.Many2one('odoocms.class.grade', 'Grade Class', states=READONLY_STATES, ondelete='cascade')
    grade_staff_id = fields.Many2one('odoocms.faculty.staff', string='Faculty for Grading', compute='_get_grade_faculty', store=True)
    batch_term_id = fields.Many2one('odoocms.batch.term', 'Batch Term', related='grade_class_id.batch_term_id',store=True)
    
    course_id = fields.Many2one('odoocms.course', 'Catalogue Course', states=READONLY_STATES)
    study_scheme_id = fields.Many2one('odoocms.study.scheme', 'Study Scheme', states=READONLY_STATES)
    study_scheme_line_id = fields.Many2one('odoocms.study.scheme.line', 'Scheme Line', states=READONLY_STATES)
    
    term_id = fields.Many2one('odoocms.academic.term', 'Academic Term', required=True, states=READONLY_STATES)
    ac_sem_seq = fields.Integer('Term Seq.', related='term_id.sequence', store=True)

    class_ids = fields.One2many('odoocms.class','primary_class_id','Classes', states=READONLY_STATES)

    strength = fields.Integer(string='Max. Class Strength', help="Total Max Strength of the Class")
    credits = fields.Float('Credits',compute='_compute_credits',store=True)
    manual_credits = fields.Float('M Credits',default=0.0)
    registration_ids = fields.One2many('odoocms.student.course', 'primary_class_id', string='Students')
    student_count = fields.Integer(string='Students Count', compute='_get_student_count')

    course_code = fields.Char('Course Code', tracking=True)
    course_name = fields.Char('Course Name', tracking=True)
    major_course = fields.Boolean('Major Course')
    self_enrollment = fields.Boolean('Self Enrollment')
    generator_id = fields.Many2one('odoocms.class.generator','Generator')
    class_nbr = fields.Char(string="Class NBR")
    CourseID = fields.Char('CourseID')
    active = fields.Boolean('Active', default=True)
    
    state = fields.Selection([
        ('draft', 'Draft'), ('current', 'Current'), ('lock', 'Locked'),
        ('submit', 'Submitted'), ('disposal', 'Disposal'), ('approval', 'Approval'),
        ('verify', 'Verify'), ('done', 'Done'), ('notify', 'Notify')
    ], 'Status', default='draft')
    to_be = fields.Boolean(default=False)
    import_identifier = fields.Many2one('ir.model.data', 'Import Identifier', compute='_get_import_identifier', store=True)

    _sql_constraints = [
        ('code_term', 'unique(code, active)', "Another Primary Class already exists with same Code!"), ]
    
    def _get_student_count(self):
        for rec in self:
            student_count = len(rec.registration_ids)
            rec.update({
                'student_count': student_count
            })

    def name_get(self):
        return [(rec.id, rec.code + '-' + rec.name) for rec in self]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            recs = self.search([('name', operator, name)] + (args or []), limit=limit)
            if not recs:
                recs = self.search([('code', operator, name)] + (args or []), limit=limit)
            if not recs:
                recs = self.search([('class_nbr', operator, name)] + (args or []), limit=limit)
            return recs.name_get()
        return super().name_search(name, args=args, operator=operator, limit=limit)

    @api.depends('class_ids', 'class_ids.weightage')
    def _compute_credits(self):
        for rec in self:
            credits = 0
            for component in rec.class_ids:
                credits += component.weightage
            rec.credits = rec.manual_credits if rec.manual_credits > 0 else credits
            
    @api.model
    def create(self, vals):
        res = super().create(vals)
        data = {}
        if not res.course_id:
            if res.CourseID:
                course_id = self.env['odoocms.course'].search([('CourseID', '=', res.CourseID)])
                if course_id:
                    data['course_id'] = course_id.id
                    if not res.course_code:
                        data['course_code'] = course_id.code
                        data['course_name'] = course_id.name

            elif res.study_scheme_line_id:
                course_id = res.study_scheme_line_id.course_id
                data['course_id'] = course_id.id
                if not res.course_code:
                    data['course_code'] = course_id.code
                    data['course_name'] = course_id.name
            
            elif res.course_code:
                course_id = self.env['odoocms.course'].search([('code','=',res.course_code),('career_id','=',res.career_id.id)])
                if course_id:
                    data['course_id'] = course_id.id
        elif not res.course_code:
            data['course_code'] = res.course_id.code
            data['course_name'] = res.course_id.name
            
        if data:
            res.write(data)
        return res

    # @api.depends('class_nbr','code')
    # def _get_import_identifier(self):
    #     for rec in self:
    #         name = 'class_' + (rec.class_nbr or rec.code)
    #         identifier = self.env['ir.model.data'].search(
    #             [('model', '=', 'odoocms.class.primary'), ('res_id', '=', rec.id)])
    #         if identifier:
    #             identifier.write({
    #                 'module': self.env.user.company_id.identifier or 'CLASS',
    #                 'name':  name,
    #             })
    #         else:
    #             data = {
    #                 'name': name,
    #                 'module': self.env.user.company_id.identifier or 'CLASS',
    #                 'model': 'odoocms.class.primary',
    #                 'res_id': rec.id,
    #             }
    #             identifier = self.env['ir.model.data'].create(data)
    #         rec.import_identifier = identifier.id
    
    @api.depends('class_ids', 'class_ids.faculty_staff_id', 'class_ids.sequence')
    def _get_grade_faculty(self):
        for rec in self:
            staff_id = rec.class_ids.sorted(key=lambda r: r.sequence)[:1]
            if staff_id:
                rec.grade_staff_id = staff_id.faculty_staff_id.id
                rec.grade_class_id.grade_staff_id = staff_id.faculty_staff_id.id

    def view_students(self):
        self.ensure_one()
    
        students_list = self.registration_ids.mapped('student_id')
        return {
            'domain': [('id', 'in', students_list.ids)],
            'name': _('Students'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'odoocms.student',
            'view_id': False,
            'context': {'default_primary_class_id': self.id},
            'type': 'ir.actions.act_window'
        }
    
    def unlink(self):
        for rec in self.sudo():
            if rec.registration_ids:
                raise ValidationError(_("Students are registered in the Primary Class, Class can not be deleted."))
        
            grade_class = rec.grade_class_id
            for component_class in rec.class_ids:
                component_class.unlink()

            #.with_context(dict(active_test=False))
            ctx = self.env.context.copy()
            ctx['active_test'] = False
            dropped_courses = self.env['odoocms.student.course'].sudo().with_context(ctx).search([
                ('primary_class_id', '=', rec.id), ('active', '=', False)])
            dropped_courses.sudo().unlink()
            
            super().unlink()
            grade_class.unlink()
            
    def set_to_draft(self):
        if self.state == 'current':
            self.state = 'draft'
            self.grade_class_id.state = 'draft'
            for rec in self:
                rec.class_ids.state = 'draft'

    def set_to_current(self):
        if self.state == 'draft':
            self.state = 'current'
            self.grade_class_id.state = 'current'
            for rec in self:
                rec.class_ids.state = 'draft'
            
    
class OdooCMSClass(models.Model):
    _name = 'odoocms.class'
    _description = 'CMS Class'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'
    
    name = fields.Char(string='Name', required=True, help="Class Name",states=READONLY_STATES)
    code = fields.Char(string="Code", required=True, help="Code",states=READONLY_STATES)
    description = fields.Text(string='Description')
    
    primary_class_id = fields.Many2one('odoocms.class.primary','Primary Class',states=READONLY_STATES, ondelete='cascade')
    course_id = fields.Many2one('odoocms.course', 'Catalogue Course', related='primary_class_id.course_id',store=True)
    term_id = fields.Many2one('odoocms.academic.term', 'Academic Term', related='primary_class_id.term_id',store=True)
    section_id = fields.Many2one('odoocms.batch.section', 'Class Section', states=READONLY_STATES)
    faculty_staff_id = fields.Many2one('odoocms.faculty.staff', string='Primary Faculty',compute='_get_primary_faculty',store=True)
    faculty_ids = fields.One2many('odoocms.class.faculty', 'class_id',string='Faculty Staff')
    allow_secondary_staff = fields.Boolean('Access to Secondary Staff',default=False)
    batch_id = fields.Many2one('odoocms.batch', 'Program Batch', related='primary_class_id.batch_id', store=True)
    session_id = fields.Many2one('odoocms.academic.session', 'Academic Session', related='primary_class_id.session_id', store=True)
    career_id = fields.Many2one('odoocms.career', 'Academic Level', related='primary_class_id.career_id', store=True)

    component_id = fields.Many2one('odoocms.components', ondelete='cascade')
    # component = fields.Selection([
    #     ('lab', 'Lab'),
    #     ('lecture', 'Lecture'),
    #     ('studio', 'Studio'),
    # ], string='Component', states=READONLY_STATES)

    weightage = fields.Float(string='Credit Hours', default=3.0, help="Weightage for this Course", states=READONLY_STATES, tracking=True)
    contact_hours = fields.Float(string='Contact Hours', default=1.0, help="Contact Hours for this Course", states=READONLY_STATES, tracking=True)

    registration_component_ids = fields.One2many('odoocms.student.course.component', 'class_id', string='Students', domain=[('dropped','=',False)])
    student_count = fields.Integer(string='Students Count', compute='_get_student_count')
    sequence = fields.Integer('Priority')
    active = fields.Boolean('Active',default=True)
    
    state = fields.Selection([
        ('draft', 'Draft'), ('current', 'Current'), ('lock', 'Locked'), ('merge','Merged'),
        ('submit', 'Submitted'), ('disposal', 'Disposal'), ('approval', 'Approval'),
        ('verify', 'Verify'), ('done', 'Done'), ('notify', 'Notify')
    ], 'Status', default='draft')
    merge_id = fields.Many2one('odoocms.class','Merge with')
    to_be = fields.Boolean(default=False)
    
    _sql_constraints = [
        ('code', 'unique(code,active)', "Another Class already exists with same Code!"), ]

    @api.constrains('weightage')
    def check_weightage(self):
        for rec in self:
            if rec.weightage < 0:
                raise ValidationError(_('Weightage must be Positive'))


    @api.depends('faculty_ids','faculty_ids.role_id')
    def _get_primary_faculty(self):
        for rec in self:
            staff_ids = rec.faculty_ids.filtered(lambda l: (l.role_id.code  or "").upper() == 'PRIMARY')
            for staff in staff_ids:
                rec.faculty_staff_id = staff.faculty_staff_id.id

    def action_marge_class(self):
        for reg in self.registration_component_ids:
            reg.class_id = self.merge_id.id
        self.state = 'merge'
        self.active = False
   
    # @api.onchange('study_scheme_line_id')
    # def onchagene_scheme_line(self):
    #     subject = self.study_scheme_line_id
    #     self.weightage = subject.weightage
    #     self.lecture = subject.lecture
    #     self.lab = subject.lab
    #     self.course_code = subject.course_code or subject.subject_id.code
    #     self.course_name = subject.course_name or subject.subject_id.name
    #

    def name_get(self):
        return [(rec.id, rec.code + '-' + rec.name) for rec in self]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            recs = self.search([('name', operator, name)] + (args or []), limit=limit)
            if not recs:
                recs = self.search([('code', operator, name)] + (args or []), limit=limit)
            return recs.name_get()
        return super(OdooCMSClass, self).name_search(name, args=args, operator=operator, limit=limit)
        
    def set_to_draft(self):
        if self.state == 'current':
            self.state = 'draft'
            self.primary_class_id.state = 'draft'
            self.primary_class_id.grade_class_id.state = 'draft'

    def set_to_current(self):
        if self.state == 'draft':
            self.state = 'current'
            self.primary_class_id.state = 'current'
            self.primary_class_id.grade_class_id.state = 'current'

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Class Section'),
            'template': '/odoocms_registration/static/xls/odoocms_class.xls'
        }]

    def view_students(self):
        self.ensure_one()
        
        students_list = self.registration_component_ids.mapped('student_id')
        return {
            'domain': [('id', 'in', students_list.ids)],
            'name': _('Students'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'odoocms.student',
            'view_id': False,
            'context': {'default_class_id': self.id},
            'type': 'ir.actions.act_window'
        }
    
    def _get_student_count(self):
        for rec in self:
            student_count = len(rec.registration_component_ids)
            rec.update({
                'student_count': student_count
            })


class OdooCMSClassFaculty(models.Model):
    _name = 'odoocms.class.faculty'
    _description = 'CMS Class Faculty'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    class_id = fields.Many2one('odoocms.class','Class Component')
    term_id = fields.Many2one('odoocms.academic.term', related="class_id.term_id", string='Academic Term', store=True)
    credits = fields.Float('Credits',related='class_id.weightage',store=True)
    student_count = fields.Integer('Student Count',related='class_id.student_count')
    faculty_staff_id = fields.Many2one('odoocms.faculty.staff','Faculty Member')
    role_id = fields.Many2one('odoocms.faculty.staff.position','Role')
    active = fields.Boolean(default=True)
    
        
class OdooCMSStudySchemeLine(models.Model):
    _inherit = 'odoocms.study.scheme.line'
    
    primary_class_ids = fields.One2many('odoocms.class.primary','study_scheme_line_id','Primary Classes')

    def unlink(self):
        for rec in self:
            if rec.primary_class_ids:
                raise ValidationError(_("Scheme Line maps with Primary Classes and can not be deleted, You only can Archive it."))
        super().unlink()
        

class OdooCMSCourse(models.Model):
    _inherit = 'odoocms.course'
    
    primary_class_ids = fields.One2many('odoocms.class.primary','course_id','Primary Classes')
    registration_ids = fields.One2many('odoocms.student.course','course_id','Registrations')

    def unlink(self):
        for rec in self:
            if rec.primary_class_ids:
                raise ValidationError(_("Course maps with Primary Classes and can not be deleted, You only can Archive it."))
        super().unlink()


class OdooCMSAcademicTerm(models.Model):
    _inherit = 'odoocms.academic.term'
    
    term_scheme_ids = fields.One2many('odoocms.term.scheme', 'term_id', 'Study Schemes')
    primary_class_ids = fields.One2many('odoocms.class.primary', 'term_id', 'Primary Classes')

    # scheme_lines = fields.One2many('odoocms.term.scheme', 'term_id', 'Study Schemes')
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved')], string='Status', default='draft')

    def approve_scheme(self):
        for rec in self.term_scheme_ids:
            rec.approve_scheme()
        self.state = 'approve'

    def reset_draft(self):
        for rec in self.term_scheme_ids:
            rec.reset_draft()
        self.state = 'draft'
        

class OdooCMSAcademicSession(models.Model):
    _inherit = 'odoocms.academic.session'
    
    term_scheme_ids = fields.One2many('odoocms.term.scheme', 'session_id', 'Study Scheme')
    batch_ids = fields.One2many('odoocms.batch', 'session_id', 'Batches')
    

class OdooCMSProgram(models.Model):
    _inherit = 'odoocms.program'

    registration_load_ids = fields.One2many('odoocms.student.registration.load', 'program_id', 'Registration Load')
    
    registration_domain = fields.Char('Registration Domain for Compulsory')
    elec_registration_domain = fields.Char('Registration Domain For Elective Courses')
    additional_registration_domain = fields.Char('Registration Domain For Additional Courses')
    minor_registration_domain = fields.Char('Registration Domain For Minor Courses')
    repeat_registration_domain = fields.Char('Registration Domain For Repeat Courses')
    
    
class OdooCMSStudent(models.Model):
    _inherit = 'odoocms.student'

    batch_id = fields.Many2one('odoocms.batch', 'Program Batch', tracking=True, readonly=True,
                               states={'draft': [('readonly', False)]})
    section_id = fields.Many2one('odoocms.batch.section', 'Class Section', tracking=True, readonly=True,
                                 states={'draft': [('readonly', False)]})
    
    
class OdooCMSBatchTerm(models.Model):
    _name = "odoocms.batch.term"
    _description = "Batch Term"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name desc'

    def _get_waiting_domain(self):
        domain = [('state', 'in', ('draft','current','lock','submit'))]
        return domain
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    sequence = fields.Integer('Sequence')
    color = fields.Integer(string='Color Index')
    batch_id = fields.Many2one('odoocms.batch','Batch')
    department_id = fields.Many2one('odoocms.department', string="Department", related='batch_id.department_id')
    career_id = fields.Many2one('odoocms.career', string="Academic Level", related='batch_id.career_id')
    program_id = fields.Many2one('odoocms.program', string="Program", related='batch_id.program_id')
    session_id = fields.Many2one('odoocms.academic.session', 'Academic Session', related='batch_id.session_id')
    term_id = fields.Many2one('odoocms.academic.term', 'Current Term')
    semester_id = fields.Many2one('odoocms.semester', 'Semester')
   
    grade_class_ids = fields.One2many('odoocms.class.grade', 'batch_term_id', string='Grade Classes')
    registration_ids = fields.One2many('odoocms.student.course', 'batch_term_id', string='Registrations')
    waiting_ids = fields.One2many('odoocms.student.course', 'batch_term_id', string='Waiting...',
        domain=lambda self: self._get_waiting_domain())
    
    state = fields.Selection([
        ('draft', 'Draft'), ('disposal', 'Disposal'), ('approval', 'Approval'),
        ('verify', 'Verify'), ('done', 'Done'), ('notify', 'Notify')
    ], 'Status', compute='get_status')
    
    _sql_constraints = [
        ('code', 'unique(code)', "Code already exists for some other Batch Term"),
    ]
    
    def get_status(self):
        for rec in self:
            if any([line.state == 'notify' for line in rec.grade_class_ids]):
                rec.state = 'notify'
            elif any([line.state == 'done' for line in rec.grade_class_ids]):
                rec.state = 'done'
            elif any([line.state == 'verify' for line in rec.grade_class_ids]):
                rec.state = 'verify'
            elif any([line.state == 'approval' for line in rec.grade_class_ids]):
                rec.state = 'approval'
            elif any([line.state == 'disposal' for line in rec.grade_class_ids]):
                rec.state = 'disposal'
            else:
                rec.state = 'draft'

        
class OdooCMSFacultyStaff(models.Model):
    _inherit = 'odoocms.faculty.staff'

    class_ids = fields.One2many('odoocms.class.faculty','faculty_staff_id','Classes')
    credits = fields.Float('Credit Load',compute='_compute_load_credits',store=True)
#     course_ids = fields.Many2many('odoocms.course','faculty_course_rel','faculty_id','course_id','Courses')
    term_id = fields.Many2one('odoocms.academic.term','Term')
#
    @api.depends('term_id','class_ids')
    def _compute_load_credits(self):
        for rec in self:
            credits = 0
            classes = rec.class_ids.filtered(lambda l: l.term_id.id == rec.term_id.id).mapped('class_id')
            for pclass in classes:
                credits += pclass.weightage
                if pclass.student_count > 50:
                    credits += 1
            courses = classes.mapped('course_id')
            if len(courses) >= 3:
                credits += 2
            elif len(courses) >= 2:
                credits += 1
            rec.credits = credits
        
    
