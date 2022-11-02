# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError
import pdb


class OdooCMSStudentRoomVacantWiz(models.TransientModel):
    _name = "odoocms.student.room.vacant.wiz"
    _description = "This Wizard will Vacant the Room to a student, from Student Profile."

    @api.model
    def _get_student(self):
        if self._context.get('active_model', False)=='odoocms.student' and self._context.get('active_id', False):
            return self.env['odoocms.student'].browse(self._context.get('active_id', False))

    student_id = fields.Many2one('odoocms.student', 'Student', default=_get_student)
    student_code = fields.Char('Student ID')
    student_gender = fields.Selection(related='student_id.gender', string='Gender')
    hostel_id = fields.Many2one('odoocms.hostel', 'To Hostel')
    room_id = fields.Many2one('odoocms.hostel.room', 'To Hostel Room')
    room_type = fields.Many2one('odoocms.hostel.room.type', 'To Room Type')
    date = fields.Date('Date', default=fields.Date.today())

    @api.onchange('student_id')
    def onchange_student_id(self):
        for rec in self:
            if rec.student_id:
                rec.student_code = rec.student_id.id_number and rec.student_id.id_number or ''
                rec.gender = rec.student_id.gender and rec.student_id.gender or ''
                rec.hostel_id = rec.student_id.hostel_id and rec.student_id.hostel_id.id or False
                rec.room_id = rec.student_id.room_id and rec.student_id.room_id.id or False
                rec.room_type = rec.student_id.room_id and rec.student_id.room_id.room_type.id or False

    def action_student_room_vacant(self):
        for rec in self:
            if rec.student_id.hostel_id:
                history_values = {
                    'student_id': rec.student_id.id,
                    'student_code': rec.student_id.id_number and rec.student_id.id_number or '',
                    'session_id': rec.student_id.session_id and rec.student_id.session_id.id or False,
                    'program_id': rec.student_id.program_id and rec.student_id.program_id.id or False,
                    'career_id': rec.student_id.career_id and rec.student_id.career_id.id or False,
                    'request_date': rec.date,
                    'vacant_date': rec.date,
                    'request_type': 'De Allocation',
                    'state': 'Done',
                    'active': True,
                    'hostel_id': rec.student_id.hostel_id and rec.student_id.hostel_id.id or False,
                    'room_id': rec.student_id.room_id and rec.student_id.room_id.id or False,
                    'room_type': rec.student_id.room_type and rec.student_id.room_type.id or False
                }
                new_hist_rec = self.env['odoocms.student.hostel.history'].create(history_values)
                if new_hist_rec:
                    rec.student_id.write({'hostel_id': False,
                                          'room_id': False,
                                          'room_type': False,
                                          'hostel_state': 'Vacated',
                                          'allocated_date': '',
                                          'vacated_date': rec.date})
                if not rec.room_id.student_ids:
                    rec.room_id.state = 'Vacant'
            else:
                raise UserError(_('This Student do not have the Hostel Room Allocation, This Action Cannot be Performed.'))
