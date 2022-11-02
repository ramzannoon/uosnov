# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import pdb


# class HelpdeskTicket(models.Model):
#     _inherit = 'helpdesk.ticket'
#
#     hostel_id = fields.Many2one('odoocms.hostel', 'Hostel', tracking=True, compute='_compute_info', store=True)
#     room_id = fields.Many2one('odoocms.hostel.room', 'Room#', tracking=True, compute='_compute_info', store=True)
#
#     @api.depends('type', 'student_reg_no', 'employee_id')
#     def _compute_info(self):
#         for rec in self:
#             super(HelpdeskTicket, self)._compute_info()
#             if rec.student_id:
#                 rec.hostel_id = rec.student_id.hostel_id and rec.student_id.hostel_id.id or False
#                 rec.room_id = rec.student_id.room_id and rec.student_id.room_id.id or False


class HostelWings(models.Model):
    _name = 'odoocms.hostel.wings'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _description = 'Hostel Wings'

    name = fields.Char('Name', tracking=True)
    sequence = fields.Integer('Sequence')
    active = fields.Boolean('Active', default=True)
    state = fields.Selection([('draft', 'Draft'), ('lock', 'Locked')], string='Status', default='draft', tracking=True)

    def unlink(self):
        return super(HostelWings, self).unlink()

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'


class HostelRoomBlockageReason(models.Model):
    _name = 'odoocms.hostel.room.blockage.reason'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _description = 'Hostel Rooms Blockage Reasons'

    name = fields.Char('Name', tracking=True)
    sequence = fields.Integer('Sequence')
    room_ids = fields.One2many('odoocms.hostel.room', 'blockage_reason_id', 'Rooms')
    active = fields.Boolean('Active', default=True)
    state = fields.Selection([('draft', 'Draft'), ('lock', 'Locked')], string='Status', default='draft', tracking=True)

    def unlink(self):
        for rec in self:
            if rec.room_ids:
                raise UserError(_("This Cannot de delete because there are some rooms linked with this"))
        return super(HostelRoomBlockageReason, self).unlink()

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'
