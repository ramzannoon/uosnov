# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class OdooCMSStudent(models.Model):
    _inherit = 'odoocms.student'

    hostel_id = fields.Many2one('odoocms.hostel', 'Hostel', tracking=True, index=True, ondelete='restrict')
    room_id = fields.Many2one('odoocms.hostel.room', 'Room', tracking=True, index=True, ondelete='restrict')
    room_type = fields.Many2one('odoocms.hostel.room.type', 'Room Type', compute='compute_room_type', store=True, tracking=True, index=True, ondelete='restrict')
    floor_id = fields.Many2one('odoocms.hostel.floor', 'Floor', related='room_id.floor_no', tracking=True, index=True, store=True)
    hostel_state = fields.Selection([('Allocated', 'Allocated'),
                                     ('Vacated', 'Vacated')], string='Hostel Status', default='Vacated', tracking=True)
    vacated_date = fields.Date(string="Vacated Date", tracking=True)
    allocated_date = fields.Date(string="Allocated Date", tracking=True)
    hostel_faculty = fields.Char('Hostel Faculty')
    hostel_hist_ids = fields.One2many('odoocms.student.hostel.history', 'student_id', 'Hostel History')
    special_info_ids = fields.One2many('odoocms.hostel.student.special.info', 'student_id', 'Special information')
    extra_facility_ids = fields.One2many('odoocms.hostel.extra.facilities', 'student_id', 'Extra Items')

    visitor_ids = fields.One2many('odoocms.hostel.visitor', 'student_id', 'Visitors')
    hostel_required = fields.Boolean('Hostel Required', default=1)

    @api.model
    def assign_room_type(self):
        students = self.env['odoocms.student'].search([('to_be', '=', True)])
        for student in students:
            student.room_type = student.room_id.room_type and student.room_id.room_type.id or False
            student.to_be = False

    @api.depends('room_id')
    def compute_room_type(self):
        for rec in self:
            rec.room_type = rec.room_id.room_type and rec.room_id.room_type.id or False
