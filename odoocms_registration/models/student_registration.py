from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools.safe_eval import safe_eval
from odoo.osv import expression

import pdb


class OdooCMSStudentCourse(models.Model):
    _name = "odoocms.student.course"
    _description = "Student Course Details"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _order = 'semester_date,student_id'

    READONLY_STATES = {
        'current': [('readonly', True)],
        'submit': [('readonly', True)],
        'lock': [('readonly', True)],
        'disposal': [('readonly', True)],
        'approval': [('readonly', True)],
        'dropped': [('readonly', True)],
        'done': [('readonly', True)],
    }

    student_id = fields.Many2one('odoocms.student', 'Student', ondelete="cascade")
    program_id = fields.Many2one('odoocms.program', 'Program', related='student_id.program_id', store=True)
    institute_id = fields.Many2one('odoocms.institute', 'School', related='student_id.program_id.institute_id', store=True)
    batch_id = fields.Many2one('odoocms.batch', 'Batch', related='student_id.batch_id', store=True)
    session_id = fields.Many2one('odoocms.academic.session', 'Academic Session',
                                          related='student_id.session_id', store=True)
    semester_id = fields.Many2one('odoocms.semester', 'Semester')
    date_effective = fields.Date('Effective Date', default=fields.Date.today(),states=READONLY_STATES)
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    
    primary_class_id = fields.Many2one('odoocms.class.primary', 'Primary Class', ondelete="restrict")
    grade_class_id = fields.Many2one('odoocms.class.grade','Grade Class',related='primary_class_id.grade_class_id',store=True)
    batch_term_id = fields.Many2one('odoocms.batch.term', 'Batch Term', compute='_get_batch_term', store=True)
    term_id = fields.Many2one('odoocms.academic.term', 'Term')
    number = fields.Integer(related='term_id.number', store=True)

    student_term_id = fields.Many2one('odoocms.student.term', 'Student Term')
    
    course_id = fields.Many2one('odoocms.course','Catalogue Course')
    credits = fields.Float('Credits', related='primary_class_id.credits', store=True)
    credit = fields.Float('Credit')
    
    course_code = fields.Char('Course Code', required=True, states=READONLY_STATES)
    course_name = fields.Char('Course Name', required=True, states=READONLY_STATES)
    CourseID = fields.Char('CourseID')
    component_ids = fields.One2many('odoocms.student.course.component', 'student_course_id','Components')
    course_type = fields.Selection([
        ('compulsory','Compulsory'),
        ('elective','Elective'),
        ('repeat','Repeat'),
        ('improve','Improve'),
        ('additional','Additional'),
        ('alternate','Alternate'),
        ('minor','Minor'),
        ('thesis', 'Thesis'),
    ],'Course Type',default='compulsory')
   
    transferred = fields.Boolean('Transferred Course',default=False)
    dropped = fields.Boolean('Dropped',default=False)
    dropped_date = fields.Datetime('Dropped Date')
    is_defer = fields.Boolean(default=False)
    class_nbr = fields.Integer()

    repeat_code = fields.Char("RPT Code")
    tscrpt__note254 = fields.Char('TSCRPT_NOTE254')

    inc_in_cgpa = fields.Char()

    course_id_1 = fields.Many2one('odoocms.student.course')
    course_id_2 = fields.Many2one('odoocms.student.course')

    tag = fields.Char('Tag', readonly=True)
    active = fields.Boolean('Active', default=True, tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'), ('current', 'Current'), ('lock', 'Locked'),('dropped','Dropped'),
        ('submit', 'Submitted'), ('disposal', 'Disposal'), ('approval', 'Approval'),
        ('verify', 'Verify'), ('done', 'Done'), ('notify', 'Notify')
    ], 'Status', compute='_get_course_state', store=True)
    to_be = fields.Boolean(default=False)
    prereq = fields.Boolean('Pre-req Satisfy?',default=True)
    prereq_course_id = fields.Many2one('odoocms.course')
    
    _sql_constraints = [
        ('unique_student_term_course',
         'unique(student_id,term_id,course_id,active,dropped_date)',
         'Student can take a course once in an Academic Term!'),
    ]
    
    @api.depends('batch_id','term_id')
    def _get_batch_term(self):
        for rec in self:
            batch_term = False
            if rec.batch_id and rec.term_id:
                batch_term = self.env['odoocms.batch.term'].search(
                    [('batch_id', '=', rec.batch_id.id), ('term_id', '=', rec.batch_id.term_id.id)]
                )
            rec.batch_term_id = batch_term and batch_term.id or False
        
    @api.depends('primary_class_id','primary_class_id.state','dropped')
    def _get_course_state(self):
        for rec in self:
            if rec.dropped:
                rec.state = 'done'
            elif rec.primary_class_id:
                rec.state = rec.sudo().primary_class_id.state
            else:
                rec.state = 'done'
                
    def name_get(self):
        return [
            (rec.id, rec.student_id.code + ('-' + rec.primary_class_id.code + '-' +
                rec.primary_class_id.name) if rec.primary_class_id else '- Transferred')
                    for rec in self.sudo()
        ]

    @api.onchange('course_id')
    def onchagene_course(self):
        course = self.course_id
        self.credits = course.credits
        self.course_code = course.code
        self.course_name = course.name

    @api.model
    def create(self, vals):
        data = {}
        res = super().create(vals)
        term = res.term_id or res.primary_class_id.term_id
        
        if not res.term_id and res.primary_class_id:
            data['term_id'] = res.primary_class_id.term_id.id
            
        if not res.course_id:
            if res.primary_class_id:
                course_id = res.primary_class_id.course_id
                data['course_id'] = course_id.id
                if not res.course_code:
                    data['course_code'] = course_id.code
                    data['course_name'] = course_id.name
            elif res.CourseID:
                course_id = self.env['odoocms.course'].search([('CourseID','=',res.CourseID)])
                if course_id:
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
            
        term_obj = self.env['odoocms.student.term']
        st_term = term_obj.search([('student_id', '=', res.student_id.id), ('term_id', '=', term.id)])
        if not st_term:
            term_data = {
                'student_id': res.student_id.id,
                'term_id': term.id,
                'semester_id': res.semester_id.id,
            }
            if res.course_type == 'thesis':
                term_data['number'] = 10000
                term_data['term_type'] = 'thesis'
                
            st_term = term_obj.create(term_data)
        data['student_term_id'] = st_term.id
        res.write(data)
        return res


