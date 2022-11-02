# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import pdb


class OdooCMSStudentHostelMultiSwap(models.Model):
    _name = 'odoocms.student.hostel.multi.swap'
    _description = "Student Hostel Multi Swap"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    name = fields.Char('Name')
    sequence = fields.Char('Sequence')
    date = fields.Date('Date', default=fields.Date.today(), readonly=True, states={'Draft': [('readonly', False)]})
    approved_date = fields.Date('Approved Date', readonly=True, states={'Draft': [('readonly', False)]}, tracking=True)
    state = fields.Selection([('Draft', 'Draft'),
                              ('Approved', 'Approved'),
                              ('Rejected', 'Rejected')], 'Status', default='Draft')
    line_ids = fields.One2many('odoocms.student.hostel.multi.swap.line', 'multi_swap_id', 'Lines')
    remarks = fields.Text('Remarks')

    @api.model
    def create(self, values):
        if not values.get('name', False):
            values['name'] = self.env['ir.sequence'].next_by_code('odoocms.student.hostel.multi.swap')
        result = super(OdooCMSStudentHostelMultiSwap, self).create(values)
        return result

    def unlink(self):
        for rec in self:
            if rec.state!='Draft':
                raise UserError('Only Draft Entries Can be Delete.')
            if rec.line_ids:
                rec.line_ids.unlink()
        return super(OdooCMSStudentHostelMultiSwap, self).unlink()

    def action_approved(self):
        for rec in self:
            if rec.line_ids:
                rec.line_ids.create_hostel_entry()
            else:
                raise UserError('There is not Line Detail, Please Enter the Detail then Try it.')
            rec.line_ids.write({'state': 'Approved'})
            rec.approved_date = fields.Date.today()
            rec.state = 'Approved'

    def action_rejected(self):
        for rec in self:
            if rec.line_ids:
                rec.line_ids.write({'state': 'Rejected'})
            rec.state = 'Rejected'


