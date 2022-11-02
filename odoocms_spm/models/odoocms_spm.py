from odoo import models, fields, _, api
from odoo.exceptions import ValidationError
import datetime
from datetime import date, timedelta


class OdooCMSStudentProjectManagement(models.Model):
    _name = 'odoocms.student.project'
    _description = 'Student Project Management'
    _rec_name = 'project_number'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    READONLY_STATES = {
        'confirm': [('readonly', True)],
        'accept': [('readonly', True)],
        'reject': [('readonly', True)],
    }
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('accept', 'Accept'),
                              ('reject', 'Reject')],
                             'Status', default='draft')

    project_number = fields.Char(string='Project Number', default=lambda self:self.env['ir.sequence'].next_by_code('odoocms.student.project'), copy=False, readonly=True)
    project_title = fields.Char(string="Project Title", help="Title Of Student Desired Project ",required='True', track_visibility='onchange', states=READONLY_STATES)
    status = fields.Boolean('Active', default=True,
                            help="Current Status of Project")
    checklist_progress = fields.Float(string='Progress',digits=(12,2), store=True, default=0.0, compute='compute_progress')

    date_start = fields.Date(string='Start Date', states=READONLY_STATES)
    date_end = fields.Date(string='End Date', states=READONLY_STATES)
    default_projects = fields.Many2one('odoocms.projects',states=READONLY_STATES,string="Default Project List")
    supervisor = fields.Many2one('odoocms.faculty.staff', string='Supervisor',required='True',tracking=True)
    co_supervisor = fields.Many2one('odoocms.faculty.staff',
                                    string='CoSupervisor',required='True',tracking=True)


    student_ids = fields.Many2many('odoocms.student', 'project_student_rel', 'project_id', 'student_id', 'Students')
    faculty_ids = fields.Many2many('odoocms.faculty.staff', 'project_faculty_rel', 'project_id', 'faculty_id', 'Faculty',tracking=True)
    project_document_ids = fields.One2many('odoocms.spm.document.lines', 'project_id', 'Project Documents')
    selected_milestone_ids = fields.One2many('odoocms.student.project.checklist.lines', 'project_id',string='Selected Milestones')
    feedback_ids = fields.One2many('odoocms.spm.feedback.lines', 'project_id',string='Feedbacks')

    description = fields.Text(string='Description', help="Description about the Project",states=READONLY_STATES)
    short_description = fields.Text(string='Short Description', help="Short Description about the Project",states=READONLY_STATES)
    formal_description = fields.Text(string='Formal Description', help="Formal Description about the Project",states=READONLY_STATES)
    email_id = fields.Char(string='Email')
    supervisor_feedback = fields.Html(string="Supervisor Feedback from portal")
    supervisor_meeting_link = fields.Text(string="Supervisor Meeting link for student")
    co_supervisor_feedback = fields.Html(string="Supervisor Feedback from portal")
    student_message = fields.Text(string="Supervisor Message from portal")

    _sql_constraints = [
        ('project_number', 'unique(project_number)', "project_number already exists for another Project!"),
    ]


    @api.onchange('default_projects')
    def set_project(self):
        for rec in self:
            rec.project_title = self.default_projects.name
            rec.description = self.default_projects.description
            rec.short_description = self.default_projects.short_description
            rec.formal_description = self.default_projects.formal_description



    @api.depends('selected_milestone_ids')
    def compute_progress(self):
        count = 0
        if self.selected_milestone_ids:
            total = len(self.selected_milestone_ids)
            for rec in self.selected_milestone_ids:
                if rec.complition_status == True:
                    count = count + 1;
            if total != 0:
                self.checklist_progress = (count * 100) / total

    def action_confirm(self):
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'confirm'

    def action_accept(self):
        for rec in self:
            if rec.state == 'confirm':
                rec.state = 'accept'

    def action_reject(self):
        for rec in self:
            if rec.state != 'accept':
                rec.state = 'reject'


    def alert_cron_job(self):
        projects = self.env['odoocms.student.project'].search([])
        today_date = date.today()
        notification = self.env['cms.notification'].sudo().search([])
        notification_values = {}
        User_ids = []
        for project in projects:
            if project.selected_milestone_ids:
                for student in project.student_ids:
                    if student.user_id:
                        User_ids.append(student.user_id.id)
                notification_values['recipient_ids'] = [(6, 0, User_ids)]

                for milestone in project.selected_milestone_ids:
                    if milestone.end_date:
                        sevenday_before_date = milestone.end_date - timedelta(7)
                        if today_date >= sevenday_before_date:
                               notification_values = {
                                   'recipient_ids': User_ids,
                                   'description': "You are getting late for your " + milestone.display_name + " milestone achievement",
                                   'allow_preview': True,
                                   'name': 'Milestone Date Overdue',
                                   'visible_for': 'student',
                                   'alert':True,
                                   'expiry': date.today() + timedelta(7)
                               }
                               notification.sudo().create(notification_values)
                        if today_date >= milestone.end_date:
                           notification_values = {
                               'recipient_ids': User_ids,
                               'description': "You have missed your " + milestone.display_name + " milestone achievement",
                               'allow_preview': True,
                               'name': 'Milestone missed',
                               'visible_for': 'student',
                               'alert': True,
                               'expiry':date.today() + timedelta(7)
                           }
                           notification.sudo().create(notification_values)
                           notification_values = {}
         # print(self)

    @api.constrains('date_start', 'date_end')
    def validate_date(self):
        for rec in self:
            start_date = fields.Date.from_string(rec.date_start)
            end_date = fields.Date.from_string(rec.date_end)
            if start_date and end_date:
                if start_date >= end_date:
                    raise ValidationError(_('Start Date must be Anterior to End Date'))

    @api.model
    def create(self, values):
        if values.get('student_ids', False):
            students = self.env['odoocms.student'].search([('id', 'in', values['student_ids'][0][2])])
            for student in students:
                withdraw_student = student.tag_ids.filtered(lambda tg: tg.name == 'Withdrawal')
                if withdraw_student:
                    raise ValidationError('Wrong Student is added having Withdraw tag please verify')

            projects = self.env['odoocms.student.project'].search([('student_ids', 'in', values['student_ids'][0][2])])
        if projects:
            for project in projects:
                if project.state =='reject':
                    pass
                else:
                    raise ValidationError('Student already added in to another project: %s' % (project.project_title,))
        if values.get('co_supervisor',False) == values.get('supervisor'):
            raise ValidationError('Supervisor and Cosupervisor should not be Same')

        for value in values.get('faculty_ids',False)[0][2]:
            if value == values.get('supervisor', False) or value == values.get('co_supervisor', False):
                 raise ValidationError('Supervisors and GEC Members should not be Same')
        else:
            return super(OdooCMSStudentProjectManagement, self).create(values)


