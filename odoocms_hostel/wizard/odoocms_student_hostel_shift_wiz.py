# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError
import pdb


class OdooCMSStudentHostelShiftWiz(models.TransientModel):
    _name = "odoocms.student.hostel.shift.wiz"
    _description = "Student Hostel Shift Wizard, To Shift Student From One Hostel to Another Hostel"

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

    from_hostel_id = fields.Many2one('odoocms.hostel', 'From Hostel')
    from_room_id = fields.Many2one('odoocms.hostel.room', 'From Hostel Room')
    from_room_type = fields.Many2one('odoocms.hostel.room.type', 'From Room Type')

    to_hostel_id = fields.Many2one('odoocms.hostel', 'To Hostel')
    to_room_id = fields.Many2one('odoocms.hostel.room', 'To Hostel Room')
    to_room_type = fields.Many2one('odoocms.hostel.room.type', 'To Room Type')
    date = fields.Date('Date', default=fields.Date.today())
    vacant_rooms = fields.Html('Vacant Rooms Information')

    @api.onchange('student_code')
    def onchange_registration_no(self):
        for rec in self:
            if rec.student_id:
                rec.from_hostel_id = rec.student_id.hostel_id and rec.student_id.hostel_id.id or False
                rec.from_room_id = rec.student_id.room_id and rec.student_id.room_id.id or False
                rec.from_room_type = rec.student_id.room_type and rec.student_id.room_type.id or False

            if not rec.student_id and rec.student_code:
                student_id = self.env['odoocms.student'].search([('registration_no', '=', rec.student_code)])
                if student_id:
                    rec.from_hostel_id = student_id.hostel_id and student_id.hostel_id.id or False
                    rec.from_room_id = student_id.room_id and student_id.room_id.id or False
                    rec.from_room_type = student_id.room_type and student_id.room_type.id or False

    @api.onchange('to_hostel_id', 'to_room_type')
    def onchange_to_hostel_id(self):
        for rec in self:
            vacant_details = """
               <table class="table .table-striped"><tbody>
                   <tr style="text-align:left;font-size:15;background-color: #17134e;color: white;">
                       <th>Sr#.</th>
                       <th>Room</th>
                       <th>No.</th>
                       <th>Type</th>
                       <th>Vacant Date</th>
                   </tr>
               """
            if rec.to_hostel_id:
                sr = 1
                vacant_rooms = self.env['odoocms.hostel.room'].search([('hostel_id', '=', rec.to_hostel_id.id), ('vacancy', '!=', 0)])
                if rec.to_room_type:
                    vacant_rooms = self.env['odoocms.hostel.room'].search([('hostel_id', '=', rec.to_hostel_id.id), ('room_type', '=', rec.to_room_type.id), ('vacancy', '!=', 0)])

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
                    vacant_details += """
                       <tr style="text-align:left;font-size:15;background-color: #17134e;color: white;">
                           <th></th>
                           <th></th>
                           <th></th>
                           <th></th>
                           <th></th>
                       </tr>
                    """

                vacant_details += """</tbody></table>"""

        self.vacant_rooms = vacant_details

    def action_shift_student(self):
        for rec in self:
            if int(rec.to_room_id.room_capacity) > int(rec.to_room_id.allocated_number):
                if rec.student_id.gender=='m' and not rec.to_hostel_id.hostel_type.type=='Boys':
                    raise UserError(_("Please Note that, Boys Hostel Can allocated to Boys."))

                if rec.student_id.gender=='f' and not rec.to_hostel_id.hostel_type.type=='Girls':
                    raise UserError(_("Please Note that Girls Hostel Can Allocate to Girls"))

                history_values = {
                    'student_id': rec.student_id.id,
                    'student_code': rec.student_id.id_number and rec.student_id.id_number or '',
                    'session_id': rec.student_id.session_id and rec.student_id.session_id.id or False,
                    'program_id': rec.student_id.program_id and rec.student_id.program_id.id or False,
                    'career_id': rec.student_id.career_id and rec.student_id.career_id.id or False,
                    'request_date': rec.date,
                    'allocate_date': rec.date,
                    'request_type': 'Shift',
                    'state': 'Done',
                    'active': True,
                    'previous_hostel_id': rec.student_id.hostel_id and rec.student_id.hostel_id.id or False,
                    'previous_room_id': rec.student_id.room_id and rec.student_id.room_id.id or False,
                    'hostel_id': rec.student_id.hostel_id and rec.to_hostel_id.id or False,
                    'room_id': rec.to_room_id and rec.to_room_id.id or False,
                    'room_type': rec.to_room_type and rec.to_room_type.id or False
                }
                new_hist_rec = self.env['odoocms.student.hostel.history'].create(history_values)

                rec.student_id.write({'hostel_id': rec.to_hostel_id.id,
                                      'room_id': rec.to_room_id.id,
                                      'room_type': rec.to_room_type.id,
                                      'allocated_date': fields.Date.today()})
            else:
                raise UserError('There is no Capacity in the Room, This Room is Occupied.')