class OdooCMSStudentCourseComponent(models.Model):
    _name = "odoocms.student.course.component"
    _description = "Student Course Component Details"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _order = 'semester_date,student_id'

    student_course_id = fields.Many2one('odoocms.student.course', 'Student Course', ondelete="cascade")
    student_id = fields.Many2one('odoocms.student', 'Student')
    program_id = fields.Many2one('odoocms.program', 'Program', related='student_id.program_id', store=True)
    batch_id = fields.Many2one('odoocms.batch', 'Batch', related='student_id.batch_id', store=True)
    session_id = fields.Many2one('odoocms.academic.session', 'Academic Session', related='student_id.session_id', store=True)
    semester_id = fields.Many2one('odoocms.semester', 'Semester')

    class_id = fields.Many2one('odoocms.class', 'Class', ondelete="restrict")
    term_id = fields.Many2one('odoocms.academic.term', 'Term')
    active = fields.Boolean('Active',default=True)
    
    weightage = fields.Float(string='Credit Hours', default=1.0, help="Credits for this Course", required=True,)
    
    dropped = fields.Boolean(related='student_course_id.dropped',store=True)
    to_be = fields.Boolean(default=False)
   
    # _sql_constraints = [
    #     ('unique_student_term_course',
    #      'unique(student_id,term_id,course_id)',
    #      'Student can take a course once in an Academic Term!'),
    # ]

    def name_get(self):
        return [(rec.id, rec.student_id.code + '-' + rec.class_id.code+ '-' + rec.class_id.name or "-") for rec in self]

    # @api.onchange('course_id')
    # def onchagene_course(self):
    #     course = self.course_id
    #     self.credits = course.weightage
    

