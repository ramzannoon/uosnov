# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError
import pdb


class OdooCMSStudentRoomAssignmentWiz(models.TransientModel):
    _name = "odoocms.student.room.assignment.wiz"
    _description = "This Wizard will assign the Room to a student, from Student Profile."

    @api.model
    def _get_student(self):
        if self._context.get('active_model', False)=='odoocms.student' and self._context.get('active_id', False):
            return self.env['odoocms.student'].browse(self._context.get('active_id', False))

    @api.model
    def _get_reg_no(self):
        reg_no = ''
        if self._context.get('active_model', False)=='odoocms.student' and self._context.get('active_id', False):
            student = self.env['odoocms.student'].browse(self._context.get('active_id', False))
            if student and student.id_number:
                reg_no = student.id_number
        return reg_no

    student_code = fields.Char('Student ID', default=_get_reg_no)
    student_id = fields.Many2one('odoocms.student', 'Student', default=_get_student)
    student_gender = fields.Selection(related='student_id.gender', string='Gender')
    hostel_id = fields.Many2one('odoocms.hostel', 'To Hostel')
    room_id = fields.Many2one('odoocms.hostel.room', 'To Hostel Room')
    room_type = fields.Many2one('odoocms.hostel.room.type', 'To Room Type')
    date = fields.Date('Date', default=fields.Date.today())
    vacant_rooms = fields.Html('Vacant Rooms Information')

    @api.onchange('hostel_id')
    def onchange_hostel_room_type(self):
        for rec in self:
            if rec.hostel_id:
                if rec.room_type:
                    rec.room_type = False
                if rec.room_id:
                    rec.room_id = False

    @api.onchange('hostel_id', 'room_type')
    def onchange_hostel_id(self):
        for rec in self:
            vacant_details = """
               <table class="table"><tbody>
                   <tr style="text-align:left;font-size:15;background-color: #17134e;color: white;">
                       <th>Sr#.</th>
                       <th>Room</th>
                       <th>No.</th>
                       <th>Type</th>
                       <th>Vacant Date</th>
                   </tr>
               """
            if rec.hostel_id:
                sr = 1
                vacant_rooms = self.env['odoocms.hostel.room'].search([('hostel_id', '=', rec.hostel_id.id), ('vacancy', '!=', 0)])
                if rec.room_type:
                    vacant_rooms = self.env['odoocms.hostel.room'].search([('hostel_id', '=', rec.hostel_id.id), ('room_type', '=', rec.room_type.id), ('vacancy', '!=', 0)])

                if vacant_rooms:
                    for vacant_room in vacant_rooms:
                        vacant_details += """
                            <tr>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td></td>
                            </tr>
                            """ % (sr, vacant_room.name, vacant_room.code, vacant_room.room_type.name)
                        sr += 1
                vacant_details += """</tbody></table>"""

        self.vacant_rooms = vacant_details

    @api.onchange('room_type')
    def onchange_room_type(self):
        for rec in self:
            if rec.room_type:
                if rec.room_id:
                    rec.room_id = False

    def action_student_room_assignment(self):
        for rec in self:
            if int(rec.room_id.room_capacity) > int(rec.room_id.allocated_number):
                if rec.student_id and rec.student_id.hostel_id:
                    raise UserError(_("This Student have already Hostel Room assignment, \n This action can not be performed here, You can Use the Shift Hostel Room. "))

                if rec.student_id.gender == 'm' and not rec.hostel_id.hostel_type.type == 'Boys':
                    raise UserError(_("Please Note that, Boys Hostel Can allocated to Boys."))

                if rec.student_id.gender == 'f' and not rec.hostel_id.hostel_type.type == 'Girls':
                    raise UserError(_("Please Note that Girls Hostel Can Allocate to Girls"))

                history_values = {
                    'student_id': rec.student_id.id,
                    'student_code': rec.student_id.id_number and rec.student_id.id_number or '',
                    'session_id': rec.student_id.session_id and rec.student_id.session_id.id or False,
                    'program_id': rec.student_id.program_id and rec.student_id.program_id.id or False,
                    'career_id': rec.student_id.career_id and rec.student_id.career_id.id or False,
                    'request_date': rec.date,
                    'allocate_date': rec.date,
                    'request_type': 'New Allocation',
                    'state': 'Done',
                    'active': True,
                    'hostel_id': rec.hostel_id and rec.hostel_id.id or False,
                    'room_id': rec.room_id and rec.room_id.id or False,
                    'room_type': rec.room_type and rec.room_type.id or False
                }
                self.env['odoocms.student.hostel.history'].create(history_values)
                rec.student_id.write({'hostel_id': rec.hostel_id.id,
                                      'room_id': rec.room_id.id,
                                      'room_type': rec.room_type.id,
                                      'hostel_state': 'Allocated',
                                      'allocated_date': rec.date})
                if int(rec.room_id.vacancy) == 0:
                    rec.room_id.state = 'Occupied'
            else:
                raise UserError('There is no Capacity in the Room, This Room is Occupied.')