class OdooCMSStudentHostelMultiSwapLine(models.Model):
    _name = 'odoocms.student.hostel.multi.swap.line'
    _description = "Student Hostel Multi Swap Line"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence')
    student_id = fields.Many2one('odoocms.student', 'Student', index=True, tracking=True)
    student_reg_no = fields.Char('Student Reg No.')
    gender = fields.Selection(related='student_id.gender', string='Gender', store=True)
    old_hostel_id = fields.Many2one('odoocms.hostel', 'Old Hostel', index=True, tracking=True, compute='_compute_student_data', store=True)
    old_room_id = fields.Many2one('odoocms.hostel.room', 'Old Room', tracking=True, compute='_compute_student_data', store=True)
    old_room_type = fields.Many2one('odoocms.hostel.room.type', 'Old Room Type', tracking=True, compute='_compute_student_data', store=True)
    # old_dinning_hall_id = fields.Many2one('odoocms.dinning.hall', 'Old Dinning Hall', tracking=True, compute='_compute_student_data', store=True)

    new_hostel_id = fields.Many2one('odoocms.hostel', 'New Hostel', index=True, tracking=True)
    new_room_id = fields.Many2one('odoocms.hostel.room', 'New Room', tracking=True)
    new_room_type = fields.Many2one('odoocms.hostel.room.type', 'New Room Type')
    # new_dinning_hall_id = fields.Many2one('odoocms.dinning.hall', 'Old Dinning Hall', tracking=True)

    state = fields.Selection([('Draft', 'Draft'),
                              ('Approved', 'Approved'),
                              ('Rejected', 'Rejected')], 'Status', default='Draft')
    multi_swap_id = fields.Many2one('odoocms.student.hostel.multi.swap', 'Multi Swap Ref.', tracking=True)
    occupied_student_id = fields.Many2one('odoocms.student', 'Occupied Student', index=True, tracking=True)

    _sql_constraints = [('name_uniq', 'UNIQUE(student_id,multi_swap_id)', 'Student Duplication are not Allowed.')]

    @api.model
    def create(self, values):
        if not values.get('name', False):
            values['name'] = self.env['ir.sequence'].next_by_code('odoocms.student.hostel.swap.line')
        result = super(OdooCMSStudentHostelMultiSwapLine, self).create(values)
        return result

    def unlink(self):
        for rec in self:
            if rec.state!='Draft':
                raise UserError('Only Draft State Entries can be Delete.')
        return super(OdooCMSStudentHostelMultiSwapLine, self).unlink()

    @api.depends('student_id')
    def _compute_student_data(self):
        for rec in self:
            if rec.student_id:
                rec.student_reg_no = rec.student_id.id_number and rec.student_id.id_number or ''
                rec.old_hostel_id = rec.student_id.hostel_id and rec.student_id.hostel_id.id or False
                rec.old_room_id = rec.student_id.room_id and rec.student_id.room_id.id or False
                rec.old_room_type = rec.student_id.room_type and rec.student_id.room_type.id or False
            else:
                rec.student_reg_no = ''
                rec.old_hostel_id = False
                rec.old_room_id = False
                rec.old_room_type = False

    @api.onchange('new_room_id')
    def onchange_new_room_id(self):
        for rec in self:
            if rec.new_room_id:
                rec.new_room_type = rec.new_room_id.room_type and rec.new_room_id.room_type.id or False
                student_id = self.env['odoocms.student'].search([('room_id', '=', rec.new_room_id.id)], order='id desc', limit=1)
                if student_id:
                    rec.occupied_student_id = student_id.id
                else:
                    rec.occupied_student_id = False

    def create_hostel_entry(self):
        # Here we are receiving the Swapping Lines
        processed_list = []
        for rec in self:
            processed_list.append(rec.student_id.id)
            # Already Room Occupied Student Handling
            if rec.occupied_student_id and rec.occupied_student_id.id not in processed_list:
                rec.occupied_student_id.hostel_id = False
                rec.occupied_student_id.room_id = False
                rec.occupied_student_id.room_type = False

                # Search the Occupied Student hostel history record and vacant it.
                oc_prev_history_record = self.env['odoocms.student.hostel.history'].search([('student_id', '=', rec.occupied_student_id.id), ('allocate_date', '!=', rec.multi_swap_id.date)], order='id desc', limit=1)
                if oc_prev_history_record:
                    oc_prev_history_record.vacant_date = (rec.multi_swap_id.date and rec.multi_swap_id.date) or fields.Date.context_doday()

            # New Student (means that want to shuffling) Handling
            # Add the Vacant Date
            prev_history_record = self.env['odoocms.student.hostel.history'].search([('student_id', '=', rec.student_id.id), ('allocate_date', '!=', rec.multi_swap_id.date)], order='id desc', limit=1)
            if prev_history_record:
                prev_history_record.vacant_date = (rec.multi_swap_id.date and rec.multi_swap_id.date) or fields.Date.context_doday()

            # Create the New History Record
            student_history_values = {
                'student_id': rec.student_id.id,
                'student_code': rec.student_reg_no and rec.student_reg_no or '',
                'session_id': rec.student_id.session_id and rec.student_id.session_id.id or False,
                'program_id': rec.student_id.program_id and rec.student_id.program_id.id or False,
                'career_id': rec.student_id.career_id and rec.student_id.career_id.id or False,
                'request_date': (rec.multi_swap_id.date and rec.multi_swap_id.date) or fields.Date.context_doday(),
                'allocate_date': (rec.multi_swap_id.date and rec.multi_swap_id.date) or fields.Date.context_doday(),
                'request_type': 'Swap',
                'state': 'Done',
                'active': True,
                'hostel_id': rec.new_hostel_id and rec.new_hostel_id.id or False,
                'room_id': rec.new_room_id and rec.new_room_id.id or False,
                'room_type': (rec.new_room_type and rec.new_room_type.id) or (rec.new_room_id.room_type and rec.new_room_id.room_type.id) or False,
                'previous_hostel_id': rec.old_hostel_id and rec.old_hostel_id.id or False,
                'previous_room_id': rec.old_room_id and rec.old_room_id.id or False,
            }
            new_rec = self.env['odoocms.student.hostel.history'].create(student_history_values)
            new_rec.multi_swap_id = rec.multi_swap_id.id

            rec.student_id.hostel_id = rec.new_hostel_id.id
            rec.student_id.room_id = rec.new_room_id.id
            rec.student_id.room_type = rec.new_room_id and rec.new_room_id.room_type.id
            rec.student_id.allocated_date = (rec.multi_swap_id.date and rec.multi_swap_id.date) or fields.Date.context_doday()
