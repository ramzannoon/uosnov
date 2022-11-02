# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class OdooCMSFacultyHostelHistory(models.Model):
    _name = 'odoocms.faculty.hostel.history'
    _description = "faculty Hostel History"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    name = fields.Char('Name', tracking=True)
    sequence = fields.Char('Sequence')
    faculty_id = fields.Many2one('odoocms.faculty.staff', 'Faculty', tracking=True, readonly=True, states={'Draft': [('readonly', False)]})
    faculty_code = fields.Char('faculty ID', tracking=True, readonly=True, states={'Draft': [('readonly', False)]})

    session_id = fields.Many2one('odoocms.academic.session', 'Academic Session', tracking=True, readonly=True, states={'Draft': [('readonly', False)]})
    program_id = fields.Many2one('odoocms.program', 'Academic Program', tracking=True, readonly=True, states={'Draft': [('readonly', False)]})
    career_id = fields.Many2one('odoocms.career', 'Academic Level', tracking=True, readonly=True, states={'Draft': [('readonly', False)]})

    request_date = fields.Date('Request Date', default=fields.Date.today(), readonly=True, states={'Draft': [('readonly', False)]})
    allocate_date = fields.Date('Allocation Date', readonly=True, states={'Draft': [('readonly', False)]})
    vacant_date = fields.Date('Vacant Date', readonly=True, states={'Draft': [('readonly', False)]})
    request_type = fields.Selection([('Swap', 'Swap'),
                                     ('Re-Allocate', 'Re-Allocate'),
                                     ('New Allocation', 'New Allocation'),
                                     ('De Allocation', 'De Allocation'),
                                     ('Shift', 'Shift')], 'Type', readonly=True, states={'Draft': [('readonly', False)]})
    active = fields.Boolean('Active', default=True, readonly=True, states={'Draft': [('readonly', False)]})
    state = fields.Selection([('Draft', 'Draft'),
                              ('Approved', 'Approved'),
                              ('Done', 'Done')], 'Status', default='Draft', tracking=True)

    hostel_id = fields.Many2one('odoocms.hostel', 'Hostel', readonly=True, states={'Draft': [('readonly', False)]})
    room_id = fields.Many2one('odoocms.hostel.room', 'Swap With Room', readonly=True, states={'Draft': [('readonly', False)]})
    room_type = fields.Many2one('odoocms.hostel.room.type', 'Room Type', readonly=True, states={'Draft': [('readonly', False)]})

    previous_hostel_id = fields.Many2one('odoocms.hostel', 'Previous Hostel', readonly=True, states={'Draft': [('readonly', False)]})
    previous_room_id = fields.Many2one('odoocms.hostel.room', 'Previous Room', readonly=True, states={'Draft': [('readonly', False)]})

    hostel_swap_id = fields.Many2one('odoocms.faculty.hostel.swap', 'Swap Ref.', readonly=True)
    multi_swap_id = fields.Many2one('odoocms.faculty.hostel.multi.swap', 'Multi Swap Ref.', readonly=True)

    @api.model
    def create(self, values):
        if not values.get('name', False):
            values['name'] = self.env['ir.sequence'].next_by_code('odoocms.faculty.hostel.history')
        result = super(OdooCMSFacultyHostelHistory, self).create(values)
        return result

    def unlink(self):
        for rec in self:
            if not rec.state=='Draft':
                raise UserError(_('Only Draft State Entries Can be Delete.'))
        return super(OdooCMSFacultyHostelHistory, self).unlink()