class odooCMSProjects(models.Model):
    _name = 'odoocms.projects'
    _description = 'List of Projects'
    _rec_name = 'name'
    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    description = fields.Text(string='Description', help="Description about the Project")
    short_description = fields.Text(string='Short Description', help="Short Description about the Project")
    formal_description = fields.Text(string='Formal Description', help="Formal Description about the Project")


class odooCMSSPMDocumentLines(models.Model):
    _name = 'odoocms.spm.document.lines'
    _description = 'SPM Documents'

    document_title = fields.Char(string='Document Name')
    document_code = fields.Char(string='Document Code')
    # attachment = True
    attachment_file = fields.Binary(string="Attachments", )
    milestone_id = fields.Many2one('odoocms.student.project.milestone', string='Related MileStone')
    project_id = fields.Many2one('odoocms.student.project',string="Project")


class odooCMSSPMFeedbackLines(models.Model):
    _name = 'odoocms.spm.feedback.lines'
    _description = 'SPM Feedback'

    feedback = fields.Html(
         string='Feedback',
         required=False)
    milestone_id = fields.Many2one('odoocms.student.project.milestone', string='Related MileStone')
    project_id = fields.Many2one('odoocms.student.project',string="project")

class odooCMSSPMCheckListLines(models.Model):
    _name = 'odoocms.student.project.checklist.lines'
    _description = 'SPM Checklist Lines'

    milestone_id = fields.Many2one('odoocms.student.project.milestone', string='Mile Stones')
    name = fields.Char(related='milestone_id.name', string='Name', help='Name of Mile Stone')
    code = fields.Char(related='milestone_id.code', string='Code', help='Code of Mile Stone')
    effective_date = fields.Date(related='milestone_id.effective_date', string='Effective Date', help='Effective Date of MileStone')
    status = fields.Boolean('Active', default=True,
                            help="Current Status of MileStone")
    start_date = fields.Date(string='Start Date', help='Start Date of MileStone')
    end_date = fields.Date(string='End Date', help='End Date of MileStone')
    complition_date = fields.Date(string='Completion Date', help='Completion Date of MileStone')
    complition_status = fields.Boolean('Completed', default=False, help="Current Status of MileStone")
    project_id = fields.Many2one('odoocms.student.project',string= "Project")


    @api.onchange('complition_status')
    def _onchange_completion_status(self):
        if (self.complition_status == True):
            self.complition_date = str(datetime.date.today())
        else:
            self.complition_date = ''



    @api.constrains('start_date', 'end_date')
    def validate_date(self):
        for rec in self:
            start_date = fields.Date.from_string(rec.start_date)
            end_date = fields.Date.from_string(rec.end_date)
            if start_date and end_date:
                if start_date >= end_date:
                    raise ValidationError(_('Start Date must be Anterior to End Date'))

    # @api.onchange('complition_status')
    # def check_approval(self):
    #     for rec in self:
    #         project = self.env(['odoocms.student.project']).search([('id','=','rec.project_id')])
    #         if project.state != 'approved':
    #             raise ValidationError(_('Completion Status Can Only Be Change on Approved State'))
    #         else:
    #             return
