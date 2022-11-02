
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.osv import expression
import pdb


class OdooCMSClassAttendance(models.Model):
    _name = 'odoocms.class.attendance'
    _description = 'Student Attendance Register'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    READONLY_STATES = {
        'done': [('readonly', True)],
    }

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    class_id = fields.Many2one('odoocms.class', string='Class')
    term_id = fields.Many2one('odoocms.academic.term', string='Term', related='class_id.term_id', store=True)
    batch_id = fields.Many2one('odoocms.batch', string='Batch', related='class_id.batch_id', store=True)
    program_id = fields.Many2one('odoocms.program', string='Program', related='batch_id.program_id', store=True)
    department_id = fields.Many2one('odoocms.department', string='Department', related='program_id.department_id', store=True)
    institute_id = fields.Many2one('odoocms.institute', string='School', related='department_id.institute_id', store=True)
    
    faculty_id = fields.Many2one(related='class_id.faculty_staff_id', string='Faculty', store=True)
    date_schedule = fields.Date(string='Scheduled Date', default=fields.Date.today, required=True)
    date_class = fields.Date(string='Class Date', default=fields.Date.today, required=True, states = READONLY_STATES)
    date_att = fields.Date(string='Att. Date')
    time_from = fields.Float(string='From', required=True, index=True, help="Start and End time of Period.", states = READONLY_STATES)
    time_to = fields.Float(string='To', required=True, states = READONLY_STATES)
    makeup_class = fields.Boolean('Makeup Class',default=False)
    
    attendance_created = fields.Boolean(string='Attendance Created')
    att_marked = fields.Boolean('Marked',default=False)
    
    all_marked = fields.Boolean(string='All Students are Present',default=True)
    state = fields.Selection([
        ('draft', 'To be Marked'),
        ('done', 'Marked'),
        ('lock','Locked')], default='draft')
    attendance_lines = fields.One2many('odoocms.class.attendance.line', 'attendance_id', string='Attendance Lines')
    can_edit = fields.Boolean('Can Edit',compute='_can_edit')
    to_be = fields.Boolean()

    _sql_constraints = [
        ('unique_classtime', 'unique(class_id,date_class,time_from)', "Another Class scheduled at the same time!"),
    ]

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('odoocms.class.attendance') or _('New')
        result = super().create(vals)
        return result

    def create_attendance_lines(self):
        attendance_line_obj = self.env['odoocms.class.attendance.line']
        registrations = self.class_id.sudo().registration_component_ids
        # if len(registrations) < 1:
        #     raise UserError(_('There are no students in this Class Section'))
        attendance_lines = self.attendance_lines
        flag = 0
        for reg in registrations:
            if reg.student_course_id.grade not in ('W','F','XF') and \
                    ((not reg.student_course_id.date_effective) or reg.student_course_id.date_effective <= self.date_class):
                attendance_line = attendance_lines.filtered(lambda l: l.student_id.id == reg.student_id.id)
                if attendance_line:
                    attendance_lines -= attendance_line
                else:
                    data = {
                        'attendance_id': self.id,
                        'student_id': reg.student_id.id,
                        'student_name': reg.student_id.name,
                        'class_id': self.class_id.id,
                    }
                    flag = 1
                    attendance_line_obj.create(data)
        if flag:
            self.attendance_created = True
        attendance_lines.unlink()
        self.to_be = False
        
    def mark_all_present(self):
        for records in self.attendance_lines:
            records.present = True
        self.all_marked = True

    def unmark_all_present(self):
        for records in self.attendance_lines:
            records.present = False
        self.all_marked = False

    def attendance_marked(self):   # This will alse be called from a cron job
        all_marked = True
        for line in self.attendance_lines:
            if (not line.present) and (not line.reason_id):
                all_marked = False
        if all_marked:
            self.date_att = date.today()
            self.state = 'done'
            self.att_marked = True

    def set_to_draft(self):
        self.state = 'draft'
        self.att_marked = False

    @api.constrains('date_class','batch_id','time_from','time_to')
    def check_date(self):
        for rec in self:
            if rec.time_from <= 0:
                raise UserError('Time From should be Positive')
            if rec.time_to <= 0:
                raise UserError('Time To should be Positive')
            if rec.time_from >= rec.time_to:
                raise UserError('Time From should not exceed Time To')
            
            if rec.batch_id and rec.date_class:
                term_line = rec.batch_id.getermline(rec.term_id)
                if term_line.date_start > rec.date_class:
                    raise UserError('Register date can not be earlier than %s' % (term_line.date_start,))
                if term_line.date_end < rec.date_class:
                    raise UserError('Register date can not be later than %s' % (term_line.date_end,))

    @api.onchange('date_schedule', 'date_class', 'date_att')
    def _can_edit(self):
        for rec in self:
            can_edit = True
            today = date.today()
            if (rec.date_class and rec.date_class > today) or (rec.date_schedule and rec.date_schedule) > today or (rec.date_att and rec.date_att > today):
                can_edit = False
            if rec.state == 'lock':
                can_edit = False
            rec.can_edit = can_edit

    def _cron_lock_attendance(self):
        date_one = date.today() + relativedelta(day=1)
        att_recs = self.env['odoocms.class.attendance'].search([('date_class','<',date_one),('state','in',('draft','done'))])
        att_recs.write({'state':'lock'})
    
    def _cron_generate_register(self):
        class_ids = self.env['odoocms.class'].search([('state','in',('current','draft'))])
        for class_id in class_ids:
            class_id.attendance_roaster(class_id.term_id, date.today(),date.today())
        
        # config_term = self.env['ir.config_parameter'].sudo().get_param('odoocms.current_term')
        # if config_term:
        #     config_term = int(config_term)
        #     batch_ids = self.env['odoocms.batch'].search([('term_id','=',config_term)])
        #     for batch in batch_ids:
        #         batch.attendance_roaster(date.today(),date.today())
                
    
