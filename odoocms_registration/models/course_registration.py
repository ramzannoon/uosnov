
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.osv import expression
import pdb


class OdooCMSCourseRegistration(models.Model):
    _name = "odoocms.course.registration"
    _description = 'Course Registration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    SUBMITTED_STATES = {
        'submit': [('readonly', True)],
        'part_approved': [('readonly', True)],
        'approved': [('readonly', True)],
        'rejected': [('readonly', True)],
    }
    READONLY_STATES = {
        'part_approved': [('readonly', True)],
        'approved': [('readonly', True)],
        'rejected': [('readonly', True)],
    }

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    student_id = fields.Many2one('odoocms.student', 'Student', required=True, states=SUBMITTED_STATES, tracking=True)
    program_id = fields.Many2one('odoocms.program', 'Program', related='student_id.program_id',store=True)
    term_id = fields.Many2one('odoocms.academic.term', 'Term', required=True, states=SUBMITTED_STATES, tracking=True)
    last_date = fields.Date(string = 'Registration Last Date', compute = 'get_registration_last_date', readonly= True, store = True)
    reg_date = fields.Date('Date', default = (fields.Date.today()),  readonly=True)
    date_effective = fields.Date('Effective Date', default = (fields.Date.today()),states=READONLY_STATES)
    source = fields.Selection([
        ('office','Back Office'),
        ('portal','Portal'),
        ('bulk','Bulk Process'),
        ('bulk2','Bulk Process2'),
    ],'Source',default='office',readonly=True, copy=False)
    bulk_id = fields.Many2one('odoocms.course.registration.bulk','Bulk ID')
    bulk_id2 = fields.Many2one('odoocms.course.registration.bulk2','Bulk ID')
    new_courses = fields.Boolean(compute='_can_enroll_new_courses',store=True)
    override_max_limit = fields.Boolean('Override Maximum Limit?',default=False,states=READONLY_STATES, tracking=True)

    registered_course_ids = fields.Many2many('odoocms.class.primary', 'class_course_registered_rel', 'register_id', 'primary_class_id',
            string="Registered Courses", states=READONLY_STATES, tracking=True,compute='get_registered_courses',store=True,)
    compulsory_course_ids = fields.Many2many('odoocms.class.primary', 'class_course_compulsory_rel', 'register_id', 'primary_class_id',
            string="Compulsory Courses", states=READONLY_STATES, tracking=True)
    elective_course_ids = fields.Many2many('odoocms.class.primary', 'class_course_elective_rel', 'register_id', 'primary_class_id',
            string="Elective Courses", states=READONLY_STATES, tracking=True)
    repeat_course_ids = fields.Many2many('odoocms.class.primary', 'class_course_failed_rel', 'register_id', 'primary_class_id',
            string="Failed Courses", states=READONLY_STATES, tracking=True)
    improve_course_ids = fields.Many2many('odoocms.class.primary', 'class_course_improve_rel', 'register_id', 'primary_class_id',
            string="Repeat for Improvement Courses", states=READONLY_STATES, tracking=True)
    additional_course_ids = fields.Many2many('odoocms.class.primary', 'class_course_additional_rel', 'register_id', 'primary_class_id',
            string="Additional Courses", states=READONLY_STATES, tracking=True)
    alternate_course_ids = fields.Many2many('odoocms.class.primary', 'class_course_alternate_rel', 'register_id', 'primary_class_id',
                                             string="Alternate Courses", states=READONLY_STATES, tracking=True)
    minor_course_ids = fields.Many2many('odoocms.class.primary', 'class_course_minor_rel', 'register_id', 'primary_class_id',
                                            string="Minor Courses", states=READONLY_STATES, tracking=True)
    other_request_id = fields.Many2one('odoocms.course.registration','Other Pending Request',readonly=True, store=True)
    # invoice_id = fields.Many2one('account.move','Invoice')
    # invoice_status = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('unpaid', 'Unpaid'),
    #     ('open', 'Open'),
    #     ('in_payment', 'In Payment'),
    #     ('paid', 'Paid'),
    #     ('cancel', 'Cancelled')], related='invoice_id.state', tracking=True)
    can_approve = fields.Boolean('Can Approve',compute='_can_approve', tracking=True)
    # can_invoice = fields.Boolean('Can Invoice', compute='_can_invoice', tracking=True)
    error = fields.Text('Error')
    limit_error = fields.Boolean('Over Limit',default=False)
    limit_error_text = fields.Text(default='')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('error','Error'),
        ('part_approved','Partially Approved'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')], default='draft', string='Status', copy=False, tracking=True)
    
    comp_domain = fields.Many2many('odoocms.class.primary',compute='_get_courses_domain')
    elec_domain = fields.Many2many('odoocms.class.primary',compute='_get_courses_domain')
    repeat_domain = fields.Many2many('odoocms.class.primary',compute='_get_courses_domain')
    improve_domain = fields.Many2many('odoocms.class.primary',compute='_get_courses_domain')
    additional_domain = fields.Many2many('odoocms.class.primary', compute='_get_courses_domain')
    alternate_domain = fields.Many2many('odoocms.class.primary', compute='_get_courses_domain')
    minor_domain = fields.Many2many('odoocms.class.primary', compute='_get_courses_domain')

    repeat_domain_bool = fields.Boolean(compute='_get_courses_domain')
    improve_domain_bool = fields.Boolean(compute='_get_courses_domain')
    additional_domain_bool = fields.Boolean(compute='_get_courses_domain')
    alternate_domain_bool = fields.Boolean(compute='_get_courses_domain')
    minor_domain_bool = fields.Boolean(compute='_get_courses_domain')

    line_ids = fields.One2many('odoocms.course.registration.line','registration_id','Course to Enroll',domain=[('state','!=','error')])
    failed_line_ids = fields.One2many('odoocms.course.registration.line', 'registration_id', 'Failed to Enroll', domain=[('state', '=', 'error')])
    cnt = fields.Integer('Count')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('odoocms.course.registration') or _('New')
        result = super().create(vals)
        return result
    
    @api.depends('student_id', 'term_id')
    def get_registered_courses(self):
        for rec in self:
            rec.registered_course_ids = False
            if rec.student_id and rec.term_id:
                registered_class_ids = rec.student_id.enrolled_course_ids.filtered(
                    lambda l: l.term_id.id == rec.term_id.id).mapped('primary_class_id')
                rec.registered_course_ids = [(6, 0, registered_class_ids.ids)]
                domain = [('student_id', '=', rec.student_id.id), ('state', 'in', ('draft', 'submit'))]

                if "NewId" in str(rec.id) and rec._origin:
                    domain = expression.AND([domain, [('id', '!=', rec._origin.id)]])
                elif rec.id:
                    domain = expression.AND([domain, [('id', '!=', rec.id)]])
                    
                request_class_ids = self.env['odoocms.course.registration'].search(domain)
                rec.other_request_id = request_class_ids and request_class_ids[0] or False
                
    @api.depends('student_id')
    def _can_enroll_new_courses(self):
        for rec in self:
            can_enroll = True
            student_tags = rec.student_id.tag_ids.mapped('name')
            if 'Deferred' in student_tags or 'Extra' in student_tags or 'Semester Deferment' in student_tags:
                can_enroll = False
            self.new_courses = can_enroll

    @api.onchange('term_id', 'student_id')
    def _can_register(self):
        if self.term_id and self.student_id and not self.student_id.batch_id.can_apply('enrollment',self.term_id):
            self.error = 'Date Over'
        else:
            self.error = None
            
    def _can_approve(self):
        allow_re_reg_wo_fee = self.env['ir.config_parameter'].sudo().get_param('odoocms_registration.allow_re_reg_wo_fee')
        self.can_approve = True
        # if allow_re_reg_wo_fee == False or allow_re_reg_wo_fee == 'False':
        #     can_approve = False
        #     if self.state == 'submit':
        #         if self.compulsory_course_ids or self.elective_course_ids or self.additional_course_ids:
        #             can_approve = True
        #         elif self.repeat_course_ids:
        #             if self.invoice_id and self.invoice_status == 'paid':
        #                 can_approve = True
        #     if self.state == 'part_approved':
        #        if self.repeat_course_ids:
        #             if self.invoice_id and self.invoice_status == 'paid':
        #                 can_approve = True
        #     self.can_approve = can_approve
        # else:
        #     self.can_approve = True

    # def _can_invoice(self):
    #     allow_re_reg_wo_fee = self.env['ir.config_parameter'].sudo().get_param('odoocms_registration.allow_re_reg_wo_fee')
    #
    #     if allow_re_reg_wo_fee == False or allow_re_reg_wo_fee == 'False':
    #         can_invoice = False
    #         if self.state in ('submit','part_approved'):
    #             if self.repeat_course_ids:
    #                 if not self.invoice_id:
    #                     can_invoice = True
    #         self.can_invoice = can_invoice
    #     else:
    #         can_invoice = False
    #
        
    @api.depends('student_id','term_id')
    def _get_courses_domain(self):
        self.comp_domain = self.elec_domain = self.repeat_domain = self.improve_domain = self.additional_domain = self.alternate_domain = self.minor_domain = False
        self.minor_domain_bool = self.repeat_domain_bool = self.improve_domain_bool = self.additional_domain_bool = self.alternate_domain_bool = False
        if self.student_id and self.term_id:
            classes = self.student_id.get_possible_classes(self.term_id)   # [0]
            
            student_tags = self.student_id.tag_ids.mapped('name')
            if 'Deferred' in student_tags or 'Extra' in student_tags or 'Semester Deferment' in student_tags:
                self.comp_domain = []
                self.elec_domain = []
            else:
                self.comp_domain = [(6, 0, classes['comp_class_ids'] and len(classes['comp_class_ids']) > 0 and classes['comp_class_ids'].ids or [])]
                self.elec_domain = [(6, 0, classes['elec_class_ids'] and len(classes['elec_class_ids']) > 0 and classes['elec_class_ids'].ids or [])]
            
            if classes['repeat_class_ids'] and len(classes['repeat_class_ids']) > 0:
                self.repeat_domain = [(6, 0, classes['repeat_class_ids'].ids)]
                self.repeat_domain_bool = True
            
            if classes['improve_class_ids'] and len(classes['improve_class_ids']) > 0:
                self.improve_domain = [(6, 0, classes['improve_class_ids'].ids)]
                self.improve_domain_bool = True
                
            if classes['additional_class_ids'] and len(classes['additional_class_ids']) > 0:
                self.additional_domain = [(6, 0, classes['additional_class_ids'].ids)]
                self.additional_domain_bool = True
                
            if classes['alternate_class_ids'] and len(classes['alternate_class_ids']) > 0:
                self.alternate_domain = [(6, 0, classes['alternate_class_ids'].ids)]
                self.alternate_domain_bool = True
                
            if classes['minor_class_ids'] and len(classes['minor_class_ids']) > 0:
                self.minor_domain = [(6, 0, classes['minor_class_ids'].ids)]
                self.minor_domain_bool = True
                
            if classes['request_class_ids'] and len(classes['request_class_ids'].mapped('repeat_course_ids')) > 0:
                self.repeat_domain_bool = True
            if classes['request_class_ids'] and len(classes['request_class_ids'].mapped('improve_course_ids')) > 0:
                self.improve_domain_bool = True
            if classes['request_class_ids'] and len(classes['request_class_ids'].mapped('additional_course_ids')) > 0:
                self.additional_domain_bool = True
            if classes['request_class_ids'] and len(classes['request_class_ids'].mapped('alternate_course_ids')) > 0:
                self.alternate_domain_bool = True
            if classes['request_class_ids'] and len(classes['request_class_ids'].mapped('minor_course_ids')) > 0:
                self.minor_domain_bool = True
    
    def add_course(self, course, type):
        c1 = self.line_ids.filtered(lambda l: l.primary_class_id.id == course.id)
        if c1:
            return c1

        new_line = self.env['odoocms.course.registration.line']
        prereq = self.student_id.prereq_satisfy(course)
        
        regs = self.env['odoocms.student.course'].search([
            ('student_id', '=', self.student_id.id), ('term_id', '=', self.term_id.id), ('course_code', '=', course.course_code)
        ])
        
        if not regs:
            data = {
                'registration_id': self.id,
                'primary_class_id': course.id,
                'course_type': type,
                'batch_id': self.student_id.batch_id.id,
                'state': 'draft' if prereq else 'error',
                'error': False if prereq else 'Prereq Failed'
            }
            if self.student_id.batch_id.id == course.batch_id.id:
                data['scope'] = 'batch'
            elif self.student_id.program_id.id == course.program_id.id:
                data['scope'] = 'program'
                data['course_batch_id'] = course.batch_id.id
            elif self.student_id.institute_id.id == course.institute_id.id:
                data['scope'] = 'institute'
                data['course_program_id'] = course.program_id.id
            else:
                data['scope'] = 'cross'
                data['course_institute_id'] = course.institute_id.id
                
            new_line.create(data)
        return new_line

    def action_self_enroll_draft(self):
        for rec in self:
            rec._test_register_limit()
            
    def action_submit(self):
        for rec in self:
            if rec.source in ('office','bulk','bulk2'):
                lines = rec.line_ids
                for course in rec.compulsory_course_ids:
                    lines -= rec.add_course(course,'compulsory')
                for course in rec.elective_course_ids:
                    lines -= rec.add_course(course,'elective')
                for course in rec.repeat_course_ids:
                    lines -= rec.add_course(course,'repeat')
                for course in rec.improve_course_ids:
                    lines -= rec.add_course(course,'improve')
                for course in rec.additional_course_ids:
                    lines -= rec.add_course(course,'additional')
                for course in rec.alternate_course_ids:
                    lines -= rec.add_course(course,'alternate')
                for course in rec.minor_course_ids:
                    lines -= rec.add_course(course,'minor')
                lines.unlink()
            elif rec.source == 'portal':
                b = 5
            rec.line_ids.state = 'submit'
            rec.write({
                'state': 'submit',
                'cnt': len(rec.line_ids),
            })
            rec._test_register_limit()

    def action_reset_draft(self):
        self.line_ids.state = 'draft'
        self.state = 'draft'

    def action_reject(self):
        self.line_ids.state = 'rejected'
        self.state = 'rejected'

    def action_approve(self):
        reg = self.env['odoocms.student.course']
        st_term = self.env['odoocms.student.term']
        for rec in self:
            if not rec.line_ids:
                if not rec.bulk_id or not rec.bulk_id2:
                    raise UserError('No New Registration request is there')
                else:
                    rec.error = 'No New Registration request is there'
                    rec.state = 'error'
                    continue
                    
            # Here we will add term_line_id instead of term_id
            self._test_register_limit()
            if self.limit_error:
                return
            
            st_term = st_term.search([('student_id', '=', rec.student_id.id), ('term_id', '=', rec.term_id.id), ])
            if not st_term:
                data = {
                    'student_id': rec.student_id.id,
                    'term_id': rec.term_id.id,
                    'semester_id': rec.student_id.semester_id.id,
                }
                st_term = st_term.create(data)

            student_tags = self.student_id.tag_ids.mapped('name')
            if 'Deferred' in student_tags:
                st_term.term_type = 'defer'
            if self.student_id.state == 'extra' or 'Extra' in student_tags or 'Semester Deferment' in student_tags:
                st_term.term_type = 'extra'
                
            
            # Repeat Limit - Times
            # if (record.student_id.repeat_courses_count + len(course_ids2) ) > record.student_id.career_id.repeat_course_limit:
            #     raise UserError('Repeat course limit for %s is %s and student have already repeated for %s times.'
            #         %(record.student_id.career_id.name, str(record.student_id.career_id.repeat_course_limit), str(record.student_id.repeat_courses_count),))
           
    #         allow_re_reg_wo_fee = self.env['ir.config_parameter'].sudo().get_param('odoocms_registration.allow_re_reg_wo_fee')
            allow_re_reg_wo_fee = True
            if (allow_re_reg_wo_fee == False):   #and (record.invoice_id and record.invoice_status == 'paid'):
                reg += rec.student_id.register_courses(rec.compulsory_course_ids, rec.term_id, st_term, rec.date_effective, 'compulsory')
                reg += rec.student_id.register_courses(rec.elective_course_ids, rec.term_id, st_term, rec.date_effective, 'elective')
                reg += rec.student_id.register_courses(rec.additional_course_ids, rec.term_id, st_term, rec.date_effective, 'additional')
                reg += rec.student_id.register_courses(rec.alternate_course_ids, rec.term_id, st_term, rec.date_effective, 'alternate')
                reg += rec.student_id.register_courses(rec.minor_course_ids, rec.term_id, st_term, rec.date_effective, 'minor')

            elif allow_re_reg_wo_fee == True:
                for line in rec.line_ids:
                    new_registration = rec.student_id.register_new_course(line, rec.term_id, st_term,rec.date_effective)
                    if new_registration.get('reg',False):
                        reg += new_registration.get('reg')
                    elif new_registration.get('error',False):
                        rec.error = new_registration.get('error')
                        
            if len(reg) == len(rec.line_ids):
                rec.state = 'approved'
            elif len(reg) > 0:
                rec.state = 'part_approved'

        reg_list = reg.mapped('id')
        return {
            'domain': [('id', 'in', reg_list)],
            'name': _('Student Registration'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'odoocms.student.course',
            'view_id': False,
            # 'context': {'default_primary_class_id': self.id},
            'type': 'ir.actions.act_window'
        }
    
    def _test_register_limit(self):
        registered_courses = self.env['odoocms.student.course'].search([
            ('student_id', '=', self.student_id.id), ('term_id', '=', self.term_id.id),('grade','not in',('W','F'))])
        
        min_credits = max_credits = non_credits = repeat_credits = 0
        sum_credit = sum_non = sum_repeat = 0
        
        for course in registered_courses:
            sum_credit += course.primary_class_id.credits
            if course.course_type in ('additional','minor'):
                sum_non += course.primary_class_id.credits
            if course.course_type == 'repeat':
                sum_repeat += course.primary_class_id.credits
                
        # for course in (self.compulsory_course_ids + self.elective_course_ids + self.alternate_course_ids):
        #     sum_credit += course.credits
        #
        # for course in (self.additional_course_ids + self.minor_course_ids):
        #     sum_credit += course.credits
        #     sum_non += course.credits
        #
        # for course in (self.repeat_course_ids):
        #     sum_credit += course.credits
        #     sum_repeat += course.credits

        for course in self.line_ids: #   (self.compulsory_course_ids + self.elective_course_ids + self.alternate_course_ids):
            sum_credit += course.credits
            if course.course_type in ('additional','minor'):
                sum_non += course.credits
            if course.course_type == 'repeat':
                sum_repeat += course.credits
                
        # Allowed
        global_load = self.env['odoocms.student.registration.load'].search([
            ('type','=',self.term_id.type),('default_global','=',True)])
        if global_load:
            min_credits = global_load.min
            max_credits = global_load.max
            non_credits = global_load.non
            repeat_credits = global_load.repeat

        career_load = self.student_id.career_id.registration_load_ids.filtered(lambda l: l.type == self.term_id.type)
        if career_load:
            min_credits = career_load.min if career_load.min > 0 else min_credits
            max_credits = career_load.max if career_load.max > 0 else max_credits
            non_credits = career_load.non if career_load.non > 0 else non_credits
            repeat_credits = career_load.repeat if career_load.repeat > 0 else repeat_credits

        batch_load = self.student_id.batch_id.registration_load_ids.filtered(lambda l: l.type == self.term_id.type)
        if batch_load:
            min_credits = batch_load.min if batch_load.min > 0 else min_credits
            max_credits = batch_load.max if batch_load.max > 0 else max_credits
            non_credits = batch_load.non if batch_load.non > 0 else non_credits
            repeat_credits = batch_load.repeat if batch_load.repeat > 0 else repeat_credits

        program_load = self.student_id.program_id.registration_load_ids.filtered(lambda l: l.type == self.term_id.type)
        if program_load:
            min_credits = program_load.min if program_load.min > 0 else min_credits
            max_credits = program_load.max if program_load.max > 0 else max_credits
            non_credits = program_load.non if program_load.non > 0 else non_credits
            repeat_credits = program_load.repeat if program_load.repeat > 0 else repeat_credits
            
        student_load = self.student_id.registration_load_ids.filtered(lambda l: l.type == self.term_id.type)
        if student_load:
            min_credits = student_load.min if student_load.min > 0 else min_credits
            max_credits = student_load.max if student_load.max > 0 else max_credits
            non_credits = student_load.non if student_load.non > 0 else non_credits
            repeat_credits = student_load.repeat if student_load.repeat > 0 else repeat_credits
        
        if sum_non > non_credits:
            self.limit_error = True
            self.limit_error_text = 'Registration of (%s) Non-Credits is not Possible. Allowed limit: (%s) CH' % (sum_non, non_credits)
            
        elif sum_repeat > repeat_credits:
            self.limit_error = True
            self.limit_error_text = 'Registration of (%s) Repeat-Credits is not Possible. Allowed limit: (%s) CH' % (sum_repeat, repeat_credits)
            
        elif sum_credit > max_credits and not self.override_max_limit:
            self.limit_error = True
            self.limit_error_text = 'Registration of (%s) Credits is not Possible. Maximum Allowed limit: (%s) CH' % (sum_credit, max_credits)
        else:
            self.limit_error = False
            self.limit_error_text = ''
            

class OdooCMSCourseRegistrationLine(models.Model):
    _name = "odoocms.course.registration.line"
    _description = 'Enrollment Lines'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    registration_id = fields.Many2one('odoocms.course.registration','Registration ID')
    student_id = fields.Many2one('odoocms.student','Student',related='registration_id.student_id',store=True)
    primary_class_id = fields.Many2one('odoocms.class.primary','Primary Class', ondelete='cascade')
    course_code = fields.Char('Course Code', related='primary_class_id.course_code',store=True)
    credits = fields.Float('Credits',related='primary_class_id.credits',store=True)
    course_type = fields.Selection([
        ('compulsory','Compulsory'),('elective','Elective'),
        ('repeat','Repeat'),('improve','Improve'),('additional','Additional'),
        ('alternate','Alternate'),('minor','Minor')],'Course Type',default='compulsory'
    )
    scope = fields.Selection([
        ('batch','Batch'),('program','Program'),
        ('institute','Institute'),('cross','Cross')],'Scope',default='batch')
    
    batch_id = fields.Many2one('odoocms.batch','Student Batch')
    program_id = fields.Many2one('odoocms.program','Student Program')
    department_id = fields.Many2one('odoocms.department','Department',related='program_id.department_id',store=True)
    
    course_batch_id = fields.Many2one('odoocms.batch', 'Course Batch')
    course_program_id = fields.Many2one('odoocms.program', 'Program')
    course_institute_id = fields.Many2one('odoocms.institute', 'School')

    student_course_id = fields.Many2one('odoocms.student.course','Student Course', ondelete='cascade')
    cross_id = fields.Many2one('odoocms.course.registration.cross','Cross Request')
    error = fields.Text('Error')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('approval1', '1st Approval'),
        ('approval2', '2nd Approval'),
        ('error', 'Error'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')], default='draft', string='Status', copy=False, tracking=True)

    
class OdooCMSCourseRegistrationCross(models.Model):
    _name = "odoocms.course.registration.cross"
    _description = 'Cross Enrollment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'
    
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
        index=True, default=lambda self: _('New'))

    student_id = fields.Many2one('odoocms.student', 'Student')
    batch_id = fields.Many2one('odoocms.batch', 'Batch',related='student_id.batch_id',store=True)
    program_id = fields.Many2one('odoocms.program', 'Student Program',related='batch_id.program_id',store=True)
    department_id = fields.Many2one('odoocms.department', 'Department', related='program_id.department_id', store=True)
    
    primary_class_id = fields.Many2one('odoocms.class.primary', 'Primary Class', ondelete='restrict')
    course_code = fields.Char('Course Code', related='primary_class_id.course_code', store=True)
    credits = fields.Float('Credits', related='primary_class_id.credits', store=True)
    course_type = fields.Selection([
        ('compulsory', 'Compulsory'), ('elective', 'Elective'),
        ('repeat', 'Repeat'), ('improve', 'Improve'),('additional', 'Additional'),
        ('alternate', 'Alternate'), ('minor', 'Minor')], 'Course Type', default='compulsory'
    )
    
    course_batch_id = fields.Many2one('odoocms.batch', 'Course Batch', related='primary_class_id.batch_id', store=True)
    course_program_id = fields.Many2one('odoocms.program', 'Program', related='course_batch_id.program_id', store=True)
    course_institute_id = fields.Many2one('odoocms.institute', 'School', related='course_program_id.institute_id', store=True)

    registration_line_id = fields.Many2one('odoocms.course.registration.line', 'Registration ID')
    student_course_id = fields.Many2one('odoocms.student.course', 'Student Course',related='registration_line_id.student_course_id',store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('approval', 'Approval'),
        ('error', 'Error'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')], default='draft', string='Status', copy=False, tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('odoocms.course.registration.cross') or _('New')
            result = super().create(vals)
        return result

    def action_submit(self):
        activity = self.env.ref('odoocms_registration.mail_act_cross_registration')
        self.activity_schedule('odoocms_registration.mail_act_cross_registration', user_id=activity._get_role_users(self.sudo().program_id))
        self.registration_line_id.state = 'approval1'
        self.state = 'submit'

    def action_1st_approval(self):
        activity = self.env.ref('odoocms_registration.mail_act_cross_registration2')
        self.activity_schedule('odoocms_registration.mail_act_cross_registration2', user_id=activity._get_role_users(self.sudo().course_program_id))
        self.registration_line_id.state = 'approval2'
        self.state = 'approval'
        
    def action_approval(self):
        self = self.sudo()
        st_term = self.env['odoocms.student.term']
        st_term = st_term.search([
            ('student_id', '=', self.student_id.id),
            ('term_id', '=', self.registration_line_id.registration_id.term_id.id),
        ])
        if not st_term:
            data = {
                'student_id': self.student_id.id,
                'term_id': self.registration_line_id.registration_id.term_id.id,
                'semester_id': self.student_id.semester_id.id,
            }
            st_term = st_term.create(data)
            
        new_registration = self.student_id.register_new_course(
            self.registration_line_id, self.registration_line_id.registration_id.term_id, st_term, self.registration_line_id.registration_id.date_effective)
        if new_registration.get('reg', False):
            self.registration_line_id.state = 'approved'
            self.state = 'approved'
        
    def action_cancel(self):
        self.registration_line_id.state = 'rejected'
        self.state = 'rejected'


class OdooCMSCourseRegistrationCrossOffice(models.Model):
    _name = "odoocms.course.registration.cross.office"
    _description = 'Cross Enrollment - Office'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    READONLY_STATES = {
        'submit': [('readonly', True)],
        'done': [('readonly', True)],
        'rejected': [('readonly', True)],
    }
    
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    reg = fields.Char('Registration',required=True,states=READONLY_STATES)
    student_id = fields.Many2one('odoocms.student', 'Student',readonly=True, compute='_get_student',store=True)
    batch_id = fields.Many2one('odoocms.batch', 'Batch', related='student_id.batch_id', store=True)
    program_id = fields.Many2one('odoocms.program', 'Student Program', related='batch_id.program_id', store=True)
    department_id = fields.Many2one('odoocms.department', 'Department', related='program_id.department_id', store=True)

    term_id = fields.Many2one('odoocms.academic.term', 'Term', required=True, states=READONLY_STATES)
    primary_class_id = fields.Many2one('odoocms.class.primary', 'Primary Class', ondelete='restrict',states=READONLY_STATES)
    course_code = fields.Char('Course Code', related='primary_class_id.course_code', store=True)
    credits = fields.Float('Credits', related='primary_class_id.credits', store=True)
    course_type = fields.Selection([
        ('compulsory', 'Compulsory'), ('elective', 'Elective'),
        ('repeat', 'Repeat'), ('improve', 'Improve'), ('additional', 'Additional'),
        ('alternate', 'Alternate'), ('minor', 'Minor')], 'Course Type', default='compulsory', states=READONLY_STATES
    )

    course_batch_id = fields.Many2one('odoocms.batch', 'Course Batch', related='primary_class_id.batch_id', store=True)
    course_program_id = fields.Many2one('odoocms.program', 'Program', related='course_batch_id.program_id', store=True)
    course_institute_id = fields.Many2one('odoocms.institute', 'School', related='course_program_id.institute_id', store=True)

    student_course_id = fields.Many2one('odoocms.student.course', 'Student Course',readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('error', 'Error'),
        ('done', 'Done'),
        ('rejected', 'Rejected')], default='draft', string='Status', copy=False, tracking=True)

    reg_date = fields.Date('Date', default=(fields.Date.today()), readonly=True)
    date_effective = fields.Date('Effective Date', default=(fields.Date.today()),states=READONLY_STATES)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('odoocms.course.registration.cross.office') or _('New')
            result = super().create(vals)
        return result

    @api.depends('reg')
    def _get_student(self):
        if self.reg:
            student = self.env['odoocms.student'].sudo().search([('code','=',self.reg)])
            if student and len(student) == 1:
                self.student_id = student.id
    
    def action_submit(self):
        self.state = 'submit'
        
    def action_register(self):
        st_term = self.env['odoocms.student.term'].sudo()
        student = self.student_id.sudo()
        st_term = st_term.search([
            ('student_id', '=', student.id),
            ('term_id', '=', self.term_id.id),
        ])
        if not st_term:
            data = {
                'student_id': student.id,
                'term_id': self.term_id.id,
                'semester_id': student.semester_id.id,
            }
            st_term = st_term.create(data)
    
        new_registration = student.register_cross_course_office(self.primary_class_id, self.term_id, st_term, self.course_type, self.date_effective)
        if new_registration.get('reg', False):
            new_reg = new_registration.get('reg')
            self.student_course_id = new_reg.id
            self.state = 'done'
        elif new_registration.get('error', False):
            raise UserError(new_registration.get('error'))
        
    def action_cancel(self):
        self.state = 'rejected'
    
    # Remarked lines of Master table
    # @api.onchange('student_id','term_id')
    # def get_subjects(self):
    #     res = {}
    #     record = self
    #     if record.student_id and record.term_id:
    #         student = record.student_id
    #         new_semester = record.term_id
    #
    #         record.compulsory_course_ids = False
    #         record.elective_course_ids = False
    #         record.repeat_course_ids = False
    #
    #         # If Student does not have any academic semester
    #         if not student.term_id:
    #             semester_scheme = self.env['odoocms.semester.scheme'].search([
    #                 ('academic_session_id', '=', student.academic_session_id.id),
    #                 ('term_id', '=', new_semester.id)
    #             ])
    #             if not semester_scheme:
    #                 raise ValidationError("""Semester Scheme not defined for Session: %s \n Term: %s \n Student: %s """ % (
    #                     student.academic_session_id.name, new_semester.name, student.name))
    #             if semester_scheme.semester_id.number > 1:
    #                 raise ValidationError("""Direct Registration is not possible for Semester: %s \n Term: %s \n Student: %s """ % (
    #                     semester_scheme.semester_id.name, new_semester.name, student.name))
    #
    #             # student.term_id = semester_scheme.term_id.id
    #             # student.semester_id = semester_scheme.semester_id.id
    #
    #         # If Student Academic Semester and reistration semester are same
    #         elif student.term_id.id == new_semester.id:
    #             semester_scheme = self.env['odoocms.semester.scheme'].search([
    #                 ('academic_session_id', '=', student.academic_session_id.id),
    #                 ('term_id', '=', new_semester.id)
    #             ])
    #             if not semester_scheme:
    #                 raise ValidationError("""Semester Scheme not defined for Session: %s \n Term: %s \n Student: %s """ % (
    #                     student.academic_session_id.name, new_semester.name, student.name))
    #
    #             if not student.semester_id:
    #                 if semester_scheme.semester_id.number > 1:
    #                     raise ValidationError("""Direct Registration is not possible for Semester: %s \n Term: %s \n Student: %s """ % (
    #                         semester_scheme.semester_id.name, new_semester.name, student.name))
    #                 # student.semester_id = semester_scheme.semester_id.id
    #
    #         # If Student Academic Semester and reistration semester are not same
    #         elif student.term_id.id != new_semester.id:
    #             semester_scheme = self.env['odoocms.semester.scheme'].search([
    #                 ('academic_session_id', '=', student.academic_session_id.id),
    #                 ('term_id', '=', new_semester.id)
    #             ])
    #             if not semester_scheme:
    #                 raise ValidationError("""Semester Scheme not defined for Session: %s \n Term: %s \n Student: %s """ % (
    #                     student.academic_session_id.name, new_semester.name, student.name))
    #
    #             if not student.semester_id:
    #                 raise ValidationError("""Direct Promotion is not possible for Semester: %s \n Term: %s \n Student: %s """ % (
    #                     semester_scheme.semester_id.name, new_semester.name, student.name))
    #
    #             current_semester_number = student.semester_id.number
    #             next_semester_number = current_semester_number + 1
    #             next_semester = self.env['odoocms.semester'].search([('number', '=', next_semester_number)])
    #             if not next_semester:
    #                 return False
    #
    #             next_semester_scheme = self.env['odoocms.semester.scheme'].search([
    #                 ('academic_session_id', '=', student.academic_session_id.id),
    #                 ('semester_id', '=', next_semester.id)
    #             ])
    #
    #             if semester_scheme.semester_id.number != next_semester_scheme.semester_id.number:
    #                 raise ValidationError("""Promotion is not possible: \nFrom Semester: %s (%s) \nTo Semester: %s (%s) \nStudent: %s """ % (
    #                     student.term_id.name,student.semester_id.name,
    #                     semester_scheme.term_id.name, semester_scheme.semester_id.name, student.name))
    #
    #             # student.term_id = new_semester.id
    #             # student.semester_id = next_semester.id
    #
    #         classes = student.get_possible_classes(new_semester)[0]
    #         #record.registered_course_ids = [(6, 0, registered_class_ids.ids)]
    #
    #         res['domain'] = {
    #             'compulsory_course_ids': [('id', 'in', classes['comp_class_ids'] and len(classes['comp_class_ids']) > 0 and classes['comp_class_ids'].ids or [])],
    #             'elective_course_ids': [('id', 'in', classes['elec_class_ids'] and len(classes['elec_class_ids']) > 0 and classes['elec_class_ids'].ids or [])],
    #             'repeat_course_ids': [('id', 'in', classes['offered_f'] and len(classes['offered_f']) > 0 and classes['offered_f'].ids or [])],
    #             'additional_course_ids': [('id', 'in', classes['additional_class_ids'] and len(classes['additional_class_ids']) > 0 and classes['additional_class_ids'].ids or [])],
    #         }
    #     return res
    #
    #
    # def action_invoice(self):
    #     re_reg_receipt_type = self.env['ir.config_parameter'].sudo().get_param('odoocms_registration.re_reg_receipt_type')
    #     if not re_reg_receipt_type:
    #         raise UserError('Please configure the Re-Registration Receipt Type in Global Settings')
    #
    #     view_id = self.env.ref('odoocms_fee.view_odoocms_generate_invoice_form')
    #     return {
    #         'name': _('Subject Registration Invoice'),
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'odoocms.generate.invoice',
    #         'view_id': view_id.id,
    #         'views': [(view_id.id, 'form')],
    #         'context': {
    #             'default_fixed_type': True,
    #             'default_receipt_type_ids': [(4, eval(re_reg_receipt_type), None)]},
    #         'target': 'new',
    #         'type': 'ir.actions.act_window'
    #     }
    #
    #

    #
    # def write(self, vals):
    #     # old_compulsory_course_ids = ', '.join([k.name for k in self.compulsory_course_ids])
    #     # old_elective_course_ids = ', '.join([k.name for k in self.elective_course_ids])
    #     # old_repeat_course_ids = ', '.join([k.name for k in self.repeat_course_ids])
    #
    #     old_compulsory_course_ids = self.compulsory_course_ids
    #     old_elective_course_ids = self.elective_course_ids
    #     old_repeat_course_ids = self.repeat_course_ids
    #     old_additional_course_ids = self.additional_course_ids
    #
    #     super(OdooCMSCourseRegistration, self).write(vals)
    #
    #     # new_compulsory_course_ids = ', '.join([k.name for k in self.compulsory_course_ids])
    #     # new_elective_course_ids = ', '.join([k.name for k in self.elective_course_ids])
    #     # new_repeat_course_ids = ', '.join([k.name for k in self.repeat_course_ids])
    #
    #     # if old_compulsory_course_ids != new_compulsory_course_ids:
    #     #     self.message_post(body="<b>Compulsory Courses:</b> %s &#8594; %s" % (old_compulsory_course_ids, new_compulsory_course_ids))
    #     # if old_elective_course_ids != new_elective_course_ids:
    #     #     self.message_post(body="<b>Compulsory Courses:</b> %s &#8594; %s" % (old_elective_course_ids, new_elective_course_ids))
    #     # if old_repeat_course_ids != new_repeat_course_ids:
    #     #     self.message_post(body="<b>Compulsory Courses:</b> %s &#8594; %s" % (old_repeat_course_ids, new_repeat_course_ids))
    #
    #     message = ''
    #     if self.compulsory_course_ids - old_compulsory_course_ids:
    #         message += "<b>Compulsory Courses Added:</b> %s<br/>" % (
    #                 ', '.join([k.name for k in (self.compulsory_course_ids - old_compulsory_course_ids)]))
    #
    #     if old_compulsory_course_ids - self.compulsory_course_ids:
    #         message += "<b>Compulsory Courses Removed:</b> %s\n" % (
    #                  ', '.join([k.name for k in (old_compulsory_course_ids - self.compulsory_course_ids)]))
    #
    #     if self.elective_course_ids - old_elective_course_ids:
    #         message += "<b>Elective Courses Added:</b> %s<br/>" % (
    #                 ', '.join([k.name for k in (self.elective_course_ids - old_elective_course_ids)]))
    #
    #
    #     if old_elective_course_ids - self.elective_course_ids:
    #         message += "<b>Elective Courses Removed:</b> %s<br/>" % (
    #                 ', '.join([k.name for k in (old_elective_course_ids - self.elective_course_ids)]))
    #
    #
    #     if self.repeat_course_ids - old_repeat_course_ids:
    #         message += "<b>Failed Courses Added:</b> %s<br/>" % (
    #                 ', '.join([k.name for k in (self.repeat_course_ids - old_repeat_course_ids)]))
    #
    #     if old_repeat_course_ids - self.repeat_course_ids:
    #         message += "<b>Failed Courses Removed:</b> %s<br/>" % (
    #                 ', '.join([k.name for k in (old_repeat_course_ids - self.repeat_course_ids)]))
    #
    #
    #     if self.additional_course_ids - old_additional_course_ids:
    #         message += "<b>Additional Courses Added:</b> %s<br/>" % (
    #             ', '.join([k.name for k in (self.additional_course_ids - old_additional_course_ids)]))
    #
    #     if old_additional_course_ids - self.additional_course_ids:
    #         message += "<b>Additional Courses Removed:</b> %s\n" % (
    #             ', '.join([k.name for k in (old_additional_course_ids - self.additional_course_ids)]))
    #
    #     if message:
    #         self.message_post(body=message)
    #
    #     return True