class OdooCMSStudentTerm(models.Model):
    _name = "odoocms.student.term"
    _description = "Student Term Details"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'semester_id'
    _order = 'number,student_id'

    student_id = fields.Many2one('odoocms.student', 'Student', ondelete="cascade")
    program_id = fields.Many2one('odoocms.program', 'Program', related='student_id.program_id', store=True)
    batch_id = fields.Many2one('odoocms.batch', 'Batch', related='student_id.batch_id', store=True)
    career_id = fields.Many2one('odoocms.career', 'Academic Level', related='student_id.career_id', store=True)
    session_id = fields.Many2one('odoocms.academic.session', 'Academic Session', related='student_id.session_id', store=True)
    
    term_line_id = fields.Many2one('odoocms.academic.term.line', 'Term Line',compute='get_term_line',store=True)
    term_id = fields.Many2one('odoocms.academic.term', 'Term')
    number = fields.Integer(related='term_id.number', store=True)
    term_type = fields.Selection([
        ('regular','Regular'),
        ('defer','Deferred'),
        ('extra','Extra'),
        ('thesis','Thesis'),
        ('exchange', 'Exchange Program'),
        ('internal', 'Internal Transfer'),
        ('external', 'External Transfer'),
    ],'Term Type',default='regular')
    # semester_date = fields.Date(related='term_id.date_start', store=True)
    semester_id = fields.Many2one('odoocms.semester', 'Semester')
    state = fields.Selection([('draft', 'Draft'), ('current', 'Current'), ('result','Result'),('done', 'Done'),], 'Status',
        compute='_get_status', store=True)
    student_course_ids = fields.One2many('odoocms.student.course', 'student_term_id', 'Term Courses')
    to_be = fields.Boolean(default=False)
    import_identifier = fields.Many2one('ir.model.data', 'Import Identifier')  # , compute='_get_import_identifier', store=True

    next_term = fields.Many2one('odoocms.student.term','Next Term')
    prev_term = fields.Many2one('odoocms.student.term','Prev Term')
    
    _sql_constraints = [
        ('unique_student_term',
         'unique(student_id,term_id)',
         'Student can enroll once in an Academic Term!'),
    ]

    def name_get(self):
        return [(rec.id, rec.student_id.code + ':' + rec.student_id.name + '-' +
                 (rec.term_id.code or rec.term_id.short_code or rec.term_id.name)) for rec in self]
    
    @api.depends('student_course_ids', 'student_course_ids.state')
    def _get_status(self):
        for rec in self:
            if any([course.primary_class_id.state in ('draft','current','lock','submit') for course in rec.student_course_ids.filtered(lambda l: l.active == True)]):
                rec.state = 'current'
            elif any([course.primary_class_id.state in ('disposal','approval','verify') for course in rec.student_course_ids.filtered(lambda l: l.active == True)]):
                rec.state = 'result'
            else:
                rec.state = 'done'

    @api.depends('term_id.term_lines', 'term_id.term_lines.date_start', 'term_id.term_lines.date_end')
    def get_term_line(self):
        for st_term in self:
            term_line = self.env['odoocms.academic.term.line']
            for rec in st_term.term_id.term_lines.sorted(key=lambda s: s.sequence, reverse=False):
                term_line = rec
                if rec.campus_ids and st_term.program_id.campus_id not in rec.campus_ids:
                    continue
                elif rec.institute_ids and st_term.program_id.department_id.institute_id not in rec.institute_ids:
                    continue
                elif rec.career_ids and st_term.career_id not in rec.career_ids:
                    continue
                elif rec.program_ids and st_term.program_id not in rec.program_ids:
                    continue
                elif rec.batch_ids and st_term.batch_id not in rec.batch_ids:
                    continue
                else:
                    break
            st_term.term_line_id = term_line and term_line.id or False

    # st-term-00000173657-S17
    @api.depends('student_id','term_id')
    def _get_import_identifier(self):
        for rec in self:
            if rec.student_id and rec.term_id and rec.id:
                name = 'st-term-' + rec.student_id.code + '-' + rec.term_id.short_code
                identifier = self.env['ir.model.data'].search(
                    [('model', '=', 'odoocms.student.term'), ('res_id', '=', rec.id)])
                if identifier:
                    identifier.module = self.env.user.company_id.identifier or 'nust'
                    identifier.name = name
                else:
                    data = {
                        'name': name,
                        'module': self.env.user.company_id.identifier or 'nust',
                        'model': 'odoocms.student.term',
                        'res_id': rec.id,
                    }
                    identifier = self.env['ir.model.data'].create(data)
                rec.import_identifier = identifier.id

    @api.model
    def cron_identifier_job(self, n=500):
        recs_count = self.search_count([('to_be', '=', True)])
        terms = self.search([('to_be', '=', True)], limit=n)
        for term in terms:  # .with_progress(msg="Compute Result ({})".format(recs_count)):
            term._get_import_identifier()
            term.to_be = False

    @api.model
    def cron_get_status_job(self, n=500):
        recs_count = self.search_count([('to_be', '=', True)])
        terms = self.search([('to_be', '=', True)], limit=n)
        for term in terms:  # .with_progress(msg="Compute Result ({})".format(recs_count)):
            term._get_status()
            term.to_be = False
    
            