class OdooCMSClassAttendanceLine(models.Model):
    _name = 'odoocms.class.attendance.line'
    _description = 'Student Attendance'
    _order = "student_id"

    READONLY_STATES = {
        'done': [('readonly', True)],
    }

    attendance_id = fields.Many2one('odoocms.class.attendance', string='Attendance ID',ondelete='cascade')
    student_id = fields.Many2one('odoocms.student', string='Student')
    student_name = fields.Char(string='Student Name', related='student_id.name', store=True)
    class_id = fields.Many2one('odoocms.class', string='Class', required=True)

    student_course_component_id = fields.Many2one('odoocms.student.course.component', string='Student Course', compute='_get_student_course', store=True)
    
    date_class = fields.Date(string='Date', related='attendance_id.date_class',store=True)
    present = fields.Boolean(string='Present',default=True, states = READONLY_STATES)
    reason_id = fields.Many2one('odoocms.attendance.absent.reason','Absent Reason', states = READONLY_STATES)
    state = fields.Selection(string='State', related='attendance_id.state',store=True)
    term_id = fields.Many2one('odoocms.academic.term', string='Academic Term', related='class_id.term_id', store=True)
    left_early = fields.Boolean('Left Early',default=False)
    came_late = fields.Boolean('Came Late',default=False)
    remarks = fields.Text(string='Remarks')
    
    @api.depends('student_id','class_id','term_id')
    def _get_student_course(self):
        for rec in self:
            student_component = self.env['odoocms.student.course.component'].search([('student_id','=',rec.student_id.id),('class_id','=',rec.class_id.id),('term_id','=',rec.term_id.id)])
            if student_component:
                rec.student_course_component_id = student_component.id

    @api.onchange('present')
    def _onchange_present(self):
        if not self.present:
            absent = self.env['odoocms.attendance.absent.reason'].search([('name', '=', 'Absent')])
            if absent:
                self.reason_id = absent[0].id
                
        
