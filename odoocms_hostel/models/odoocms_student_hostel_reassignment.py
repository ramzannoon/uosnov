# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import pdb


class OdoocmsStudentHostelReassignment(models.Model):
    _name = 'odoocms.student.hostel.reassignment'
    _description = "Student Hostel Reassignment"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    # This Class Will be Used for Re-Assignment of the Hostel Rooms to the Students, after every Academic session
    # Hostel Rooms are re-allocated to the Students, With CGPA Level and new students with respect to Merit Number."

    name = fields.Char('Name', tracking=True)
    sequence = fields.Integer('Sequence')
    # This fields contains the Most Senior Student Session, on which we will process other students session data for the hostel.
    senior_session_id = fields.Many2one('odoocms.academic.session', 'Senior Most Session', tracking=True)
    # Students Import from Excel file, current Academic Session for Room Priority
    session_id = fields.Many2one('odoocms.academic.session', 'Students Academic Session', tracking=True)
    # Type to handle the Old Students based on the CGPA and Fresh Students to handle based on Merit No.
    type = fields.Selection([('Old Student', 'Old Student'),
                             ('Freshmen', 'Freshmen')],string='Type', tracking=True)
    date = fields.Date('Date', default=fields.Date.today(), tracking=True)
    total_students = fields.Float('Total Students', tracking=True, compute='_compute_students_total', store=True)
    newly_assigned_students = fields.Float('New Assigned Students', compute='_compute_newly_assigned_total', store=True)
    old_assigned_students = fields.Float('Old Assigned Students', compute='_compute_old_assigned_total', store=True)
    line_ids = fields.One2many('odoocms.student.hostel.reassignment.line', 'reassignment_id', 'Reassignment Lines')
    issue_line_ids = fields.One2many('odoocms.student.hostel.reassignment.issue', 'reassignment_id', 'Reassignment Issue Lines')
    state = fields.Selection([('Draft', 'Draft'),
                              ('Assigned', 'Assigned'),
                              ('Cancel', 'Cancel')],
        'Status', default='Draft', tracking=True, index=True)
    remarks = fields.Text('Remarks')

    @api.model
    def create(self, values):
        if not values.get('name', False):
            values['name'] = self.env['ir.sequence'].next_by_code('odoocms.student.hostel.reassignment')
        result = super(OdoocmsStudentHostelReassignment, self).create(values)
        return result

    def unlink(self):
        for rec in self:
            if rec.state=='Assigned':
                raise UserError(_('You Cannot Delete the Records which are Assigned.'))
        return super(OdoocmsStudentHostelReassignment, self).unlink()

    def assign_student_hostel_info(self, student_line=False, room_rec=False):
        for rec in self:
            if student_line and room_rec:
                student = student_line.student_id
                if student.hostel_id and student.room_id and student.room_type:
                    student_line.assignment_status = 'Old'
                else:
                    student.hostel_id = room_rec.hostel_id.id
                    student.room_id = room_rec.id
                    student.room_type = room_rec.room_type and room_rec.room_type.id or False
                    student.allocated_date = fields.Date.today()
                    student_line.write({'assignment_status': 'New',
                                        'state': 'Assigned',
                                        'assigned_hostel_id': room_rec.hostel_id.id,
                                        'assigned_room_id': room_rec.id,
                                        'assigned_room_type': room_rec.room_type.id})

                    # Prepare values for the Hostel History
                    student_history_values = {
                        'student_id': student.id,
                        'student_code': student.registration_no and student.registration_no or '',
                        'session_id': student.session_id and student.session_id.id or False,
                        'program_id': student.program_id and student.program_id.id or False,
                        'career_id': student.career_id and student.career_id.id or False,
                        'request_date': rec.date,
                        'allocate_date': fields.Date.today(),
                        'request_type': 'Re-Allocate',
                        'state': 'Done',
                        'hostel_id': room_rec.hostel_id and room_rec.hostel_id.id or False,
                        'room_id': room_rec and room_rec.id or False,
                        'room_type': room_rec.room_type and room_rec.room_type.id or False,
                    }
                    # Create History Entry
                    new_rec = self.env['odoocms.student.hostel.history'].create(student_history_values)

    def action_done(self):
        for rec in self:
            if rec.line_ids:
                processed_rooms = []

                # For Old Students
                if rec.type=='Old Student':
                    male_student_lines = self.env['odoocms.student.hostel.reassignment.line'].search([('id', 'in', rec.line_ids.ids), '|', ('gender', '=', 'M'), ('student_id.gender', '=', 'm')], order='cgpa desc, student_reg_no asc')
                    female_student_lines = self.env['odoocms.student.hostel.reassignment.line'].search([('id', 'in', rec.line_ids.ids), '|', ('gender', '=', 'F'), ('student_id.gender', '=', 'f')], order='cgpa desc, student_reg_no asc')

                # For New Students
                if rec.type=='Freshmen':
                    male_student_lines = self.env['odoocms.student.hostel.reassignment.line'].search([('id', 'in', rec.line_ids.ids), '|', ('gender', '=', 'M'), ('student_id.gender', '=', 'm')], order='merit_no desc, student_reg_no asc')
                    female_student_lines = self.env['odoocms.student.hostel.reassignment.line'].search([('id', 'in', rec.line_ids.ids), '|', ('gender', '=', 'F'), ('student_id.gender', '=', 'f')], order='merit_no desc, student_reg_no asc')

                # For Male Students
                if male_student_lines:
                    hostels = self.env['odoocms.hostel'].search([('hostel_type.type', '=', 'Boys')], order='id asc')
                    single_rooms = self.env['odoocms.hostel.room'].search([('hostel_id', 'in', hostels.ids), ('vacancy', '!=', '0'), ('room_type.name', '=', 'Single Bed'), ('room_blocked', '=', False)], order='hostel_id asc, id asc').ids
                    double_rooms = self.env['odoocms.hostel.room'].search([('hostel_id', 'in', hostels.ids), ('vacancy', '!=', '0'), ('room_type.name', '=', 'Double Bed'), ('room_blocked', '=', False)], order='hostel_id asc, id asc').ids
                    triple_rooms = self.env['odoocms.hostel.room'].search([('hostel_id', 'in', hostels.ids), ('vacancy', '!=', '0'), ('room_type.name', '=', 'Triple Bed'), ('room_blocked', '=', False)], order='hostel_id asc, id asc').ids

                    rooms = single_rooms + double_rooms + triple_rooms
                    if rooms:
                        room_id = rooms.pop(0)
                        room_rec = self.env['odoocms.hostel.room'].browse(room_id)
                    for student_line in male_student_lines:
                        if not rooms:
                            continue
                        else:
                            rec.assign_student_hostel_info(student_line, room_rec)
                            if room_rec.vacancy=='0':
                                processed_rooms.append(room_id)
                                room_id = rooms.pop(0)
                                room_rec = self.env['odoocms.hostel.room'].browse(room_id)

                # For Female Students
                if female_student_lines:
                    hostels = self.env['odoocms.hostel'].search([('hostel_type.type', '=', 'Girls')], order='id asc')
                    single_rooms = self.env['odoocms.hostel.room'].search([('hostel_id', 'in', hostels.ids), ('vacancy', '!=', '0'), ('room_type.name', '=', 'Single Bed'), ('room_blocked', '=', False)], order='hostel_id asc, id asc').ids
                    double_rooms = self.env['odoocms.hostel.room'].search([('hostel_id', 'in', hostels.ids), ('vacancy', '!=', '0'), ('room_type.name', '=', 'Double Bed'), ('room_blocked', '=', False)], order='hostel_id asc, id asc').ids
                    triple_rooms = self.env['odoocms.hostel.room'].search([('hostel_id', 'in', hostels.ids), ('vacancy', '!=', '0'), ('room_type.name', '=', 'Triple Bed'), ('room_blocked', '=', False)], order='hostel_id asc, id asc').ids
                    rooms = single_rooms + double_rooms + triple_rooms

                    if rooms:
                        room_id = rooms.pop(0)
                        room_rec = self.env['odoocms.hostel.room'].browse(room_id)

                    for student_line in female_student_lines:
                        if not rooms:
                            continue
                        else:
                            rec.assign_student_hostel_info(student_line, room_rec)
                            if room_rec.vacancy=='0':
                                processed_rooms.append(room_id)
                                room_id = rooms.pop(0)
                                room_rec = self.env['odoocms.hostel.room'].browse(room_id)

            if rec.issue_line_ids:
                rec.line_ids.write({'state': 'Assigned'})
            rec.state = 'Assigned'

    def action_cancel(self):
        for rec in self:
            if rec.line_ids:
                rec.line_ids.write({'state': 'Cancel'})
            if rec.issue_line_ids:
                rec.line_ids.write({'state': 'Assigned'})
            rec.state = 'Cancel'

    @api.depends('line_ids')
    def _compute_students_total(self):
        for rec in self:
            total = 0
            if rec.line_ids:
                total = len(rec.line_ids)
            rec.total_students = total

    @api.depends('line_ids', 'line_ids.assignment_status')
    def _compute_newly_assigned_total(self):
        for rec in self:
            cnt = 0
            if rec.line_ids:
                records = rec.line_ids.filtered(lambda l: l.assignment_status=='New')
                if records:
                    cnt = len(records)
            rec.newly_assigned_students = cnt

    @api.depends('line_ids', 'line_ids.assignment_status')
    def _compute_old_assigned_total(self):
        for rec in self:
            cnt = 0
            if rec.line_ids:
                records = rec.line_ids.filtered(lambda l: l.assignment_status=='Old')
                if records:
                    cnt = len(records)
            rec.old_assigned_students = cnt


