# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class OdooCMSFacultyHostelSwap(models.Model):
    _name = 'odoocms.faculty.hostel.swap'
    _description = "Faculty Hostel Swap"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    name = fields.Char('Name', tracking=True)
    sequence = fields.Char('Sequence')

    applicant_faculty_id = fields.Many2one('odoocms.faculty.staff', 'Faculty', tracking=True, readonly=True, states={'Draft': [('readonly', False)]})
    applicant_registration_no = fields.Char('Faculty ID', tracking=True, readonly=True, states={'Draft': [('readonly', False)]})
    applicant_gender = fields.Selection(related='applicant_faculty_id.gender', string='Applicant Gender', store=True)

    applicant_email = fields.Char('Email', readonly=True, states={'Draft': [('readonly', False)]})
    applicant_mobile = fields.Char('Mobile', readonly=True, states={'Draft': [('readonly', False)]})

    applicant_hostel_id = fields.Many2one('odoocms.hostel', 'Hostel', compute='compute_applicant_hostel_data', store=True)
    applicant_room_id = fields.Many2one('odoocms.hostel.room', 'Room', compute='compute_applicant_hostel_data', store=True)
    applicant_room_type = fields.Many2one('odoocms.hostel.room.type', 'Room Type', compute='compute_applicant_hostel_data', store=True)

    swap_with_faculty_id = fields.Many2one('odoocms.faculty.staff', 'Swap With faculty', tracking=True, readonly=True, states={'Draft': [('readonly', False)]})
    swap_with_registration_no = fields.Char('Swap Faculty ID', tracking=True, readonly=True, states={'Draft': [('readonly', False)]})
    swap_with_gender = fields.Selection(related='swap_with_faculty_id.gender', string='Swap With Gender', store=True)

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
            values['name'] = self.env['ir.sequence'].next_by_code('odoocms.faculty.hostel.swap')
        result = super(OdooCMSFacultyHostelSwap, self).create(values)
        return result

    def unlink(self):
        return super(OdooCMSFacultyHostelSwap, self).unlink()

    @api.onchange('applicant_faculty_id')
    def onchange_applicant_faculty_id(self):
        for rec in self:
            faculty_id = rec.applicant_faculty_id
            if faculty_id:
                rec.applicant_registration_no = faculty_id.identification_id or ''
                rec.applicant_mobile = faculty_id.mobile_phone or ''
                rec.applicant_email = faculty_id.work_email or ''

    @api.onchange('swap_with_faculty_id')
    def onchange_swap_with_faculty_id(self):
        for rec in self:
            faculty_id = rec.swap_with_faculty_id
            if faculty_id:
                rec.swap_with_registration_no = faculty_id.identification_id or ''
                rec.swap_with_hostel_id = faculty_id.hostel_id and faculty_id.hostel_id.id or False
                rec.swap_with_room_id = faculty_id.room_id and faculty_id.room_id.id or False
                rec.swap_with_room_type = faculty_id.room_type and faculty_id.room_type.id or False
                rec.swap_with_mobile = faculty_id.mobile_phone or ''
                rec.swap_with_email = faculty_id.work_email or ''

    @api.constrains('applicant_faculty_id', 'swap_with_faculty_id')
    def facultys_constrains(self):
        for rec in self:
            if rec.applicant_faculty_id.id==rec.swap_with_faculty_id.id:
                raise ValidationError(_("Applicant faculty And Swap With Should not be the Same faculty"))

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
                rec.applicant_faculty_id.hostel_id = rec.swap_with_hostel_id and rec.swap_with_hostel_id.id or False
            if rec.swap_with_room_id:
                rec.applicant_faculty_id.room_id = rec.swap_with_room_id and rec.swap_with_room_id.id or False
            if rec.swap_with_room_type:
                rec.applicant_faculty_id.room_type = rec.swap_with_room_type and rec.swap_with_room_type.id or False

            if hostel_id:
                rec.swap_with_faculty_id.hostel_id = hostel_id
            if room_id:
                rec.swap_with_faculty_id.room_id = room_id
            if room_type:
                rec.swap_with_faculty_id.room_type = room_type

            applicant_history_vals = {
                'faculty_id': rec.applicant_faculty_id.id,
                'faculty_code': rec.applicant_registration_no and rec.applicant_registration_no or '',
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
            new_rec = self.env['odoocms.faculty.hostel.history'].create(applicant_history_vals)
            new_rec.hostel_swap_id = rec.id

            swap_with_history_vals = {
                'faculty_id': rec.swap_with_faculty_id.id,
                'faculty_code': rec.swap_with_registration_no and rec.swap_with_registration_no or '',
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
            swapped_with_new_rec = self.env['odoocms.faculty.hostel.history'].create(swap_with_history_vals)
            swapped_with_new_rec.hostel_swap_id = rec.id
            rec.state = 'Approved'

    def action_rejected(self):
        for rec in self:
            rec.state = 'Rejected'

    @api.depends('applicant_faculty_id')
    def compute_applicant_hostel_data(self):
        for rec in self:
            rec.applicant_hostel_id = rec.applicant_faculty_id.hostel_id and rec.applicant_faculty_id.hostel_id.id or False
            rec.applicant_room_id = rec.applicant_faculty_id.room_id and rec.applicant_faculty_id.room_id.id or False
            rec.applicant_room_type = rec.applicant_faculty_id.room_type and rec.applicant_faculty_id.room_type.id or False

    @api.depends('swap_with_faculty_id')
    def compute_swap_with_hostel_data(self):
        for rec in self:
            rec.swap_with_hostel_id = rec.swap_with_faculty_id.hostel_id and rec.swap_with_faculty_id.hostel_id.id or False
            rec.swap_with_room_id = rec.swap_with_faculty_id.room_id and rec.swap_with_faculty_id.room_id.id or False
            rec.swap_with_room_type = rec.swap_with_faculty_id.room_type and rec.swap_with_faculty_id.room_type.id or False
