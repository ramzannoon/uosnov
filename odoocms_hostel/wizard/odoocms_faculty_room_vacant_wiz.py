# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError


class OdooCMSFacultyRoomVacantWiz(models.TransientModel):
    _name = "odoocms.faculty.room.vacant.wiz"
    _description = "This Wizard will Vacant the Room to a faculty, from faculty Profile."

    @api.model
    def _get_faculty(self):
        if self._context.get('active_model', False)=='odoocms.faculty.staff' and self._context.get('active_id', False):
            return self.env['odoocms.faculty.staff'].browse(self._context.get('active_id', False))

    faculty_id = fields.Many2one('odoocms.faculty.staff', 'Faculty', default=_get_faculty)
    faculty_code = fields.Char('Faculty ID')
    faculty_gender = fields.Selection(related='faculty_id.gender', string='Gender')
    hostel_id = fields.Many2one('odoocms.hostel', 'To Hostel')
    room_id = fields.Many2one('odoocms.hostel.room', 'To Hostel Room')
    room_type = fields.Many2one('odoocms.hostel.room.type', 'To Room Type')
    date = fields.Date('Date', default=fields.Date.today())

    @api.onchange('faculty_id')
    def onchange_faculty_id(self):
        for rec in self:
            if rec.faculty_id:
                rec.faculty_code = rec.faculty_id.employee_id.identification_id or ''
                rec.gender = rec.faculty_id.gender and rec.faculty_id.gender or ''
                rec.hostel_id = rec.faculty_id.hostel_id and rec.faculty_id.hostel_id.id or False
                rec.room_id = rec.faculty_id.room_id and rec.faculty_id.room_id.id or False
                rec.room_type = rec.faculty_id.room_id and rec.faculty_id.room_id.room_type.id or False

    def action_faculty_room_vacant(self):
        for rec in self:
            if rec.faculty_id.hostel_id:
                history_values = {
                    'faculty_id': rec.faculty_id.id,
                    'faculty_code': rec.faculty_id.employee_id.identification_id or '',
                    # 'session_id': rec.faculty_id.session_id and rec.faculty_id.session_id.id or False,
                    # 'program_id': rec.faculty_id.program_id and rec.faculty_id.program_id.id or False,
                    # 'career_id': rec.faculty_id.career_id and rec.faculty_id.career_id.id or False,
                    'request_date': rec.date,
                    'vacant_date': rec.date,
                    'request_type': 'De Allocation',
                    'state': 'Done',
                    'active': True,
                    'hostel_id': rec.faculty_id.hostel_id and rec.faculty_id.hostel_id.id or False,
                    'room_id': rec.faculty_id.room_id and rec.faculty_id.room_id.id or False,
                    'room_type': rec.faculty_id.room_type and rec.faculty_id.room_type.id or False
                }
                new_hist_rec = self.env['odoocms.faculty.hostel.history'].create(history_values)
                if new_hist_rec:
                    rec.faculty_id.write({'hostel_id': False,
                                          'room_id': False,
                                          'room_type': False,
                                          'hostel_state': 'Vacated',
                                          'allocated_date': '',
                                          'vacated_date': rec.date})
                if not rec.room_id.faculty_ids:
                    rec.room_id.state = 'Vacant'
            else:
                raise UserError(_('This faculty do not have the Hostel Room Allocation, This Action Cannot be '
                                  'Performed.'))