class OdoocmsStudentHostelReassignmentLine(models.Model):
    _name = 'odoocms.student.hostel.reassignment.line'
    _description = "Student Hostel Reassignment Lines"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    name = fields.Char('Name', tracking=True)
    sequence = fields.Integer('Sequence')
    date = fields.Date('Date', tracking=True)
    student_reg_no = fields.Char('Student Reg No.', tracking=True, required=1)
    student_id = fields.Many2one('odoocms.student', 'Student', tracking=True, index=True)
    session_id = fields.Many2one('odoocms.academic.session', 'Academic Session', tracking=True)
    program_id = fields.Many2one('odoocms.program', 'Academic Program', tracking=True)
    gender = fields.Selection([('M', 'Male'),
                               ('F', 'Female')],
        tracking=True, index=True, string='Gender')
    type = fields.Selection([('Old Student', 'Old Student'),
                             ('Freshmen', 'Freshmen')],
        string='Type', tracking=True)
    assignment_status = fields.Selection([('New', 'New'),
                                          ('Old', 'Old')],
        string='Assignment Status')
    cgpa = fields.Float('CGPA', tracking=True)
    merit_no = fields.Char('Merit No', tracking=True)
    assigned_hostel_id = fields.Many2one('odoocms.hostel', 'Assigned Hostel', tracking=True, index=True)
    assigned_room_id = fields.Many2one('odoocms.hostel.room', 'Assigned Room', tracking=True, index=True)
    assigned_room_type = fields.Many2one('odoocms.hostel.room.type', 'Assigned Room Type', tracking=True, index=True)
    reassignment_id = fields.Many2one('odoocms.student.hostel.reassignment', 'Reassignment Ref', tracking=True, index=True)
    state = fields.Selection([('Draft', 'Draft'),
                              ('Assigned', 'Assigned'),
                              ('Cancel', 'Cancel')],
        'Status', default='Draft', index=True)

    remarks = fields.Text('Remarks')

    _sql_constraints = [
        ('student_id_uniq', 'unique(reassignment_id,student_id)', "Duplicate Students are not Allowed!."),
    ]

    @api.model
    def create(self, values):
        if not values.get('name', False):
            values['name'] = self.env['ir.sequence'].next_by_code('odoocms.student.hostel.reassignment.line')
        result = super(OdoocmsStudentHostelReassignmentLine, self).create(values)
        return result

    def unlink(self):
        for rec in self:
            if rec.state=='Assigned':
                raise UserError(_('You Cannot Delete the Records which are Assigned.'))
        return super(OdoocmsStudentHostelReassignmentLine, self).unlink()


class OdoocmsStudentHostelReassignmentIssue(models.Model):
    _name = 'odoocms.student.hostel.reassignment.issue'
    _description = "Student Hostel Reassignment Lines"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence')
    student_reg_no = fields.Char('Reg No.', tracking=True, index=True)
    reassignment_id = fields.Many2one('odoocms.student.hostel.reassignment', 'Reassignment Ref', tracking=True, index=True)
    state = fields.Selection([('Draft', 'Draft'),
                              ('Assigned', 'Assigned'),
                              ('Cancel', 'Cancel')],
        'Status', default='Draft', index=True)
    remarks = fields.Text('Remarks')