class OdooCMSStudent(models.Model):
    _inherit = 'odoocms.student'

    def _get_drop_domain(self):
        domain = [('term_id','=',self.term_id.id),('dropped', '=', True),'|',('active','=',True),('active','=',False)]
        return domain
        
    section_id = fields.Many2one('odoocms.batch.section', 'Class Section', tracking=True, readonly=True,
        states={'draft': [('readonly', False)]})
    term_ids = fields.One2many('odoocms.student.term', 'student_id', 'Results (Term)', domain=[('state', '=', 'done')])
    enroll_term_ids = fields.One2many('odoocms.student.term', 'student_id', 'Enrolled Terms')
    current_term_ids = fields.One2many('odoocms.student.term', 'student_id', 'Terms',
        domain=[('state', 'in', ('draft', 'current'))])
    course_ids = fields.One2many('odoocms.student.course', 'student_id', 'Registered Courses',
        domain=[('state', 'not in', ('done', 'notify'))])
    dropped_course_ids = fields.One2many('odoocms.student.course', 'student_id', 'Dropped Courses',
        domain=lambda self: self._get_drop_domain(), context={'active_test': False})
    result_course_ids = fields.One2many('odoocms.student.course', 'student_id', 'Courses Result', domain=[('state', 'in', ('done','notify'))])
    enrolled_course_ids = fields.One2many('odoocms.student.course', 'student_id', 'Enrolled Courses',)
    allow_re_reg_wo_fee = fields.Boolean(string='Allow Course Re-Registration before Fee Submit', default=False)

    registration_load_ids = fields.One2many('odoocms.student.registration.load','student_id','Registration Load')
    repeat_courses_count = fields.Integer(string="No of Course Repeated", compute='_get_repeat_course_count')

    @api.depends('enrolled_course_ids', 'enrolled_course_ids.course_id_1', 'enrolled_course_ids.course_id_2')
    def _get_repeat_course_count(self):
        for rec in self:
            rec.repeat_courses_count = len(rec.enrolled_course_ids.filtered(lambda c: c.course_id_1))

    def register_courses(self,primary_class_ids, term_id, st_term, date_effective, type='compulsory'):
        reg = self.env['odoocms.student.course']
        alternate_id = course_id_1 = False
        
        for primary_class in primary_class_ids:
            course_id = primary_class.course_id
            
            new_registration = self.register_course(term_id, course_id, st_term, primary_class, date_effective)
            if new_registration.get('reg', False):
                new_reg = new_registration.get('reg')
                new_reg.course_type = type
                reg += new_reg

                if type in ('additional', 'minor'):
                    new_reg.include_in_cgpa = False

                elif type == 'alternate':
                    if alternate_id and alternate_id.type == 'grade':
                        course_id_1 = self.env['odoocms.student.course'].search([
                            ('course_id', '=', alternate_id.catalogue_id.id), ('student_id', '=', self.id)
                        ])
                else:
                    course_id_1 = self.env['odoocms.student.course'].search([
                        ('course_code', '=', primary_class.course_code), ('student_id', '=', self.id), ('id', '!=', new_reg.id)
                    ])  # , ('include_in_cgpa', '=', True)

                if course_id_1:
                    course_id_1[0].course_id_2 = new_reg
                    new_reg.course_id_1 = course_id_1[0].id
            
            # elif new_registration.get('error',False):
        return reg
    
    def register_cross_course_office(self, primary_class_id, term_id, st_term, course_type, date_effective):
        alternate_id = course_id_1 = False
        course_id = primary_class_id.course_id
        
        new_registration = self.register_course(term_id, course_id, st_term, primary_class_id, date_effective)
        if new_registration.get('reg', False):
            new_reg = new_registration.get('reg')
            new_reg.course_type = course_type
    
            if course_type in ('additional', 'minor'):
                new_reg.include_in_cgpa = False
        
            elif course_type == 'alternate':
                if alternate_id and alternate_id.type == 'grade':
                    course_id_1 = self.env['odoocms.student.course'].search([
                        ('course_id', '=', alternate_id.catalogue_id.id), ('student_id', '=', self.id)
                    ])
            else:
                course_id_1 = self.env['odoocms.student.course'].search([
                    ('course_code', '=', primary_class_id.course_code), ('student_id', '=', self.id), ('id', '!=', new_reg.id)
                ])  # , ('include_in_cgpa', '=', True)
    
            if course_id_1:
                course_id_1[0].course_id_2 = new_reg
                new_reg.course_id_1 = course_id_1[0].id
            
        return new_registration
    
    def register_new_course(self, line, term_id, st_term, date_effective):
        alternate_id = course_id_1 = False
        primary_class_id = line.primary_class_id.sudo()
        course_id = primary_class_id.course_id
        new_reg = self.env['odoocms.student.course']
        
        if line.scope == 'cross' and not line.cross_id:
            data = {
                'student_id': self.id,
                'primary_class_id': line.primary_class_id.id,
                'course_type': line.course_type,
                'registration_line_id': line.id,
            }
            cross_id = self.env['odoocms.course.registration.cross'].create(data)
            line.cross_id = cross_id.id
            line.cross_id.action_submit()
        
        else:
            new_registration = self.register_course(term_id, course_id, st_term, primary_class_id, date_effective)
            if new_registration.get('reg', False):
                new_reg = new_registration.get('reg')
                new_reg.course_type = line.course_type
                
                if line.course_type in ('additional', 'minor'):
                    new_reg.include_in_cgpa = False
            
                elif line.course_type == 'alternate':
                    if alternate_id and alternate_id.type == 'grade':
                        course_id_1 = self.env['odoocms.student.course'].search([
                            ('course_id', '=', alternate_id.catalogue_id.id), ('student_id', '=', self.id)
                        ])
                else:
                    course_id_1 = self.env['odoocms.student.course'].search([
                        ('course_code', '=', primary_class_id.course_code), ('student_id', '=', self.id), ('id', '!=', new_reg.id)
                    ])  # , ('include_in_cgpa', '=', True)
        
                if course_id_1:
                    course_id_1[0].course_id_2 = new_reg
                    new_reg.course_id_1 = course_id_1[0].id
    
                line.write({
                    'state': 'approved',
                    'student_course_id': new_reg.id,
                })
                return {'reg': new_reg}
            
            elif new_registration.get('error', False):
                return new_registration
    
    def register_course(self, term, course_id, st_term, primary_class_id, date_effective, tag = False):
        if course_id:
            registration_id = self.env['odoocms.student.course'].search([
                ('student_id', '=', self.id), ('term_id', '=', term.id),
                ('course_id', '=', course_id.id)])
        
            if not primary_class_id:
                primary_class_id = self.env['odoocms.class.primary'].search([
                    ('section_id', '=', self.section_id.id), ('course_id', '=', course_id.id),
                    ('term_id', '=', term.id)])
            
                if not primary_class_id:
                    return {'error':
                            """Primary Class not defined for Course: %s \n Section: %s \n Batch: %s""" % (
                                course_id.name, self.section_id.name, self.batch_id.name)
                    }
    
        if primary_class_id and not registration_id:
            registration_id = self.env['odoocms.student.course'].search([
                ('student_id', '=', self.id), ('term_id', '=', term.id),
                ('course_id', '=', primary_class_id.study_scheme_line_id.course_id.id)])

        if registration_id:
            # if not registration_id.student_term_id:
            #     registration_id.student_term_id = st_term
            return {'reg':registration_id}

        if not primary_class_id.strength or primary_class_id.strength < 1:
            return {'error': "Primary Class Strength is not defined!"}
        elif primary_class_id.student_count >= primary_class_id.strength:
            return {'error': "Primary Class Strength is fulfilled!"}
        else:
            component_ids = []
            for component in primary_class_id.class_ids:
                component_data = {
                    'student_id': self.id,
                    'class_id': component.id,
                    'semester_id': self.semester_id.id,
                    'term_id': term.id,
                    'weightage': component.weightage,
                }
                component_ids.append((0, 0, component_data))
                
            data = {
                'student_id': self.id,
                'term_id': term.id,
                'semester_id': self.semester_id.id,
                'course_id': course_id.id,
                'primary_class_id': primary_class_id.id,
                'student_term_id': st_term.id,
                'credits': primary_class_id.credits,
                'course_code': primary_class_id.course_code or primary_class_id.course_id.code,
                'course_name': primary_class_id.course_name or primary_class_id.course_id.name,
                'tag': tag or "-",
                'date_effective': date_effective,
                'component_ids': component_ids,
            }
            registration_id = self.env['odoocms.student.course'].create(data)
            for component in registration_id.component_ids:
                registration_id.add_attendance(component, date_effective)
            
            return {'reg': registration_id}

    def _prereq_satisfy(self, pre_courses, operator='and'):
        pass
    
    def prereq_satisfy(self, class_id):
        prereq = True
        if class_id.study_scheme_line_id:
            if not self._prereq_satisfy(class_id.study_scheme_line_id.prereq_ids, class_id.study_scheme_line_id.prereq_operator):
                prereq = False
        elif class_id.course_id:
            if not self._prereq_satisfy(class_id.course_id.prereq_ids.mapped('course_id'), class_id.course_id.prereq_operator):
                prereq = False
        return prereq
    
    def prereq_apply(self, class_ids):
        for class_id in class_ids:
            prereq = self.prereq_satisfy(class_id)
            if not prereq:
                class_ids -= class_id
        return class_ids

    def get_offered_classes(self, program_domain, course_ids, new_term, portal):
        domain = program_domain
        domain = expression.AND([safe_eval(domain), [('term_id', '=', new_term.id)]]) if domain else [('term_id', '=', new_term.id)]
        if portal:
            domain = expression.AND([domain, [('self_enrollment', '=', True)]])
    
        class_ids = self.env['odoocms.class.primary'].search(domain).filtered(lambda l: l.course_id.id in course_ids.ids)
        return class_ids
    
    def get_possible_classes(self, new_term, portal=False):
        comp_class_ids = elec_class_ids = additional_class_ids = alternate_class_ids = minor_class_ids = False
        if "NewId" in str(self.id) and self._origin:
            student = self._origin
        else:
            student = self
        request_ids = self.env['odoocms.course.registration'].search(
            [('student_id', '=', student.id), ('state', 'in', ('draft', 'submit'))])
        no_registration_tags = self.env['ir.config_parameter'].sudo().get_param('odoocms_registration.no_registration_tags')
        no_new_reg = (student.tag_ids and no_registration_tags and \
            any(tag.code in no_registration_tags.replace('_', ' ').split(',') for tag in student.tag_ids) or False)
        st_term = student.enroll_term_ids.filtered(lambda l: l.term_id == new_term)
        if student.state != 'enroll' or (st_term and st_term.state not in ('draft','current')):
            return {
                'comp_class_ids': comp_class_ids,
                'elec_class_ids': elec_class_ids,
                'repeat_class_ids': False,
                'improve_class_ids': False,
                'additional_class_ids': additional_class_ids,
                'alternate_class_ids': alternate_class_ids,
                'minor_class_ids': minor_class_ids,
                'request_class_ids': request_ids,
            }

        # Registered Courses in all Prev Terms
        registered_student_course_ids = student.enrolled_course_ids  # All states
        registered_course_ids = registered_student_course_ids.mapped('course_id')
        
        
        if not no_new_reg:
            # All Compulsory - Less Registered Courses
            comp_course_ids = student.study_scheme_id.line_ids.filtered(lambda l: l.course_type == 'compulsory').mapped('course_id')
            comp_course_ids -= registered_course_ids
            
            # Offered Classes of remaining Courses with applied domain criteria
            comp_class_ids = self.get_offered_classes(student.program_id.registration_domain, comp_course_ids, new_term, portal)
            comp_class_ids = student.prereq_apply(comp_class_ids)
    
            # Less Alternate & with Pending Requests
            alt_course_ids = student.alternate_ids.filtered(lambda l: l.state == 'approve').mapped('course_id')
            request_course_ids = request_ids.mapped('compulsory_course_ids').mapped('course_id')
            minus_course_ids = alt_course_ids + request_course_ids
            minus_class_ids = comp_class_ids.filtered(lambda l: l.course_id.id in minus_course_ids.ids)
            comp_class_ids -= minus_class_ids
    
            # Additional Temporarily Check
            comp_class_ids = comp_class_ids.filtered(lambda l: l.course_id.id not in registered_course_ids.ids)

     
            # All Elective - Less Registered Courses
            elec_course_ids = student.study_scheme_id.line_ids.filtered(lambda l: l.course_type in ('elective')).mapped('course_id')
            elec_course_ids =  elec_course_ids - registered_course_ids
    
            elec_class_ids = self.get_offered_classes(student.program_id.elec_registration_domain, elec_course_ids, new_term, portal)
            elec_class_ids = student.prereq_apply(elec_class_ids)
    
            # Less Alternate & with Pending Requests
            alt_course_ids = student.alternate_ids.filtered(lambda l: l.state == 'approve').mapped('course_id')
            request_course_ids = request_ids.mapped('elective_course_ids').mapped('course_id')
            minor_course_ids = student.minor_scheme_id.line_ids.mapped('course_id')
            minus_course_ids = alt_course_ids + request_course_ids + minor_course_ids
            minus_class_ids = elec_class_ids.filtered(lambda l: l.course_id.id in minus_course_ids.ids)
            elec_class_ids -= minus_class_ids
       
            # ******** Additional ************
            # Student Scheme Courses + Add already Registered Courses
            all_course_ids = student.study_scheme_id.line_ids.mapped('course_id') + registered_course_ids
    
            # additional_class_ids = self.get_offered_classes(student.program_id.additional_registration_domain, elec_scheme_line_ids, new_term, portal)
            additional_domain = student.program_id.additional_registration_domain
            additional_domain = expression.AND([safe_eval(additional_domain), [('term_id', '=', new_term.id)]]) if additional_domain else [('term_id', '=', new_term.id)]
            if portal:
                additional_domain = expression.AND([additional_domain, [('self_enrollment','=',True)]])
                
            additional_class_ids = self.env['odoocms.class.primary'].search(additional_domain).filtered(
                lambda l: l.course_id.id not in all_course_ids.ids)
            additional_class_ids = student.prereq_apply(additional_class_ids)
            
            # Less Alternate & with Pending Requests
            request_ids2 = (request_ids.mapped('compulsory_course_ids') + request_ids.mapped('elective_course_ids') + \
                            request_ids.mapped('additional_course_ids') + request_ids.mapped('alternate_course_ids') + \
                            request_ids.mapped('minor_course_ids'))
            
            alt_course_ids = student.alternate_ids.filtered(lambda l: l.state == 'approve').mapped('alternate_course_id')
            request_course_ids = request_ids2.mapped('course_id')
            minor_course_ids = student.minor_scheme_id.line_ids.mapped('course_id')
            minus_course_ids = alt_course_ids + request_course_ids + minor_course_ids
            minus_class_ids = additional_class_ids.filtered(lambda l: l.course_id.id in minus_course_ids.ids)
            additional_class_ids -= minus_class_ids

            # All Alternate - less Studied
            alt_course_ids = student.alternate_ids.filtered(lambda l: l.state == 'approve').mapped('alternate_course_id')
            alt_course_ids = alt_course_ids - registered_course_ids

            # Offered Classes of Alternate Courses with applied domain criteria
            alt_domain = student.program_id.registration_domain
            alt_domain = expression.AND([safe_eval(alt_domain), [('term_id', '=', new_term.id)]]) if alt_domain else [('term_id', '=', new_term.id)]
            if portal:
                alt_domain = expression.AND([alt_domain, [('self_enrollment', '=', True)]])

            alternate_class_ids = self.env['odoocms.class.primary'].search(alt_domain).filtered(
                lambda l: l.course_id.id in alt_course_ids.ids)
            alternate_class_ids = student.prereq_apply(alternate_class_ids)

            # Less with Pending Requests
            less_request_class_ids = alternate_class_ids.filtered(
                lambda l: l.course_id.id in request_ids.mapped('alternate_course_ids').mapped('course_id').ids)
            alternate_class_ids -= less_request_class_ids

            # Minor Courses
            # Registered Courses in all Prev Terms
            registered_minor_course_ids = student.enrolled_course_ids.filtered(lambda l: l.course_type == 'minor').mapped('course_id')

            # All Minor - Less Registered Courses
            minor_course_ids = student.minor_scheme_id.line_ids.mapped('course_id')
            minor_course_ids -= registered_minor_course_ids

            # Offered Classes of remaining Courses with applied domain criteria
            minor_class_ids = self.get_offered_classes(student.program_id.minor_registration_domain, minor_course_ids, new_term, portal)
            minor_class_ids = student.prereq_apply(minor_class_ids)

            # Less Alternate & with Pending Requests
            alt_course_ids = student.alternate_ids.filtered(lambda l: l.state == 'approve').mapped('course_id')
            request_course_ids = request_ids.mapped('minor_course_ids').mapped('course_id')
            minus_course_ids = alt_course_ids + request_course_ids
            minus_class_ids = minor_class_ids.filtered(lambda l: l.course_id.id in minus_course_ids.ids)
            minor_class_ids -= minus_class_ids
        
        # Failed and Repeat Classes are separately handled because some universities are allowing a course to improve for specific number of time
        # Though we merge them at repeat_class_ids
        repeat_grades = self.env['ir.config_parameter'].sudo().get_param('odoocms.failed_grades')
        repeat_course_ids = student.result_course_ids.filtered(
            lambda l: l.grade in repeat_grades.replace(' ','').split(',')).mapped('course_id')

        if portal:
            repeat_class_ids = new_term.primary_class_ids.filtered(lambda l: l.course_id.id in repeat_course_ids.ids and l.self_enrollment==True)
        else:
            repeat_class_ids = new_term.primary_class_ids.filtered(lambda l: l.course_id.id in repeat_course_ids.ids)

        # Less with Pending Requests
        less_request_class_ids = repeat_class_ids.filtered(
            lambda l: l.course_id.id in request_ids.mapped('repeat_course_ids').mapped('course_id').ids)
        repeat_class_ids -= less_request_class_ids
        
        
        improve_grades_allowed = self.env['ir.config_parameter'].sudo().get_param('odoocms.repeat_grades_allowed')
        improve_grades_allowed_time = self.env['ir.config_parameter'].sudo().get_param('odoocms.repeat_grades_allowed_time')
        
        # #X-Final Students Repeat time allowed
        # if student.semester_id.number > 8:
        #     x_st_repeat_grades_allowed_time = self.env['ir.config_parameter'].sudo().get_param('odoocms.x_st_repeat_grades_allowed_time')
        #     repeat_grades_allowed_time = x_st_repeat_grades_allowed_time or 2
        
        repeat_grades_allowed_no = self.env['ir.config_parameter'].sudo().get_param('odoocms.repeat_grades_allowed_no')
        improve_course_ids = student.result_course_ids.filtered(
            lambda l: l.grade in improve_grades_allowed.replace(' ','').split(',')).mapped('course_id')

        if portal:
            improve_class_ids = new_term.primary_class_ids.filtered(lambda l: l.course_id.id in improve_course_ids.ids and l.self_enrollment==True)
        else:
            improve_class_ids = new_term.primary_class_ids.filtered(lambda l: l.course_id.id in improve_course_ids.ids)

        # Less with Pending Requests
        less_request_class_ids = improve_class_ids.filtered(
            lambda l: l.course_id.id in request_ids.mapped('improve_course_ids').mapped('course_id').ids)
        improve_class_ids -= less_request_class_ids
        #repeat_class_ids -= student.course_ids.mapped('primary_class_id') i think no need of it
        if student.repeat_courses_count > student.career_id.improve_course_limit:
            improve_class_ids = False
        
        
        # minimum_cgpa = 2
        #
        # # This condition is for CGPA Requirement
        # if not(student.semester_id.number >= 8 and student.cgpa < minimum_cgpa):
        #     for line in repeat_course_ids:
        #         # if len(student.result_course_ids.filtered(
        #         #         lambda l: l.course_id.course_id.id == line.id and l.grade not in failed_grades.replace(' ','').split(
        #         #             ','))) >= int(repeat_grades_allowed_no):
        #         if len(student.result_course_ids.filtered(
        #                 lambda l: l.course_id.course_id.id == line.id and l.grade not in failed_grades.replace(' ','').split(
        #                     ','))) > int(repeat_grades_allowed_no)+1 :
        #             repeat_course_ids -= line
        #
        #
        #     for line in repeat_course_ids:
        #         if len(student.result_course_ids.filtered(
        #                 lambda l: l.course_id.course_id.id == line.id and l.grade not in failed_grades.replace(' ','').split(',')
        #                           and l.semester_id.number < (
        #                                   student.semester_id.number - int(repeat_grades_allowed_time)))) > 0 :
        #             repeat_course_ids -= line
        
        
        
        
        # if (new_term.type == 'summer' and reregister_allow_in_summer == 'False' ) or (new_term.type == 'winter' and reregister_allow_in_winter == 'False' ):
        #     offered_r = self.env['odoocms.class.primary']
        #
        #
        # if new_term.type in ('summer','winter'):
        #     additional_class_ids = self.env['odoocms.class.primary']

        return {
            'comp_class_ids': comp_class_ids,
            'elec_class_ids': elec_class_ids,
            'repeat_class_ids': repeat_class_ids,
            'improve_class_ids': improve_class_ids,
            'additional_class_ids': additional_class_ids,
            'alternate_class_ids': alternate_class_ids,
            'minor_class_ids': minor_class_ids,
            'request_class_ids': request_ids,
        }

    def fill_portal_cards(self,course, course_type):
        card = {
            'class': course,
            'course_type': course_type,
            'course_id': course.course_id.id,
        }
        if self.batch_id.id == course.batch_id.id:
            card['scope'] = 'batch'
        elif self.program_id.id == course.program_id.id:
            card['scope'] = 'program'
            card['program_id'] = course.program_id.id
        elif self.institute_id.id == course.institute_id.id:
            card['scope'] = 'institute'
            card['institute_id'] = course.institute_id.id
        else:
            card['scope'] = 'cross'
        return card
        
    def get_portal_classes(self, term_id, course_registration):
        classes = self.get_possible_classes(term_id, portal=True)
        cards = {
            'batch': [],
            'program': [],
            'institute': [],
            'cross': [],
        }
        if classes['comp_class_ids']:
            for course in classes['comp_class_ids']:
                if course_registration and len(course_registration.line_ids.filtered(lambda l: l.course_code == course.course_code)) > 0:
                    continue
                card = self.fill_portal_cards(course,'compulsory')
                cards[card['scope']].append(card)
        if classes['elec_class_ids']:
            for course in classes['elec_class_ids']:
                if course_registration and len(course_registration.line_ids.filtered(lambda l: l.course_code == course.course_code)) > 0:
                    continue
                card = self.fill_portal_cards(course,'elective')
                cards[card['scope']].append(card)
        if classes['repeat_class_ids']:
            for course in classes['repeat_class_ids']:
                if course_registration and len(course_registration.line_ids.filtered(lambda l: l.course_code == course.course_code)) > 0:
                    continue
                card = self.fill_portal_cards(course, 'repeat')
                cards[card['scope']].append(card)
        if classes['improve_class_ids']:
            for course in classes['improve_class_ids']:
                if course_registration and len(course_registration.line_ids.filtered(lambda l: l.course_code == course.course_code)) > 0:
                    continue
                card = self.fill_portal_cards(course, 'improve')
                cards[card['scope']].append(card)
        if classes['additional_class_ids']:
            for course in classes['additional_class_ids']:
                if course_registration and len(course_registration.line_ids.filtered(lambda l: l.course_code == course.course_code)) > 0:
                    continue
                card = self.fill_portal_cards(course, 'additional')
                cards[card['scope']].append(card)
        if classes['alternate_class_ids']:
            for course in classes['alternate_class_ids']:
                if course_registration and len(course_registration.line_ids.filtered(lambda l: l.course_code == course.course_code)) > 0:
                    continue
                card = self.fill_portal_cards(course, 'alternate')
                cards[card['scope']].append(card)
        if classes['minor_class_ids']:
            for course in classes['minor_class_ids']:
                if course_registration and len(course_registration.line_ids.filtered(lambda l: l.course_code == course.course_code)) > 0:
                    continue
                card = self.fill_portal_cards(course, 'minor')
                cards[card['scope']].append(card)
        
        return cards
    
        
class OdooCMSAcademicTerm(models.Model):
    _inherit = 'odoocms.academic.term'

    course_ids = fields.One2many('odoocms.student.course', 'term_id', 'Courses')
