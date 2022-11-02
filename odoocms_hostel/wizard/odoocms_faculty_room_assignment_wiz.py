# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError


class OdooCMSFacultyRoomAssignmentWiz(models.TransientModel):
    _name = "odoocms.faculty.room.assignment.wiz"
    _description = "This Wizard will assign the Room to a faculty, from faculty Profile."

    @api.model
    def _get_faculty(self):
        if self._context.get('active_model', False)=='odoocms.faculty.staff' and self._context.get('active_id', False):
            return self.env['odoocms.faculty.staff'].browse(self._context.get('active_id', False))

    @api.model
    def _get_reg_no(self):
        reg_no = ''
        if self._context.get('active_model', False)=='odoocms.faculty.staff' and self._context.get('active_id', False):
            faculty = self.env['odoocms.faculty.staff'].browse(self._context.get('active_id', False))
            if faculty and faculty.employee_id.identification_id:
                reg_no = faculty.employee_id.identification_id
        return reg_no

    faculty_code = fields.Char('faculty ID', default=_get_reg_no)
    faculty_id = fields.Many2one('odoocms.faculty.staff', 'faculty', default=_get_faculty)
    faculty_gender = fields.Selection(related='faculty_id.gender', string='Gender')
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

    def action_faculty_room_assignment(self):
        for rec in self:
            if int(rec.room_id.room_capacity) > int(rec.room_id.allocated_number):
                if rec.faculty_id and rec.faculty_id.hostel_id:
                    raise UserError(_("This faculty have already Hostel Room assignment, \n This action can not be performed here, You can Use the Shift Hostel Room. "))

                if rec.faculty_id.gender == 'm' and not rec.hostel_id.hostel_type.type == 'Boys':
                    raise UserError(_("Please Note that, Boys Hostel Can allocated to Boys."))

                if rec.faculty_id.gender == 'f' and not rec.hostel_id.hostel_type.type == 'Girls':
                    raise UserError(_("Please Note that Girls Hostel Can Allocate to Girls"))

                history_values = {
                    'faculty_id': rec.faculty_id.id,
                    'faculty_code': rec.faculty_id.employee_id.identification_id and rec.faculty_id.employee_id.identification_id or '',
                    # 'session_id': rec.faculty_id.session_id and rec.faculty_id.session_id.id or False,
                    # 'program_id': rec.faculty_id.program_id and rec.faculty_id.program_id.id or False,
                    # 'career_id': rec.faculty_id.career_id and rec.faculty_id.career_id.id or False,
                    'request_date': rec.date,
                    'allocate_date': rec.date,
                    'request_type': 'New Allocation',
                    'state': 'Done',
                    'active': True,
                    'hostel_id': rec.hostel_id and rec.hostel_id.id or False,
                    'room_id': rec.room_id and rec.room_id.id or False,
                    'room_type': rec.room_type and rec.room_type.id or False
                }
                self.env['odoocms.faculty.hostel.history'].create(history_values)
                rec.faculty_id.write({'hostel_id': rec.hostel_id.id,
                                      'room_id': rec.room_id.id,
                                      'room_type': rec.room_type.id,
                                      'hostel_state': 'Allocated',
                                      'allocated_date': rec.date})
                if int(rec.room_id.vacancy) == 0:
                    rec.room_id.state = 'Occupied'
            else:
                raise UserError('There is no Capacity in the Room, This Room is Occupied.')