class OdooCMSClassAttendanceOpen(models.Model):
    _name = 'odoocms.class.attendance.open'
    _description = 'Student Attendance Unlock'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    READONLY_STATES = {
        'approve': [('readonly', True)],
        'refuse': [('readonly', True)],
        'lock': [('readonly', True)],
    }

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    term_id = fields.Many2one('odoocms.academic.term', string='Academic Term', states = READONLY_STATES)
    faculty_id = fields.Many2one('odoocms.faculty.staff', string='Faculty', states = READONLY_STATES)
    batch_ids = fields.Many2many('odoocms.batch', string='Batches', states = READONLY_STATES)
    class_ids = fields.Many2many('odoocms.class', string='Component Classes', states = READONLY_STATES)
    program_ids = fields.Many2many('odoocms.program', string='Programs', states = READONLY_STATES)
    department_ids = fields.Many2many('odoocms.department', string='Departments', states = READONLY_STATES)
    institute_ids = fields.Many2many('odoocms.institute', string='Schools', states = READONLY_STATES)
    level = fields.Selection([
        ('institute','Institute'),
        ('department','Department'),
        ('program','Program'),
        ('component','Component Class'),
        ('batch','Batch')],string='Level',default='batch', states = READONLY_STATES)
    
    date_from = fields.Date('Date From', states = READONLY_STATES)
    date_to = fields.Date('Date To', states = READONLY_STATES)
    date_lock = fields.Date('Lock Date', states = READONLY_STATES)
    state = fields.Selection([
        ('draft','Draft'),
        ('submit','Submit'),
        ('approve','Approved'),
        ('refuse','Refused'),
        ('lock','Locked')],
        string='Status',default='draft')
    att_class_ids = fields.Many2many('odoocms.class.attendance',string='Attendance Classes', states = READONLY_STATES)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('odoocms.class.attendance.open') or _('New')
        result = super().create(vals)
        return result
    
    def get_att_classes(self):
        domain = [
            ('term_id','=',self.term_id.id),
            ('date_class','>=',self.date_from),
            ('date_class','<=',self.date_to),
            ('state','=','lock')
        ]
        if self.level == 'batch' and self.batch_ids:
            domain = expression.AND([domain, [('batch_id', 'in', self.batch_ids.ids)]])
        elif self.level == 'program' and self.program_ids:
            # batch_ids = self.env['odoocms.batch'].search([('program_id','in',self.program_ids.ids)])
            domain = expression.AND([domain, [('program_id', 'in', self.program_ids.ids)]])
        elif self.level == 'department' and self.department_ids:
            domain = expression.AND([domain, [('department_id', 'in', self.department_ids.ids)]])
        elif self.level == 'institute' and self.institute_ids:
            domain = expression.AND([domain, [('institute_id', 'in', self.institute_ids.ids)]])
        elif self.level == 'component' and self.class_ids:
            domain = expression.AND([domain, [('class_id', 'in', self.class_ids.ids)]])
            
        classes = self.env['odoocms.class.attendance'].search(domain)
        self.att_class_ids = [(6,0,classes.ids)]
        
    def submit(self):
        self.state = 'submit'
        
    def approve(self):
        self.state = 'approve'
        for att_class in self.att_class_ids:
            att_class.state = 'done' if att_class.att_marked else 'draft'
        
    def refuse(self):
        self.state = 'refuse'
        
    def _cron_lock_attendance(self):
        date_today = date.today()
        lock_recs = self.env['odoocms.class.attendance.open'].search([
            ('date_lock','<',date_today),('state','=','approve')])
        for lock_rec in lock_recs:
            lock_rec.write({'state':'lock'})
            lock_rec.att_class_ids.state = 'lock'


class OdooCMSAttendanceAbsentReason(models.Model):
    _name = 'odoocms.attendance.absent.reason'
    _description = 'Student Attendance Absent Reason'

    name = fields.Char('Absent Reason', tracking=True)
    code = fields.Char('Code', required=True, tracking=True)
    present = fields.Boolean('Consider as Present', tracking=True)
    absent = fields.Boolean('Consider as Absent', tracking=True)

    
