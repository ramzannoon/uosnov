from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, datetime
from odoo.tools.safe_eval import safe_eval
from odoo.osv import expression

import pdb
from datetime import datetime, timedelta
import base64


class StudentGradeChange(models.Model):
    _name = "odoocms.student.grade.change"
    _description = 'Student Grade Change'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    READONLY_STATES = {
        'submit': [('readonly', True)],
        'approve': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    student_id = fields.Many2one('odoocms.student', string='Student', states=READONLY_STATES)
    term_id = fields.Many2one('odoocms.academic.term', string='Academic Term', related='student_id.term_id',store=True)
    program_id = fields.Many2one('odoocms.program', string='Program', related='student_id.program_id',store=True)
    batch_id = fields.Many2one('odoocms.batch', string='Program batch', related='student_id.batch_id',store=True)

    registration_id = fields.Many2one('odoocms.student.course', string='Student Course', required=True, )
    primary_class_id = fields.Many2one('odoocms.class.primary', string='Primary Class', related='registration_id.primary_class_id')
    
    prev_grade = fields.Char('Previous Grade', compute='_get_previous_grade', readonly=True)
    prev_grade2 = fields.Char('Prev. Grade', readonly=True)
    grade = fields.Char('New Grade')
    reason = fields.Text('Reason')
    
    date_request = fields.Date('Date', default=date.today(), readonly=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('submit', 'Submit'), ('approve', 'Approved'), ('done', 'Done'), ('cancel', 'Cancel')],
        string='State', default='draft', tracking=True)

    @api.onchange('registration_id')
    def _get_previous_grade(self):
        for rec in self:
            if rec.registration_id and rec.registration_id.grade:
                rec.prev_grade = rec.registration_id.grade

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('odoocms.student.grade.change') or _('New')
        result = super().create(vals)
        return result

    def action_submit(self):
        activity = self.env.ref('odoocms_exam.mail_act_grade_change')
        self.activity_schedule('odoocms_exam.mail_act_grade_change', user_id=activity._get_role_users(self.program_id))
    
        self.state = 'submit'
        if self.state == 'draft':
            self.state = 'submit'

    def action_approve(self):
        if self.state == 'submit':
            self.state = 'approve'

    def action_done(self):
        for rec in self:
            if rec.state == 'approve':
                message = ''
            
                if not rec.grade:
                    raise UserError('New Grade is not assigned.')
                
                rec.prev_grade2 = rec.registration_id.grade
                rec.registration_id.grade = rec.grade
            
                grade_rec = self.env['odoocms.grade.gpa'].search([('name', '=', rec.registration_id.grade)])
                if not grade_rec:
                    raise UserError('GPA Setting is not configured.')
                rec.registration_id.gpa = grade_rec.gpa
            
                message += "Grade has been changed from <b>%s</b> to <b>%s</b>" % (rec.prev_grade, rec.grade)
                rec.registration_id.message_post(body=message)
            
                self.state = 'done'
        
            else:
                raise UserError("You can't change the grade from %s to %s" % (rec.registration_id.grade, rec.grade))

    def action_cancel(self):
        for rec in self:
            if rec.state != 'done':
                rec.state = 'cancel'
                
                
