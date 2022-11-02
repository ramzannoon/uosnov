# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.exceptions import AccessError, UserError
import pdb


class OdooCMSHostelDeallocationWiz(models.TransientModel):
    _name = "odoocms.hostel.rooms.deallocation.wiz"
    _description = "Hostel Rooms De-Allocation"

    hostel_ids = fields.Many2many('odoocms.hostel', 'deallocation_hostel_rooms_rel', 'deallocation_id', 'hostel_id', 'Hostels')
    floor_ids = fields.Many2many('odoocms.hostel.floor', 'deallocation_hostel_floors_rel', 'deallocation_id', 'floor_id', 'Floors')
    all_hostel = fields.Boolean('All Hostel')

    exclude_session_ids = fields.Many2many('odoocms.academic.session', 'ex_deallocation_academic_session_rel', 'deallocation_id', 'ex_session_id', 'Excluded Academic Sessions')
    exclude_hostel_ids = fields.Many2many('odoocms.hostel', 'ex_deallocation_hostel_rel', 'deallocation_id', 'ex_hostel_id', 'Excluded Hostels')
    exclude_room_ids = fields.Many2many('odoocms.hostel.room', 'ex_deallocation_hostel_room_rel', 'deallocation_id', 'ex_hostel_room_id', 'Excluded Rooms')
    exclude_room_types = fields.Many2many('odoocms.hostel.room.type', 'ex_deallocation_room_types', 'deallocation_id', 'ex_room_type_id', 'Excluded Room Types')

    def deallocate_students_action(self):
        for rec in self:
            hostels = False
            if rec.all_hostel:
                hostels = self.env['odoocms.hostel'].search([])
            if not rec.all_hostel and rec.hostel_ids:
                hostels = rec.hostel_ids

            if hostels:
                for hostel in hostels:
                    domain = [('hostel_id', '=', hostel.id)]
                    if rec.floor_ids:
                        domain.append(('floor_id', 'in', rec.floor_ids.ids))
                    if self.exclude_session_ids:
                        domain.append(('session_id', 'not in', self.exclude_session_ids.ids))
                    if self.exclude_hostel_ids:
                        domain.append(('hostel_id', 'not in', self.exclude_hostel_ids.ids))
                    if self.exclude_room_types:
                        domain.append(('room_type', 'not in', self.exclude_room_types.ids))
                    if self.exclude_room_ids:
                        domain.append(('room_id', 'not in', self.exclude_room_ids.ids))
                    students = self.env['odoocms.student'].search(domain)
                    if students:
                        for student in students:
                            history_vals = {
                                'student_id': student.id,
                                'student_code': student.id_number and student.id_number or '',
                                'session_id': student.session_id and student.session_id.id or False,
                                'program_id': student.program_id and student.program_id.id or False,
                                'career_id': student.career_id and student.career_id.id or False,
                                'request_date': fields.Date.today(),
                                'vacant_date': fields.Date.today(),
                                'request_type': 'De Allocation',
                                'state': 'Done',
                                'active': True,
                                'hostel_id': student.hostel_id and student.hostel_id.id or False,
                                'room_id': student.room_id and student.room_id.id or False,
                                'room_type': student.room_type and student.room_type.id or False
                            }

                            self.env['odoocms.student.hostel.history'].create(history_vals)
                            student.room_id.vacancy = str(int(student.room_id.vacancy) + 1)
                            if student.room_id.vacancy == student.room_id.room_capacity:
                                student.room_id.state = 'Vacant'

                            student.room_id.vacant_date = fields.Date.today()
                            student.hostel_id = False
                            student.room_id = False
                            student.room_type = False
                            student.hostel_state = 'Vacated'

                            # last_hist_id = self.env['odoocms.student.hostel.history'].search([('student_id', '=', student.id)], order='id desc', limit=1)
                            # last_hist_id.state = 'Draft'
                            # last_hist_id.sudo().unlink()

            if not rec.all_hostel and not rec.hostel_ids:
                raise UserError('No Data Selected')
