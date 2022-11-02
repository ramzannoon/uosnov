# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import pdb


class OdooCMSStudentHostelSwap(models.Model):
    _name = 'odoocms.student.hostel.swap'
    _description = "Student Hostel Swap"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    name = fields.Char('Name', tracking=True)
    sequence = fields.Char('Sequence')

    applicant_student_id = fields.Many2one('odoocms.student', 'Student', tracking=True, readonly=True, states={'Draft': [('readonly', False)]})
    applicant_registration_no = fields.Char('Student ID', tracking=True, readonly=True, states={'Draft': [('readonly', False)]})
    applicant_gender = fields.Selection(related='applicant_student_id.gender', string='Applicant Gender', store=True)

    applicant_email = fields.Char('Email', readonly=True, states={'Draft': [('readonly', False)]})
    applicant_mobile = fields.Char('Mobile', readonly=True, states={'Draft': [('readonly', False)]})
    applicant_session_id = fields.Many2one('odoocms.academic.session', 'Academic Session', tracking=True, readonly=True, states={'Draft': [('readonly', False)]})
    applicant_program_id = fields.Many2one('odoocms.program', 'Academic Program', tracking=True, readonly=True, states={'Draft': [('readonly', False)]})
    applicant_career_id = fields.Many2one('odoocms.career', 'Academic Level', tracking=True, readonly=True, states={'Draft': [('readonly', False)]})

    applicant_hostel_id = fields.Many2one('odoocms.hostel', 'Hostel', compute='compute_applicant_hostel_data', store=True)
    applicant_room_id = fields.Many2one('odoocms.hostel.room', 'Room', compute='compute_applicant_hostel_data', store=True)
    applicant_room_type = fields.Many2one('odoocms.hostel.room.type', 'Room Type', compute='compute_applicant_hostel_data', store=True)

    swap_with_student_id = fields.Many2one('odoocms.student', 'Swap With Student', tracking=True, readonly=True, states={'Draft': [('readonly', False)]})
    swap_with_registration_no = fields.Char('Swap Student ID', tracking=True, readonly=True, states={'Draft': [('readonly', False)]})
    swap_with_gender = fields.Selection(related='swap_with_student_id.gender', string='Swap With Gender', store=True)

    swap_with_session_id = fields.Many2one('odoocms.academic.session', 'Swap With Academic Session', tracking=True,
        readonly=True, states={'Draft': [('readonly', False)]})
    swap_with_program_id = fields.Many2one('odoocms.program', 'Swap With Academic Program', tracking=True, readonly=True,
        states={'Draft': [('readonly', False)]})
    swap_with_career_id = fields.Many2one('odoocms.career', 'Swap With Academic Level', tracking=True, readonly=True, states={'Draft': [('readonly', False)]})
    swap_with_hostel_id = fields.Many2one('odoocms.hostel', 'Swap With Hostel', compute='compute_swap_with_hostel_data', store=True)
    swap_with_room_id = fields.Many2one('odoocms.hostel.room', 'Swap With Room', compute='compute_swap_with_hostel_data', store=True)
    swap_with_room_type = fields.Many2one('odoocms.hostel.room.type', 'Swap With Room Type', compute='compute_swap_with_hostel_data', store=True)

    swap_with_email = fields.Char('Swap With Email', readonly=True, states={'Draft': [('readonly', False)]})
    swap_with_mobile = fields.Char('Swap With Mobile', readonly=True, states={'Draft': [('readonly', False)]})

    submission_date = fields.Date('Submission Date', default=fields.Date.today(), readonly=True, states={'Draft': [('readonly', False)]})
    approved_date = fields.Date('Approved Date', readonly=True, states={'Draft': [('readonly', False)]}, tracking=True)
    state = fields.Selection([('Draft', 'Draft'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], 'Status', default='Draft')
    active = fields.Boolean('Active', default=True)
    remarks = fields.Text('Remarks')

    @api.model
    def create(self, values):
        if not values.get('name', False):
            values['name'] = self.env['ir.sequence'].next_by_code('odoocms.student.hostel.swap')
        result = super(OdooCMSStudentHostelSwap, self).create(values)
        return result

    def unlink(self):
        return super(OdooCMSStudentHostelSwap, self).unlink()

    @api.onchange('applicant_student_id')
    def onchange_applicant_student_id(self):
        for rec in self:
            student_id = rec.applicant_student_id
            if student_id:
                rec.applicant_registration_no = student_id.id_number and student_id.id_number or ''
                rec.applicant_session_id = student_id.session_id and student_id.session_id.id or False
                rec.applicant_program_id = student_id.program_id and student_id.program_id.id or False
                rec.applicant_career_id = student_id.career_id and student_id.career_id.id or False
                rec.applicant_mobile = student_id.mobile and student_id.mobile or ''
                rec.applicant_email = student_id.email and student_id.email or ''

    @api.onchange('swap_with_student_id')
    def onchange_swap_with_student_id(self):
        for rec in self:
            student_id = rec.swap_with_student_id
            if student_id:
                rec.swap_with_registration_no = student_id.id_number and student_id.id_number or ''
                rec.swap_with_session_id = student_id.session_id and student_id.session_id.id or False
                rec.swap_with_program_id = student_id.program_id and student_id.program_id.id or False
                rec.swap_with_career_id = student_id.career_id and student_id.career_id.id or False
                rec.swap_with_hostel_id = student_id.hostel_id and student_id.hostel_id.id or False
                rec.swap_with_room_id = student_id.room_id and student_id.room_id.id or False
                rec.swap_with_room_type = student_id.room_type and student_id.room_type.id or False
                rec.swap_with_mobile = student_id.mobile and student_id.mobile or ''
                rec.swap_with_email = student_id.email and student_id.email or ''

    @api.constrains('applicant_student_id', 'swap_with_student_id')
    def students_constrains(self):
        for rec in self:
            if rec.applicant_student_id.id==rec.swap_with_student_id.id:
                raise ValidationError(_("Applicant Student And Swap With Should not be the Same Student"))

    def action_approved(self):
        for rec in self:
            if not rec.applicant_gender == rec.swap_with_gender:
                raise UserError(_('Swapping Can be Done With Same Gender! \n '
                                  'Male can Swap With Male and Female can Swap Female, Cross Swapping is not allowed'))
            rec.approved_date = fields.Date.today()
            hostel_id = rec.applicant_hostel_id and rec.applicant_hostel_id.id or False
            room_id = rec.applicant_room_id and rec.applicant_room_id.id or False
            room_type = rec.applicant_room_id and rec.applicant_room_type.id or False

            if rec.swap_with_hostel_id:
                rec.applicant_student_id.hostel_id = rec.swap_with_hostel_id and rec.swap_with_hostel_id.id or False
            if rec.swap_with_room_id:
                rec.applicant_student_id.room_id = rec.swap_with_room_id and rec.swap_with_room_id.id or False
            if rec.swap_with_room_type:
                rec.applicant_student_id.room_type = rec.swap_with_room_type and rec.swap_with_room_type.id or False

            if hostel_id:
                rec.swap_with_student_id.hostel_id = hostel_id
            if room_id:
                rec.swap_with_student_id.room_id = room_id
            if room_type:
                rec.swap_with_student_id.room_type = room_type

            applicant_history_vals = {
                'student_id': rec.applicant_student_id.id,
                'student_code': rec.applicant_registration_no and rec.applicant_registration_no or '',
                'session_id': rec.applicant_session_id and rec.applicant_session_id.id or False,
                'program_id': rec.applicant_program_id and rec.applicant_program_id.id or False,
                'career_id': rec.applicant_career_id and rec.applicant_career_id.id or False,
                'request_date': rec.submission_date,
                'allocate_date': rec.approved_date,
                'request_type': 'Swap',
                'state': 'Done',
                'active': True,
                'hostel_id': rec.swap_with_hostel_id and rec.swap_with_hostel_id.id or False,
                'room_id': rec.swap_with_room_id and rec.swap_with_room_id.id or False,
                'room_type': rec.swap_with_room_type and rec.swap_with_room_type.id or False,
                'previous_hostel_id': hostel_id and hostel_id or False,
                'previous_room_id': room_id and room_id or False,
            }
            new_rec = self.env['odoocms.student.hostel.history'].create(applicant_history_vals)
            new_rec.hostel_swap_id = rec.id

            swap_with_history_vals = {
                'student_id': rec.swap_with_student_id.id,
                'student_code': rec.swap_with_registration_no and rec.swap_with_registration_no or '',
                'session_id': rec.swap_with_session_id and rec.swap_with_session_id.id or False,
                'program_id': rec.swap_with_program_id and rec.swap_with_program_id.id or False,
                'career_id': rec.swap_with_career_id and rec.applicant_career_id.id or False,
                'request_date': rec.submission_date,
                'allocate_date': rec.approved_date,
                'request_type': 'Swap',
                'state': 'Done',
                'active': True,
                'hostel_id': rec.applicant_hostel_id and rec.applicant_hostel_id.id or False,
                'room_id': rec.applicant_room_id and rec.applicant_room_id.id or False,
                'room_type': rec.applicant_room_type and rec.applicant_room_type.id or False,
                'previous_hostel_id': rec.swap_with_hostel_id and rec.swap_with_hostel_id.id or False,
                'previous_room_id': rec.swap_with_room_id.id and rec.swap_with_room_id.id or False,
            }
            swapped_with_new_rec = self.env['odoocms.student.hostel.history'].create(swap_with_history_vals)
            swapped_with_new_rec.hostel_swap_id = rec.id
            rec.state = 'Approved'

    def action_rejected(self):
        for rec in self:
            rec.state = 'Rejected'

    @api.depends('applicant_student_id')
    def compute_applicant_hostel_data(self):
        for rec in self:
            rec.applicant_hostel_id = rec.applicant_student_id.hostel_id and rec.applicant_student_id.hostel_id.id or False
            rec.applicant_room_id = rec.applicant_student_id.room_id and rec.applicant_student_id.room_id.id or False
            rec.applicant_room_type = rec.applicant_student_id.room_type and rec.applicant_student_id.room_type.id or False

    @api.depends('swap_with_student_id')
    def compute_swap_with_hostel_data(self):
        for rec in self:
            rec.swap_with_hostel_id = rec.swap_with_student_id.hostel_id and rec.swap_with_student_id.hostel_id.id or False
            rec.swap_with_room_id = rec.swap_with_student_id.room_id and rec.swap_with_student_id.room_id.id or False
            rec.swap_with_room_type = rec.swap_with_student_id.room_type and rec.swap_with_student_id.room_type.id or False