class OdooCMSBatch(models.Model):
    _inherit = 'odoocms.batch'

    def attendance_roaster(self, term_id, date_from, date_to):
        att_classes = self.env['odoocms.class.attendance']
        pub_holiday = []
        pub_holiday_search = self.env['odoocms.holidays.public'].search([('term_id', '=', term_id.id)])
        for ho in pub_holiday_search:
            pub_holiday.append(ho.date)

        ex_registers = self.env['odoocms.class.attendance'].search([
            ('batch_id', '=', self.id), ('date_class', '>=', date_from), ('att_marked', '=', False)])

        term_line = self.getermline(term_id)
        if not term_line:
            raise UserError('Term Line not defined for %s' % (self.name,))

        # .with_progress(msg="Schedule Classes")
        dt = date_from
        while dt <= date_to:
            if term_line.date_start <= dt and term_line.date_end >= dt:
                weekdays = self.env['odoocms.week.day'].search([('number', '=', dt.weekday() + 1)])
                schedules = self.env['odoocms.timetable.schedule'].search([
                    ('term_id','=',term_id.id),('batch_id', '=', self.id)]).filtered(
                    lambda l: weekdays in l.week_day_ids)
            
                for schedule in schedules:
                    if dt not in pub_holiday:
                        class_exist = self.env['odoocms.class.attendance'].search([
                            ('class_id','=',schedule.class_id.id),
                            ('date_class','=', dt),
                            ('time_from','=',schedule.time_from)
                        ])
                        ex_registers -= class_exist
                        if not class_exist:
                            data = {
                                'class_id': schedule.class_id.id,
                                'faculty_id': schedule.faculty_id.id,
                                'date_schedule': dt,
                                'date_class': dt,
                                'time_from': schedule.time_from,
                                'time_to': schedule.time_to,
                            }
                            att_class = self.env['odoocms.class.attendance'].sudo().create(data)
                            if att_class:
                                att_class.create_attendance_lines()
                                att_classes += att_class
            dt = dt + relativedelta(days=1)

        ex_registers.unlink()
        return att_classes


class OdooCMSClass(models.Model):
    _inherit = 'odoocms.class'

    def attendance_roaster(self, term_id, date_from, date_to):
        att_classes = self.env['odoocms.class.attendance']
        pub_holiday = []
        pub_holiday_search = self.env['odoocms.holidays.public'].search([('term_id', '=', self.term_id.id)])
        for ho in pub_holiday_search:
            pub_holiday.append(ho.date)

        ex_registers = self.env['odoocms.class.attendance'].search([
            ('class_id', '=', self.id), ('date_class', '>=', date_from),('att_marked','=',False)])

        if self.batch_id:
            term_line = self.batch_id.getermline(term_id)
            if not term_line:
                raise UserError('Term Line not defined for %s' % (self.name,))
            date_start = term_line.date_start
            date_end = term_line.date_end
        else:
            date_start = date.today()
            date_end = date.today()-relativedelta(years=5)
            for term in term_id.term_lines:
                if term.date_start < date_start:
                    date_start = term.date_start
                if term.date_end > date_end:
                    date_end = term.date_end
                    
        # .with_progress(msg="Schedule Classes")
        dt = date_from
        while dt <= date_to:
            if date_start <= dt and date_end >= dt:
                weekdays = self.env['odoocms.week.day'].search([('number', '=', dt.weekday() + 1)])
                schedules = self.env['odoocms.timetable.schedule'].search([
                    ('class_id', '=', self.id)]).filtered(
                    lambda l: weekdays in l.week_day_ids)
            
                for schedule in schedules:
                    if dt not in pub_holiday:
                        class_exist = self.env['odoocms.class.attendance'].search([
                            ('class_id', '=', schedule.class_id.id),
                            ('date_class', '=', dt),
                            ('time_from', '=', schedule.time_from)
                        ])
                        ex_registers -= class_exist
                        if not class_exist:
                            data = {
                                'class_id': schedule.class_id.id,
                                'faculty_id': schedule.faculty_id.id,
                                'date_schedule': dt,
                                'date_class': dt,
                                'time_from': schedule.time_from,
                                'time_to': schedule.time_to,
                            }
                            att_class = self.env['odoocms.class.attendance'].create(data)
                            if att_class:
                                att_class.create_attendance_lines()
                                att_classes += att_class
            dt = dt + relativedelta(days=1)
        
        ex_registers.unlink()
        return att_classes


