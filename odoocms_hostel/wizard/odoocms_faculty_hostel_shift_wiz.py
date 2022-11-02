# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError


class OdooCMSFacultyHostelShiftWiz(models.TransientModel):
    _name = "odoocms.faculty.hostel.shift.wiz"
    _description = "Faculty Hostel Shift Wizard, To Shift Faculty From One Hostel to Another Hostel"

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

    faculty_code = fields.Char('Faculty ID', default=_get_reg_no)
    faculty_id = fields.Many2one('odoocms.faculty.staff', 'Faculty', default=_get_faculty)
    # faculty_gender = fields.Selection(related='faculty_id.gender', string='Gender')

    from_hostel_id = fields.Many2one('odoocms.hostel', 'From Hostel')
    from_room_id = fields.Many2one('odoocms.hostel.room', 'From Hostel Room')
    from_room_type = fields.Many2one('odoocms.hostel.room.type', 'From Room Type')

    to_hostel_id = fields.Many2one('odoocms.hostel', 'To Hostel')
    to_room_id = fields.Many2one('odoocms.hostel.room', 'To Hostel Room')
    to_room_type = fields.Many2one('odoocms.hostel.room.type', 'To Room Type')
    date = fields.Date('Date', default=fields.Date.today())
    vacant_rooms = fields.Html('Vacant Rooms Information')

    @api.onchange('faculty_code')
    def onchange_registration_no(self):
        for rec in self:
            if rec.faculty_id:
                rec.from_hostel_id = rec.faculty_id.hostel_id and rec.faculty_id.hostel_id.id or False
                rec.from_room_id = rec.faculty_id.room_id and rec.faculty_id.room_id.id or False
                rec.from_room_type = rec.faculty_id.room_type and rec.faculty_id.room_type.id or False

            if not rec.faculty_id and rec.faculty_code:
                faculty_id = self.env['odoocms.faculty.staff'].search([('registration_no', '=', rec.code)])
                if faculty_id:
                    rec.from_hostel_id = faculty_id.hostel_id and faculty_id.hostel_id.id or False
                    rec.from_room_id = faculty_id.room_id and faculty_id.room_id.id or False
                    rec.from_room_type = faculty_id.room_type and faculty_id.room_type.id or False

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

    def action_shift_faculty(self):
        for rec in self:
            if int(rec.to_room_id.room_capacity) > int(rec.to_room_id.allocated_number):
                if rec.faculty_id.gender=='male' and not rec.to_hostel_id.hostel_type.type=='Boys':
                    raise UserError(_("Please Note that, Boys Hostel Can allocated to Boys."))

                if rec.faculty_id.gender=='female' and not rec.to_hostel_id.hostel_type.type=='Girls':
                    raise UserError(_("Please Note that Girls Hostel Can Allocate to Girls"))

                history_values = {
                    'faculty_id': rec.faculty_id.id,
                    'faculty_code': rec.faculty_id.employee_id.identification_id or '',
                    # 'session_id': rec.faculty_id.session_id and rec.faculty_id.session_id.id or False,
                    # 'program_id': rec.faculty_id.program_id and rec.faculty_id.program_id.id or False,
                    # 'career_id': rec.faculty_id.career_id and rec.faculty_id.career_id.id or False,
                    'request_date': rec.date,
                    'allocate_date': rec.date,
                    'request_type': 'Shift',
                    'state': 'Done',
                    'active': True,
                    'previous_hostel_id': rec.faculty_id.hostel_id and rec.faculty_id.hostel_id.id or False,
                    'previous_room_id': rec.faculty_id.room_id and rec.faculty_id.room_id.id or False,
                    'hostel_id': rec.faculty_id.hostel_id and rec.to_hostel_id.id or False,
                    'room_id': rec.to_room_id and rec.to_room_id.id or False,
                    'room_type': rec.to_room_type and rec.to_room_type.id or False
                }
                new_hist_rec = self.env['odoocms.faculty.hostel.history'].create(history_values)

                rec.faculty_id.write({'hostel_id': rec.to_hostel_id.id,
                                      'room_id': rec.to_room_id.id,
                                      'room_type': rec.to_room_type.id,
                                      'allocated_date': fields.Date.today()})
            else:
                raise UserError('There is no Capacity in the Room, This Room is Occupied.')