class CourseGradeChange(models.Model):
    _name = "odoocms.course.grade.change"
    _description = 'Grade Change'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'batch_id'

    READONLY_STATES = {
        'submit': [('readonly', True)],
        'approve': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    term_id = fields.Many2one('odoocms.academic.term', string='Academic Term', states=READONLY_STATES)
    program_id = fields.Many2one('odoocms.program', string='Program')
    batch_id = fields.Many2one('odoocms.batch', string='Program batch')
    primary_class_id = fields.Many2one('odoocms.class.primary', string='Primary Class')
    grade_ids= fields.One2many('odoocms.course.grade.change.line', 'grade_id', string='Exam Grade Details')
    date_request = fields.Date('Date', default=date.today(), readonly=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('submit', 'Submit'), ('approve', 'Approved'), ('done', 'Done'), ('cancel', 'Cancel')],
        string='State', default='draft', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('odoocms.course.grade.change') or _('New')
        result = super().create(vals)
        return result
        
    def action_submit(self):
        activity = self.env.ref('odoocms_exam.mail_act_grade_change')
        self.activity_schedule('odoocms_exam.mail_act_grade_change', user_id=activity._get_role_users(self.program_id))

        self.state = 'submit'
        if self.state == 'draft':
            self.state = 'submit'

    def action_approve(self):
        for rec in self.grade_ids:
            message = ''
            if self.state == 'submit':
                self.state = 'approve'
                for line in self.grade_ids:
                    line.state = 'approve'
            # if rec.state == 'approve' and not rec.student_course_id.grade in ('I','W'):

    def action_done(self):
        for rec in self.grade_ids:
            if rec.state == 'approve':
                message = ''

                rec.prev_grade2 = rec.student_course_id.grade
                rec.student_course_id.grade = rec.grade

                message += "Grade has been changed from <b>%s</b> to <b>%s</b>" % (rec.prev_grade, rec.grade)
                rec.student_course_id.message_post(body=message)

                if rec.grade:
                    grade_gpa = self.env['odoocms.grade.gpa'].search([('name', '=', rec.student_course_id.grade)])
                    if not grade_gpa:
                        raise UserError('GPA Setting is not configured.')
                    rec.student_course_id.gpa = grade_gpa.gpa
                self.state = 'done'
            else:
                raise UserError("You can't change the grade from %s to %s" % (rec.student_course_id.grade, rec.grade))

    def action_cancel(self):
        for rec in self:
            if rec.state != 'done':
                rec.state = 'cancel'


class CourseGradeChangeLine(models.Model):
    _name = "odoocms.course.grade.change.line"
    _description = 'Grade Change line'

    # student_id = fields.Many2one('odoocms.student', string='Student')
    student_course_id = fields.Many2one('odoocms.student.course', string='Student Course', required=True,)
    primary_class_id = fields.Many2one('odoocms.class.primary', string='Primary Class', related='student_course_id.primary_class_id')
    program_id = fields.Many2one('odoocms.program', string='Program', related='student_course_id.program_id',
                                 readonly=True, store=True)
    session_id = fields.Many2one('odoocms.academic.session', string='Academic Session',
                                 related='student_course_id.session_id', readonly=True, store=True)
    prev_grade = fields.Char('Previous Grade', compute='_get_previous_grade', readonly=True)
    prev_grade2 = fields.Char('Prev. Grade', readonly=True)
    grade = fields.Char('New Grade')
    reason = fields.Text('Reason')
    grade_id = fields.Many2one('odoocms.course.grade.change', string='Grade Change')
    date_request = fields.Date('Date', default=date.today(), readonly=True)

    state = fields.Selection(
        [('draft', 'Draft'), ('submit', 'Submit'), ('approve', 'Approved'), ('done', 'Done'), ('cancel', 'Cancel')],
        string='State', default='draft', tracking=True)

    @api.onchange('student_course_id')
    def _get_previous_grade(self):
        for rec in self:
            student_course = self.env['odoocms.student.course'].search([('id', '=', rec.student_course_id.id)])
            if student_course and student_course.grade:
                rec.prev_grade = student_course.grade


class OdooCMSCourseWithdraw(models.Model):
    _name = "odoocms.student.course.withdraw"
    _description = 'Course Withdraw'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'registration_id'

    READONLY_STATES = {
        'submit': [('readonly', True)],
        'approve': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    student_id = fields.Many2one('odoocms.student', string='Student', states=READONLY_STATES)
    date_request = fields.Date('Date', required=True, default=fields.Date.context_today, readonly=True)
    term_id = fields.Many2one('odoocms.academic.term', string='Academic Term', states=READONLY_STATES)
    registration_id = fields.Many2one('odoocms.student.course', string='Student Subject', required=True,
                                      states=READONLY_STATES)

    program_id = fields.Many2one('odoocms.program', string='Program', related='registration_id.program_id',
                                 readonly=True, store=True)
    session_id = fields.Many2one('odoocms.academic.session', string='Academic Session',
                                 related='registration_id.session_id', readonly=True,
                                 store=True)
    primary_class_id = fields.Many2one('odoocms.class.primary', string='Primary Class', related='registration_id.primary_class_id', readonly=True)

    grade = fields.Char('Grade', related='registration_id.grade')
    request_time = fields.Selection([('pre', 'PRE Result'), ('post', 'Post Result')], string='Request Time',
                                    compute='get_grade_data', store=True)

    state = fields.Selection(
        [('draft', 'Draft'), ('submit', 'Submit'), ('approve', 'Approved'), ('done', 'Done'), ('cancel', 'Cancel')],
        string='State', default='draft', tracking=True)
    reason = fields.Text('Reason', required=True, states=READONLY_STATES)

    @api.onchange('registration_id')
    @api.depends('registration_id')
    def get_grade_data(self):
        for rec in self:
            if rec.registration_id:
                rec.request_time = 'post' if rec.registration_id.state == 'done' else 'pre'

    def action_submit(self):
        for rec in self:
            activity = self.env.ref('odoocms_exam.mail_activity_grade_withdraw')
            self.activity_schedule('odoocms_exam.mail_activity_grade_withdraw', user_id=activity._get_role_users(rec.program_id))
            rec.get_grade_data()
            rec.state = 'submit'

    def action_approve(self):
        for rec in self:
            message = ''
            rec.state = 'approve'
            rec.registration_id.grade = 'W'

            message += "Grade Changed from <b>%s</b> to <b>%s</b>" % (rec.grade, 'W')
            rec.message_post(body=message)
            rec.registration_id.message_post(body=message)

    def action_cancel(self):
        for rec in self:
            if rec.state != 'done':
                rec.state = 'cancel'


class OdooCMSCourseIncomplete(models.Model):
    _name = "odoocms.student.course.incomplete"
    _description = 'Course Incomplete'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'registration_id'

    READONLY_STATES = {
        'submit': [('readonly', True)],
        'approve': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    name = fields.Char(string='Reference', copy=False, readonly=True, index=True, default=lambda self: _('New'))
    student_id = fields.Many2one('odoocms.student', string='Student', states=READONLY_STATES)
    date_request = fields.Date('Date', required=True, default=fields.Date.context_today, readonly=True)
    term_id = fields.Many2one('odoocms.academic.term', string='Academic Term', states=READONLY_STATES)
    registration_id = fields.Many2one('odoocms.student.course', string='Student Course', required=True, states=READONLY_STATES)

    program_id = fields.Many2one('odoocms.program', string='Program', related='registration_id.program_id',
                                 readonly=True, store=True)
    session_id = fields.Many2one('odoocms.academic.session', string='Academic Session',
                                 related='registration_id.session_id', readonly=True, store=True)
    primary_class_id = fields.Many2one('odoocms.class.primary', string='Primary Class', related='registration_id.primary_class_id', readonly=True)

    grade = fields.Char('Grade', related='registration_id.grade')
    request_time = fields.Selection([('pre', 'Pre Result'), ('post', 'Post Result')], string='Request Time',
                                    compute='get_grade_data', store=True)

    state = fields.Selection(
        [('draft', 'Draft'), ('submit', 'Submit'), ('approve', 'Approved'), ('done', 'Done'), ('cancel', 'Cancel')],
        string='State', default='draft', tracking=True)
    reason = fields.Text('Reason', required=True, states=READONLY_STATES)
    line_ids = fields.One2many('odoocms.student.course.incomplete.line', 'incomplete_id', 'Components', states=READONLY_STATES)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('odoocms.student.course.incomplete') or _('New')
        result = super().create(vals)
        return result
    
    @api.onchange('registration_id')
    def get_grade_data(self):
        for rec in self:
            if rec.registration_id:
                rec.request_time = 'pre' if rec.registration_id.state in ('draft','current','lock') else 'post'
                
                components = [[5]]
                for component in rec.registration_id.component_ids:
                    cdata = {
                        'registration_component_id': component.id,
                        'total_marks': component.total_marks,
                    }
                    components.append((0, 0, cdata))
                rec.line_ids = components
                
    def action_submit(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError('Please add component first!')
            rec.attendance_check()
            # planning_line = rec.term_id.get_planning(rec.student_id, 'i-grade')
            # if not planning_line:
            #     raise UserError('I Grade Schedule for Current Semester has not been entered yet!')
            # if planning_line[0].date_start > rec.date_request or planning_line[0].date_end < rec.date_request:
            #     raise UserError('I Grade date has been Passed now!')
            
            activity = self.env.ref('odoocms_exam.mail_activity_grade_incomplete')
            self.activity_schedule('odoocms_exam.mail_activity_grade_incomplete', user_id=activity._get_role_users(rec.program_id))
            rec.state = 'submit'

    def attendance_check(self):
        pass

    def action_approve(self):
        for rec in self:
            message = ''
            rec.state = 'approve'
            rec.registration_id.write({
                'grade': 'I',
                'grade_date': date.today(),
                'incomplete_id': rec.id,
            })
            
            message += "Grade Changed from <b>%s</b> to <b>%s</b>" % (rec.grade, 'I')
            rec.message_post(body=message)
            rec.registration_id.message_post(body=message)

    def action_cancel(self):
        for rec in self:
            if rec.state != 'done':
                rec.state = 'cancel'

    def cron_action_change_grade(self, days):
        for rec in self:
            if date.today() > rec.registration_id.grade_date + timedelta(days= days):
                rec.registration_id.grade_date = date.today()
                rec.registration_id.grade = 'F'
                message = "Grade Changed from <b>%s</b> to <b>%s</b>" % (rec.grade, 'F')
                rec.message_post(body=message)
                rec.registration_id.message_post(body=message)
                
                method = "grade_class_id.%s(%d)" % (rec.primary_class_id.grade_class_id.grading_id.method, rec.registration.id)
                safe_eval(method, {'grade_class_id': rec.primary_class_id.grade_class_id}, mode='exec', nocopy=True)


class OdooCMSCourseIncompleteLine(models.Model):
    _name = "odoocms.student.course.incomplete.line"
    _description = 'Course Incomplete Line'
    _rec_name = 'registration_component_id'

    incomplete_id = fields.Many2one('odoocms.student.course.incomplete', string='Incomplete ID',ondelete='cascade')
    registration_id = fields.Many2one('odoocms.student.course', string='Student Course', related='incomplete_id.registration_id', store=True)
    registration_component_id = fields.Many2one('odoocms.student.course.component', string='Component')
    total_marks = fields.Float('Total Marks')
    state = fields.Selection(related='incomplete_id.state', store=True)
    

class OdooCMSStudentCourseRetest(models.Model):
    _name = "odoocms.student.course.retest"
    _description = 'Course Retest'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'registration_id'

    READONLY_STATES = {
        'current': [('readonly', True)],
        'lock': [('readonly', True)],
        'submit': [('readonly', True)],
        'disposal': [('readonly', True)],
        'approval': [('readonly', True)],
        'verify': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }
    
    name = fields.Char(string='Reference', copy=False, readonly=True, index=True, default=lambda self: _('New'))
    student_id = fields.Many2one('odoocms.student', string='Student', states=READONLY_STATES)
    date_request = fields.Date('Date', required=True, default=fields.Date.context_today, readonly=True)
    term_id = fields.Many2one('odoocms.academic.term', string='Academic Term', states=READONLY_STATES)
    registration_id = fields.Many2one('odoocms.student.course', string='Student Subject', required=True, states=READONLY_STATES)

    program_id = fields.Many2one('odoocms.program', string='Program', related='registration_id.program_id',
                                 readonly=True, store=True)
    session_id = fields.Many2one('odoocms.academic.session', string='Academic Session',
                                 related='registration_id.session_id', readonly=True, store=True)
    primary_class_id = fields.Many2one('odoocms.class.primary', string='Primary Class', related='registration_id.primary_class_id', readonly=True)

    pre_total_marks = fields.Float('Prev. Marks', compute='_get_marks', store=True)
    pre_normalized_marks = fields.Float('Prev. Normalized Marks', compute='_get_marks', store=True)
    pre_grade = fields.Char('Prev. Grade', compute='_get_marks', store=True)
    
    total_marks = fields.Float('New Marks',related='registration_id.total_marks',store=True)
    normalized_marks = fields.Float('New Normalized Marks',related='registration_id.normalized_marks',store=True)
    grade = fields.Char('Grade',related='registration_id.grade',store=True)
    
    state = fields.Selection([
        ('draft', 'Draft'), ('current', 'Current'), ('lock', 'Locked'),
        ('submit', 'Submitted'), ('disposal', 'Disposal'), ('approval', 'Approval'),
        ('verify', 'Verify'), ('done', 'Done'), ('cancel', 'Cancel')
    ], string='State', default='draft', tracking=True)
    reason = fields.Text('Reason', required=True, states=READONLY_STATES)
    
    line_ids = fields.One2many('odoocms.student.course.retest.line', 'retest_id', 'Components')
    disposal_history_id = fields.Many2one('odoocms.exam.disposal.history','Disposal')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('odoocms.student.course.retest') or _('New')
        result = super().create(vals)
        return result
    
    @api.depends('registration_id')
    def _get_marks(self):
        for rec in self:
            if rec.registration_id:
                rec.pre_total_marks = rec.registration_id.total_marks
                rec.pre_normalized_marks = rec.registration_id.normalized_marks
                rec.pre_grade = rec.registration_id.grade

                # rec.assessment_ids = False
                components = [[5]]
                for component in rec.registration_id.component_ids:
                    lines = component.assessment_summary_ids.filtered(lambda l: l.final == True).assessment_lines
                    cdata = {
                        'registration_component_id': component.id,
                        'pre_total_marks': component.total_marks,
                        'pre_final_obtained_marks': lines and lines[0].obtained_marks or 0,
                        'pre_final_max_marks': lines and lines[0].max_marks or 0,
                    }
                    components.append((0, 0, cdata))
                rec.line_ids = components

    def action_current(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError('Please add component first!')
            rec.state = 'current'
            rec.registration_id.retest_id = rec.id
            
    def action_submit(self):
        for rec in self:
            rec.assign_grade()
            activity = self.env.ref('odoocms_exam.mail_act_retest_request')
            rec.activity_schedule('odoocms_exam.mail_act_retest_request', user_id=activity._get_role_users(rec.program_id))
            rec.state = 'submit'

    def action_approve(self):
        for rec in self:
            rec.state = 'disposal'
            
    def action_disposal(self):
        waiting_recs = self.env['odoocms.student.course'].search([
            ('term_id','=',self.term_id.id),('student_id','=',self.student_id.id),
            ('state', 'in', ('draft','current','lock','submit'))
        ])
        if waiting_recs:
            raise UserError('There are %s Course results pending for %s-%s' % (len(waiting_recs),self.student_id.code,self.student_id.name))
        
        values = {
            'batch_id': self.student_id.batch_id.id,  # [(6, 0, self.batch_ids.mapped('id'))],
            'batch_term_id': False,
            'user_id': self.env.user.id,
            'date': datetime.now(),
            'term_id': self.term_id.id,
        }
        disposal_history_id = self.env['odoocms.exam.disposal.history'].create(values)
        self.student_id.apply_disposals(disposal_history_id.id)
        disposal_recs = self.env['odoocms.student.course.retest'].search([('student_id','=',self.student_id.id),('state','=','disposal')])
        disposal_recs.write({
            'disposal_history_id': disposal_history_id.id,
            'state': 'done'
        })
        
    def assign_grade(self):
        for rec in self:
            grade_method_id = rec.registration_id.primary_class_id.grade_class_id.grade_method_id
            marks = rec.registration_id.total_marks
            if grade_method_id and grade_method_id.code == 'histogram':
                grade_id = self.env['odoocms.grade.histo'].search([
                    ('low_per', '<=', marks),
                    ('high_per', '>', marks if marks < 100 else 99),
                    ('grade_class_id', '=', rec.registration_id.grade_class_id.id),
                ])
                if rec.registration_id.grade == 'I':
                    if grade_id and marks > 0:
                        rec.registration_id.grade = grade_id.name
                    else:
                        rec.registration_id.grade = 'F'
                elif grade_id.name != 'F':
                    rec.registration_id.grade = 'D'
            else:
                grade_rec = self.env['odoocms.grade']
                for grade in self.env['odoocms.grade'].search([]):
                    domain = expression.AND([safe_eval(grade.domain), [('id', '=', rec.student_id.program_id.id)]]) if grade.domain else []
                    program = self.env['odoocms.program'].search(domain)
                    if program:
                        grade_rec = grade
    
                grade_id = grade_rec.line_ids.filtered(lambda g: g.low_per <= marks <= g.high_per)
                if rec.registration_id.grade == 'I':
                    if grade_id and marks > 0:
                        rec.registration_id.grade = grade_id[0].name
                    else:
                        rec.registration_id.grade = 'F'
                elif grade_id[0].name != 'F':
                    rec.registration_id.grade = 'D'

    def action_cancel(self):
        for rec in self:
            if rec.state != 'done':
                rec.state = 'cancel'


class OdooCMSStudentCourseRetestLine(models.Model):
    _name = "odoocms.student.course.retest.line"
    _description = 'Course Retest Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'registration_component_id'

    retest_id = fields.Many2one('odoocms.student.course.retest', string='Retest ID', ondelete='cascade')
    registration_id = fields.Many2one('odoocms.student.course', string='Student Course', related='retest_id.registration_id', store=True)
    registration_component_id = fields.Many2one('odoocms.student.course.component', string='Component')
    pre_total_marks = fields.Float('Pre Total Marks')
    pre_final_obtained_marks = fields.Float('Final Obtained Marks')
    pre_final_max_marks = fields.Float('Final Max Marks')
    
    new_final_marks = fields.Float('New Final Marks')
    new_total_marks = fields.Float('New Total Marks', compute='_get_marks', store=True)
    state = fields.Selection(related='retest_id.state',store=True)
    
    @api.depends('new_final_marks')
    def _get_marks(self):
        for rec in self:
            lines = rec.registration_component_id.assessment_summary_ids.filtered(lambda l: l.final == True).assessment_lines
            if lines:
                lines[0].obtained_marks = rec.new_final_marks
            rec.new_total_marks = rec.registration_component_id.total_marks
            

class OdooCMSStudentCourse(models.Model):
    _inherit = "odoocms.student.course"
    
    retest_id = fields.Many2one('odoocms.student.course.retest','Re-Test Request')
    incomplete_id = fields.Many2one('odoocms.student.course.incomplete','Incomplete Request')
    
    @api.depends('primary_class_id', 'primary_class_id.state', 'dropped','retest_id','retest_id.state')
    def _get_course_state(self):
        for rec in self:
            if rec.dropped:
                rec.state = 'done'
            elif rec.retest_id:
                rec.state = rec.retest_id.state
            elif rec.incomplete_id:
                rec.state = 'done'
            elif rec.primary_class_id:
                rec.state = rec.primary_class_id.state
            else:
                rec.state = 'done'
                

class OdooCMSCourseWaiting(models.Model):
    _name = 'odoocms.student.course.waiting'
    _description = 'Course Waiting'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'registration_id'

    READONLY_STATES = {
        'submit': [('readonly', True)],
        'approve': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    student_id = fields.Many2one('odoocms.student', string='Student', states=READONLY_STATES)
    date_request = fields.Date('Date Request', required=True, default=fields.Date.context_today, readonly=True)
    date_approve = fields.Date('Date Approved', required=True, readonly=True)
    term_id = fields.Many2one('odoocms.academic.term', string='Academic Term', states=READONLY_STATES)
    registration_id = fields.Many2one('odoocms.student.course', string='Student Subject', required=True,
                                      states=READONLY_STATES)

    program_id = fields.Many2one('odoocms.program', string='Program', related='registration_id.program_id',
                                 readonly=True, store=True)
    session_id = fields.Many2one('odoocms.academic.session', string='Academic Session',
                                 related='registration_id.session_id', readonly=True,
                                 store=True)
    primary_class_id = fields.Many2one('odoocms.class.primary', string='Primary Class', related='registration_id.primary_class_id', readonly=True)

    grade = fields.Char('Grade', related='registration_id.grade')
    request_time = fields.Selection([('pre', 'PRE Result'), ('post', 'Post Result')], string='Request Time',
                                    compute='get_grade_data', store=True)

    state = fields.Selection(
        [('draft', 'Draft'), ('submit', 'Submit'), ('approve', 'Approved'), ('done', 'Done'), ('cancel', 'Cancel')],
        string='State', default='draft', tracking=True)
    reason = fields.Text('Reason', required=True, states=READONLY_STATES)

    @api.onchange('registration_id')
    @api.depends('registration_id')
    def get_grade_data(self):
        for rec in self:
            if rec.registration_id:
                rec.request_time = 'post' if rec.registration_id.state == 'done' else 'pre'
                
    def action_submit(self):
        for rec in self:
            activity = self.env.ref('odoocms_exam.mail_activity_grade_incomplete')
            rec.activity_schedule('odoocms_exam.mail_activity_grade_incomplete', user_id=activity._get_role_users(rec.program_id))
            rec.get_grade_data()
            rec.state = 'submit'

    def action_approve(self):
        for rec in self:
            message = ''
            rec.state = 'approve'
            rec.registration_id.grade = 'RW'
            rec.date_approve = date.today()

            message += "Grade Changed from <b>%s</b> to <b>%s</b>" % (rec.grade, 'RW')
            rec.message_post(body=message)
            rec.registration_id.message_post(body=message)

    def action_cancel(self):
        for rec in self:
            if rec.state != 'done':
                rec.state = 'cancel'

    def action_assign_grade(self):
        for rec in self:
            if rec.state == 'approve':
                rec.state = 'done'
                method = "class_id.%s(%d)" % (rec.class_id.grading_id.method, rec.registration.id)
                safe_eval(method, {'class_id': rec.class_id}, mode='exec', nocopy=True)


class OdoocmsStudentCourseEquivalence(models.Model):
    _name = "odoocms.student.course.equivalence"
    _description = 'Subject Equivalence'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'registration_id'

    READONLY_STATES = {
        'submit': [('readonly', True)],
        'approve': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    student_id = fields.Many2one('odoocms.student', string='Student', required=True, states=READONLY_STATES)
    date_request = fields.Date('Date', required=True, default=fields.Date.context_today, readonly=True)
    term_id = fields.Many2one('odoocms.academic.term', string='Academic Term', states=READONLY_STATES)
    registration_id = fields.Many2one(relation='subject',comodel_name='odoocms.student.course', string='Student Course', required=True,
                                      states=READONLY_STATES)

    new_registration_id = fields.Many2one(relation='new_suject',comodel_name='odoocms.student.course', string='Equivalent Student Subject',
                                          states=READONLY_STATES)

    equivalent_class_id = fields.Many2one('odoocms.class.primary', string='Equivalent Course', states=READONLY_STATES)

    program_id = fields.Many2one('odoocms.program', string='Program', related='registration_id.program_id',
                                 readonly=True, store=True)
    session_id = fields.Many2one('odoocms.academic.session', string='Academic Session',
                                 related='registration_id.session_id', readonly=True,
                                 store=True)

    grade = fields.Char('Grade', related='registration_id.grade')
    request_time = fields.Selection([('pre', 'PRE Result'), ('post', 'Post Result')], string='Request Time',
                                    compute='get_grade_data', store=True)

    state = fields.Selection(
        [('draft', 'Draft'), ('submit', 'Submit'), ('approve', 'Approved'), ('done', 'Done'), ('cancel', 'Cancel')],
        string='State', default='draft', tracking=True)
    reason = fields.Text('Reason', states=READONLY_STATES)

    @api.onchange('registration_id')
    @api.depends('registration_id')
    def get_grade_data(self):
        for rec in self:
            if rec.registration_id:
                rec.request_time = 'post' if rec.registration_id.state == 'done' else 'pre'

    @api.onchange('student_id', 'registration_id', 'term_id')
    def get_domain(self):
        equivalent_courses = []
        if self.student_id and self.registration_id:
            registered_student_course_ids = self.student_id.enrolled_course_ids  # All states
            request_class_ids = self.env['odoocms.course.registration'].search(
                [('student_id', '=', self.student_id.id), ('state', 'in', ('draft', 'submit'))])
            request_class_ids = request_class_ids.mapped('compulsory_course_ids') + request_class_ids.mapped('elective_course_ids') + request_class_ids.mapped('repeat_course_ids') + request_class_ids.mapped('additional_course_ids')
    
            equivalent_courses = self.registration_id.course_id.equivalent_ids.mapped('course_id')
            new_courses = equivalent_courses - registered_student_course_ids.mapped('course_id')
            all_classes = self.env['odoocms.class.primary'].search([('term_id', '=', self.term_id.id)]).filtered(
                lambda l: l.study_scheme_line_id.course_id in new_courses ) - request_class_ids

            equivalent_courses = all_classes.ids
            #Prereq needs to be checked and minus the course that are in student compl study scheme
        return {
            'domain': {
                'equivalent_class_id': [('id', 'in', equivalent_courses)],
            }
        }

    def action_submit(self):
        for rec in self:
            if not rec.equivalent_class_id and not rec.new_registration_id:
                raise UserError('Please add Equivalent Course or New Student Subject')

            activity = self.env.ref('odoocms_exam.mail_act_subject_equivalence')
            rec.activity_schedule('odoocms_exam.mail_act_subject_equivalence', user_id=activity._get_role_users(rec.program_id))

            rec.get_grade_data()
            rec.state = 'submit'

    def action_approve(self):
        for rec in self:
            message = ''
            rec.state = 'approve'
            if rec.new_registration_id:
                rec.new_registration_id.course_id_1 = rec.registration_id.id
                rec.registration_id.course_id_2 = rec.new_registration_id.id
                rec.registration_id.repeat_code = 'EQU'
                rec.new_registration_id.repeat_code = 'EQU*'

                if rec.new_registration_id.gpa < rec.new_registration_id.course_id_1.gpa:
                    rec.new_registration_id.include_in_cgpa = False
                else:
                    rec.new_registration_id.course_id_1.include_in_cgpa = False
            elif rec.equivalent_class_id:
                message += "Equivalent Code assigned: <b>%s</b>" % (rec.equivalent_class_id.code,)
                rec.message_post(body=message)
                rec.registration_id.message_post(body=message)

                new_course_id = rec.action_enrollment()

                rec.registration_id.course_id_2 = new_course_id.id
                new_course_id.course_id_1 = rec.registration_id.id

                rec.registration_id.repeat_code = 'EQU'
                new_course_id.repeat_code = 'EQU*'

            else:
                raise UserError('Please add Equivalent Code or New Student Subject')

    def action_cancel(self):
        for rec in self:
            if rec.state != 'done':
                rec.state = 'cancel'

    def action_enrollment(self):
        st_term = self.env['odoocms.student.term'].search([('student_id', '=', self.student_id.id), ('term_id', '=', self.term_id.id), ])
        if not st_term:
            data = {
                'student_id': self.student_id.id,
                'term_id': self.term_id.id,
                'semester_id': self.student_id.semester_id.id,
            }
            st_term = st_term.create(data)

        component_ids = []
        for component in self.equivalent_class_id.class_ids:
            component_data = {
                'student_id': self.student_id.id,
                'class_id': component.id,
                'semester_id': self.student_id.semester_id.id,
                'term_id': self.term_id.id,
                'weightage': component.weightage,
            }
            component_ids.append((0, 0, component_data))

        data = {
            'student_id': self.student_id.id,
            'term_id': self.term_id.id,
            'semester_id': self.student_id.semester_id.id,
            'course_id': self.equivalent_class_id.study_scheme_line_id.id,
            'primary_class_id': self.equivalent_class_id.id,
            'student_term_id': st_term.id,
            'credits': self.equivalent_class_id.weightage,
            'course_code': self.equivalent_class_id.course_code,
            'course_name': self.equivalent_class_id.course_name,
            'tag': 'ALTERNATE' or "-",
            'component_ids': component_ids,
        }

        return self.env['odoocms.student.course'].create(data)


class OdooCMSCourseAlternate(models.Model):
    _name = "odoocms.student.course.alternate"
    _description = 'Course Alternate'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    READONLY_STATES = {
        'submit': [('readonly', True)],
        'approve': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    student_id = fields.Many2one('odoocms.student', string='Student', required=True, states=READONLY_STATES)
    date_request = fields.Date('Date Request', required=True, default=fields.Date.context_today, readonly=True)
    date_approve = fields.Date('Date Approved', readonly=True)

    type = fields.Selection([('grade','Grade Book'),('scheme','Study Scheme')],'Alternative Selection',default='grade', states=READONLY_STATES)
    
    registration_id = fields.Many2one('odoocms.student.course', string='Registered Course', states=READONLY_STATES)
    term_id = fields.Many2one('odoocms.academic.term', string='Academic Term', related='registration_id.term_id',store=True)
    grade = fields.Char('Previous Grade', related='registration_id.grade', store=True)
    
    course_id = fields.Many2one('odoocms.course','Course to Replace', states=READONLY_STATES)
    
    alternate_course_id = fields.Many2one('odoocms.course', string='Alternate Course',
        states={'approve': [('readonly', True)], 'cancel': [('readonly', True)],})

    program_id = fields.Many2one('odoocms.program', string='Program', related='student_id.program_id', store=True)
    session_id = fields.Many2one('odoocms.academic.session', string='Session', related='student_id.session_id', store=True)
    career_id = fields.Many2one('odoocms.career','Academic Level',related='student_id.career_id',store=True)
    state = fields.Selection([
        ('draft', 'Draft'), ('submit', 'Submit'), ('approve', 'Approved'), ('cancel', 'Cancel')],
        string='State', default='draft', tracking=True)
    reason = fields.Text('Reason', states=READONLY_STATES)

    def _get_domain(self, student_id):
        registered_course_ids = student_id.enrolled_course_ids.mapped('course_id')
        compulsory_course_ids = student_id.study_scheme_id.line_ids.filtered(lambda l: l.course_type in ('compulsory')).mapped('course_id')
        
        grade_courses = student_id.enrolled_course_ids.filtered(lambda l: l.state in ('done', 'notify'))
        alternate_courses = self.env['odoocms.course'].search([('career_id', '=', self.student_id.career_id.id)]) - registered_course_ids
        rep_courses = compulsory_course_ids - registered_course_ids
        return grade_courses, rep_courses, alternate_courses

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('odoocms.student.course.alternate') or _('New')
        result = super().create(vals)
        return result
    
    @api.onchange('student_id')
    def get_domain(self):
        grade_courses, rep_courses, alternate_courses = self._get_domain(self.student_id)
        # Prereq needs to be checked
        return {'domain': {
                'alternate_course_id': [('id', 'in', alternate_courses.ids)],
                'course_id': [('id', 'in', rep_courses.ids)],
                'registration_id': [('id', 'in', grade_courses.ids)],
            }
        }

    def action_submit(self):
        for rec in self:
            # activity = self.env.ref('odoocms_exam.mail_act_subject_alternate')
            # rec.activity_schedule('odoocms_exam.mail_act_subject_alternate', user_id=activity._get_role_users(rec.program_id))
            rec.state = 'submit'

    def action_approve(self):
        for rec in self:
            if not rec.alternate_course_id:
                raise UserError('Please Select the Alternative Course before Approval.')
            message = ''
            rec.state = 'approve'
            rec.date_approve = date.today()

            message += "Alternate Code assigned: <b>%s</b>" % (rec.alternate_course_id.code,)
            rec.message_post(body=message)
            if rec.registration_id:
                rec.registration_id.message_post(body=message)

    def action_cancel(self):
        for rec in self:
            if rec.state != 'approve':
                rec.state = 'cancel'


class OdooCMSrequestPaperRechecking(models.Model):
    _name = "odoocms.request.subject.rechecking"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Student Rechecking Request"
    _rec_name = 'student_id'

    READONLY_STATES = {
        'approve': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    READONLY_STATES2 = {
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    student_id = fields.Many2one('odoocms.student', string='Student', states=READONLY_STATES)
    batch_id = fields.Many2one('odoocms.batch', string='Class Batch', related='student_id.batch_id',
                               states=READONLY_STATES)
    term_id = fields.Many2one('odoocms.academic.term', string='Academic Term', states=READONLY_STATES)

    description = fields.Text(string='Detailed Reason', states=READONLY_STATES)
    reason_id = fields.Many2one('odoocms.drop.reason', string='Reason', states=READONLY_STATES)
    date_request = fields.Date('Request Date', default=date.today(), readonly=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('submit', 'Submit'), ('approve', 'Approved'), ('approve2', 'Approved2'),
         ('cancel', 'Cancel'), ('done', 'Done'),('invoice_generated','Invoice Generated')], default='draft', string="Status", tracking=True)
    invoice_created = fields.Boolean(string='Invoice Created')
    rechecking_subject = fields.Integer(compute='_total_subjects',string='Rechecking Subjects')
    rechecking_line_ids= fields.One2many('odoocms.request.subject.rechecking.line','rechecking_id',string="Rechecking Details")
    rechecking_id = fields.Char('rechecking Reference',help='Batch Number etc...', default=lambda self:self.env['ir.sequence'].next_by_code('odoocms.request.subject.rechecking'),copy=False, readonly=True)

    @api.depends('rechecking_line_ids')
    def _total_subjects(self):
        for rec in self:
            rec.rechecking_subject = len(rec.rechecking_line_ids)

    @api.constrains('rechecking_line_ids')
    def _check_subject_limit(self):
        for rec in self:
            subject_limit = self.env['ir.config_parameter'].sudo().get_param(
                'odoocms_registration.re_checking_subject_limit')
            if len(rec.rechecking_line_ids)>int(subject_limit) :

                raise UserError(_("you can not exceed from Rechecking subject Limit! Please Check In Global setting"))

    def action_submit(self):
        for rec in self:
            planning_line = rec.term_id.get_planning(rec.student_id, 'rechecking')
            if not planning_line:
                raise UserError('Rechecking schedule for %s! is not entered Yet.' % (rec.term_id.name))

            if planning_line.date_start > rec.date_request or planning_line.date_end < rec.date_request:
                raise UserError('Rechecking Schedule has been over now!')

            # if not rec.batch_id.department_id.chairman_id:
            #     raise UserError('Please Assign Head/Chariman to %s!' % (rec.batch_id.department_id.name))
            # if not rec.batch_id.department_id.chairman_id.user_id:
            #     raise UserError('Please Create the Login User for %s!' % (rec.batch_id.department_id.chairman_id.name))
            #
            # rec.activity_schedule('odoocms_registration.mail_act_paper_rechecking',
            #                       user_id=rec.batch_id.department_id.chairman_id.user_id.id)
            # rec.state = 'submit'
            rec.state = 'approve'

    def action_approve(self):
        for rec in self:
            if rec.state == 'submit':
                rec.state = 'approve'
            else:
                raise UserError('Request is not Approved by Management yet.')

    def action_invoice(self):
        re_checking_receipt_type = self.env['ir.config_parameter'].sudo().get_param(
            'odoocms_registration.re_checking_receipt_type')
        if not re_checking_receipt_type:
            raise UserError('Please configure the Rechecking Receipt Type in Global Settings')
        re_checking_receipt_type = self.env['odoocms.receipt.type'].search([('id', '=', re_checking_receipt_type)])
        if not re_checking_receipt_type.fee_head_ids:
            raise UserError('Please configure heads with Receipt Type.')

        fee_structure = self.env['odoocms.fee.structure'].search([
            ('session_id', '=', self.student_id.session_id.id),
            ('career_id', '=', self.student_id.career_id.id),('current','=',True)
        ])
        if not fee_structure:
            raise UserError(
                _('Fee structure is not defined for session %s.' % (self.student_id.session_id.name)))

        fee_amount = 0
        if fee_structure and fee_structure.line_ids and fee_structure.line_ids.filtered(
                lambda l: l.fee_head_id.id == re_checking_receipt_type.fee_head_ids[0].id):
            fee_amount = fee_structure.line_ids.filtered(
                lambda l: l.fee_head_id.id == re_checking_receipt_type.fee_head_ids[0].id).fee_amount
        # sm_freez_receipt_type.fee_head_ids[0].

        re_checking_receipt_types  = re_checking_receipt_type
        for i in range(len(self.rechecking_line_ids)-1):
            re_checking_receipt_types += re_checking_receipt_type

        des =""
        for sub in self.rechecking_line_ids:
            des += sub.registration_id.subject_id.subject_id.name + ","

        if fee_amount > 0:
            self.invoice_created = True
            view_id = self.env.ref('odoocms_fee.view_odoocms_generate_invoice_form')
            return {
                'name': _('Rechecking Invoice'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'odoocms.generate.invoice',
                'view_id': view_id.id,
                'views': [(view_id.id, 'form')],
                'context': {
                    'default_fixed_type': True,
                    'default_rechecking_subject': self.rechecking_subject,
                    'default_rechecking_id': self.rechecking_id,
                    'default_description_sub': des,
                    # 'default_registration_id': self.registration_id.id or 0,
                    'default_term_id': self.term_id.id or 0,
                    'default_receipt_type_ids': [(4, rec_type.id, None) for rec_type in re_checking_receipt_types],
                    'default_student_ids': [(4, self.student_id.id, None)]
                },

                'target': 'new',
                'type': 'ir.actions.act_window'
            }

        return {'type': 'ir.actions.act_window_close'}

    # def action_approve2(self):
    #     re_checking_receipt_type = self.env['ir.config_parameter'].sudo().get_param('odoocms_registration.re_checking_receipt_type')
    #     re_checking_receipt_type = self.env['odoocms.receipt.type'].search([('id', '=', re_checking_receipt_type)])
    #
    #     for rec in self:
    #         invoice_id = self.env['account.invoice'].search([('student_id','=',rec.student_id.id),('registration_id','=',rec.registration_id.id),('state','=','paid'),('receipt_type_ids','in',re_checking_receipt_type.id)])
    #         if rec.state == 'approve' and invoice_id:
    #             rec.state ='approve2'
    #         else:
    #             raise UserError('Request is not confirmed yet. Invoice not paid may be.')

    def action_update_result(self):

        re_checking_receipt_type = self.env['ir.config_parameter'].sudo().get_param(
            'odoocms_registration.re_checking_receipt_type')
        re_checking_receipt_type = self.env['odoocms.receipt.type'].search([('id', '=', re_checking_receipt_type)])

        for rec in self.rechecking_line_ids:
            invoice_id = self.env['account.invoice'].search(
                [('student_id', '=', self.student_id.id), ('term_id', '=', self.term_id.id),
                 ('state', '=', 'paid'), ('receipt_type_ids', 'in', re_checking_receipt_type.id)])
            if self.state != 'invoice_generated':
                raise UserError('Request is not Approved yet.')
            elif self.state == 'invoice_generated' and invoice_id:
                max_marks = rec.registration_id.primary_class_id.max_marks
                if max_marks ==0:
                    max_marks = 1
                new_marks = rec.new_marks/max_marks
                if new_marks >= 100:
                    new_marks = 100
                rec.registration_id.normalized_marks = new_marks

                grade_rec = self.env['odoocms.exam.grade'].search([
                    ('low_per', '<=', new_marks),
                    ('high_per', '>=', new_marks),
                    ('primary_class_id', '=', False)
                ])
                if grade_rec:
                    rec.registration_id.grade = grade_rec.name
                else:
                    raise UserError('Grading is not configured.')

                grade_gpa = self.env['odoocms.grade.gpa'].search([('name', '=', rec.registration_id.grade)])
                if not grade_gpa:
                    raise UserError('GPA Setting is not configured.')

                rec.registration_id.gpa = grade_gpa.gpa
                rec.state = 'done'
                self.state='done'
            else:
                raise UserError('Invoice not Paid Yet.')

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'


class OdooCMSrequestPaperRecheckingLine(models.Model):
    _name = "odoocms.request.subject.rechecking.line"
    _description = "Student Rechecking Request Line "

    registration_id = fields.Many2one('odoocms.student.course', string='Subject',
                                      required=True)
    primary_class_id = fields.Many2one('odoocms.class.primary', related='registration_id.primary_class_id', store=True)
    pre_normalized_marks = fields.Float(string='Previous Normalized Marks', related='registration_id.normalized_marks')
    pre_gpa = fields.Float(string='Previous GPA', related='registration_id.gpa')
    new_marks = fields.Float(string='New Marks', required=True)
    rechecking_id = fields.Many2one('odoocms.request.subject.rechecking',string='Rechecking')

    state = fields.Selection(
        [('draft', 'Draft'), ('submit', 'Submit'), ('approve', 'Approved'), ('approve2', 'Approved2'),
         ('cancel', 'Cancel'), ('done', 'Done'), ('invoice_generated', 'Invoice Generated')], default='draft',
        string="Status")


class OdooCMSStudentDegree(models.Model):
    _name = "odoocms.student.degree"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Student Degree"
    _rec_name = 'student_id'

    READONLY_STATES = {
        'approve': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    READONLY_STATES2 = {
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    student_id = fields.Many2one('odoocms.student', string='Student', states=READONLY_STATES)
    batch_id = fields.Many2one('odoocms.batch', string='Class Batch', related='student_id.batch_id',
                               states=READONLY_STATES)
    term_id = fields.Many2one('odoocms.academic.term', string='Academic Term', related='student_id.term_id', states=READONLY_STATES)
    date_request = fields.Date('Date Request', default=date.today(), readonly=True)
    date_approve = fields.Date('Date Approve', readonly=True)
    date_done = fields.Datetime('Date Award', readonly=True)

    state = fields.Selection(
        [('draft', 'Draft'), ('submit', 'Submit'), ('invoice', 'Invoice'), ('approve', 'Approved'),
         ('cancel', 'Cancel'), ('done', 'Done')], default='draft', string="Status", tracking=True)
    invoice_created = fields.Boolean(string='Invoice Created')

    def action_submit(self):
        for rec in self:
            activity = self.env.ref('odoocms_exam.mail_act_degree_request')
            rec.activity_schedule('odoocms_exam.mail_act_degree_request', user_id=activity._get_role_users(rec.student_id.program_id))

            rec.state = 'submit'

    def action_approve(self):
        for rec in self:
            if rec.state == 'submit':
                rec.state = 'approve'
                rec.date_approve = date.today()
            else:
                raise UserError('Request is not Submitted yet.')

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def action_invoice(self):
        degree_receipt_type = self.env['ir.config_parameter'].sudo().get_param(
            'odoocms_registration.degree_receipt_type')
        if not degree_receipt_type:
            raise UserError('Please configure the Degree Receipt Type in Global Settings')
        degree_receipt_type = self.env['odoocms.receipt.type'].search([('id', '=', degree_receipt_type)])
        if not degree_receipt_type.fee_head_ids:
            raise UserError('Please configure heads with Receipt Type.')

        self.invoice_created = True
        self.state = 'invoice'
        view_id = self.env.ref('odoocms_fee.view_odoocms_generate_invoice_form')
        return {
            'name': _('Degree Invoice'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'odoocms.generate.invoice',
            'view_id': view_id.id,
            'views': [(view_id.id, 'form')],
            'context': {
                'default_fixed_type': True,
                'default_receipt_type_ids': [(4, degree_receipt_type.id, None)],
                'default_student_ids': [(4, self.student_id.id, None)]
            },

            'target': 'new',
            'type': 'ir.actions.act_window'
        }
        return {'type': 'ir.actions.act_window_close'}

    def action_award(self):
        for rec in self:
            if rec.state == 'invoice': #here we will add code for invoice paid
                rec.state = 'done'
                rec.date_done = datetime.today()


class OdooCMSStudentTranscript(models.Model):
    _name = "odoocms.student.transcript"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Student Transcript"
    _rec_name = 'student_id'

    READONLY_STATES = {
        'submit': [('readonly', True)],
        'approve': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    student_id = fields.Many2one('odoocms.student', string='Student', states=READONLY_STATES)
    batch_id = fields.Many2one('odoocms.batch', string='Class Batch', related='student_id.batch_id', store=True)
    program_id = fields.Many2one('odoocms.program', string='Program', related='student_id.program_id', store=True)
    institute_id = fields.Many2one('odoocms.institute', 'Institute', related='program_id.institute_id', store=True)
    discipline_id = fields.Many2one('odoocms.discipline', 'Discipline', related='student_id.discipline_id', store=True)
    campus_id = fields.Many2one('odoocms.campus', 'Campus', related='institute_id.campus_id', store=True)

    date_request = fields.Date('Date Request', default=date.today(), readonly=True)
    date_approve = fields.Date('Date Approve', readonly=True)
    date_done = fields.Datetime('Date Award', readonly=True)

    attachment = fields.Binary('Attachment',  attchment=True, readonly=True)

    state = fields.Selection(
        [('draft', 'Draft'), ('submit', 'Submit'), ('invoice', 'Invoice'), ('approve', 'Approved'),
         ('cancel', 'Cancel'), ('done', 'Done')], default='draft', string="Status", tracking=True)
    invoice_created = fields.Boolean(string='Invoice Created')

    def action_submit(self):
        for rec in self:
            if rec.have_invoice_paid():
                activity = self.env.ref('odoocms_exam.mail_act_transcript_request')
                self.activity_schedule('odoocms_exam.mail_act_transcript_request', user_id=activity._get_role_users(self.program_id))

                rec.state = 'submit'
            else:
                raise UserError('Fee Not paid Yet.')

    def action_approve(self):
        for rec in self:
            if rec.state == 'submit':
                pdf_content, input_pdf_report_path = rec.student_id.gen_transcript()
                rec.attachment = base64.encodestring(pdf_content)

                rec.state = 'approve'
                rec.date_approve = date.today()
            else:
                raise UserError('Request is not Submitted yet.')

    def action_cancel(self):
        pass

    def have_invoice_paid(self):
        return True

    def action_award(self):
        for rec in self:
            rec.state = 'done'
            rec.date_done = datetime.today()