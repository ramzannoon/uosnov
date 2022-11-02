# See LICENSE file for full copyright and licensing details.
from lxml import etree
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError


class OdooCMSHostelExtraFacilityCategory(models.Model):
    _name = 'odoocms.hostel.extra.facility.category'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'This Model Will Contain the Information About Extra Facilities that a Student can Avail'

    name = fields.Char('Name', required=True, help="Name", tracking=True)
    code = fields.Char('Code', tracking=True)
    sequence = fields.Char('Sequence')
    active = fields.Boolean('Active', default=True)
    facility_ids = fields.One2many('odoocms.hostel.extra.facilities', 'category_id', 'Facilities')

    @api.model
    def create(self, values):
        result = super(OdooCMSHostelExtraFacilityCategory, self).create(values)
        return result

    def unlink(self):
        return super(OdooCMSHostelExtraFacilityCategory, self).unlink()


class OdooCMSHostelExtraFacilities(models.Model):
    _name = 'odoocms.hostel.extra.facilities'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Extra Facilities that a student can Avail'

    name = fields.Char('Name')
    sequence = fields.Char('Sequence')
    student_code = fields.Char('Student Code', tracking=True)
    faculty_code = fields.Char('Faculty Code', tracking=True)
    student_id = fields.Many2one('odoocms.student', 'Student', tracking=True, index=True, ondelete='restrict')
    faculty_id = fields.Many2one('odoocms.faculty', 'Faculty', tracking=True, index=True, ondelete='restrict')
    session_id = fields.Many2one('odoocms.academic.session', 'Academic Session', tracking=True)
    program_id = fields.Many2one('odoocms.program', 'Academic Program', tracking=True)

    hostel_id = fields.Many2one('odoocms.hostel', 'Hostel', index=True, tracking=True)
    room_id = fields.Many2one('odoocms.hostel.room', 'Room', tracking=True, index=True)
    room_type = fields.Many2one('odoocms.hostel.room.type', 'Room Type', tracking=True)
    request_date = fields.Date('Request Date', default=fields.Date.today(), tracking=True)
    approved_date = fields.Date('Approved Date', tracking=True)
    close_date = fields.Date('Close Date', tracking=True)
    state = fields.Selection([('Draft', 'Draft'),
                              ('Approved', 'Approved'),
                              ('Close', 'Close'),
                              ('Rejected', 'Rejected')], string='Status',default='Draft', tracking=True, index=True)
    category_id = fields.Many2one('odoocms.hostel.extra.facility.category', 'Category', tracking=True, index=True)
    amount = fields.Float('Amount', tracking=True)

    @api.model
    def create(self, values):
        result = super(OdooCMSHostelExtraFacilities, self).create(values)
        if not result.name:
            result.name = self.env['ir.sequence'].next_by_code('odoocms.hostel.facilities')
        return result

    def unlink(self):
        for rec in self:
            if rec.state not in ('Draft', 'Rejected'):
                raise UserError('Records that are not in the Draft Or Rejected State cannot be deleted.')
        return super(OdooCMSHostelExtraFacilities, self).unlink()

    @api.onchange('student_code',)
    def onchange_student_code(self):
        for rec in self:
            student_id = self.env['odoocms.student'].search([('code', '=', rec.student_code)])
            if student_id:
                rec.student_id = student_id.id
                rec.session_id = student_id.session_id and student_id.session_id.id or False
                rec.program_id = student_id.program_id and student_id.program_id.id or False
                rec.hostel_id = student_id.hostel_id and student_id.hostel_id.id or False
                rec.room_id = student_id.room_id and student_id.room_id.id or False
                rec.room_type = student_id.room_type and student_id.room_type or ''

    def action_approved(self):
        for rec in self:
            if not rec.approved_date:
                raise UserError(_('Please enter the Approved Date and then Perform this Action.'))
            rec.state = 'Approved'

    def action_close(self):
        for rec in self:
            rec.state = 'Close'
            rec.close_Date = fields.Date.today()

    def action_rejected(self):
        for rec in self:
            rec.state = 'Rejected'

