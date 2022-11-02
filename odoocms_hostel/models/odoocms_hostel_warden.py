# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import pdb


class OdooCMSHostelWarden(models.Model):
    _name = "odoocms.hostel.warden"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hostel Managers"

    name = fields.Char('Manager Name', tracking=True)
    father_name = fields.Char('Father Name', tracking=True)
    cnic = fields.Char('CNIC', tracking=True)
    gender = fields.Selection([('Male', 'Male'),
                               ('Female', 'Female')
                               ], string='Gender', default='Male', tracking=True, index=True)
    phone = fields.Char('Phone', tracking=True)
    phone_ext = fields.Char('Ext', tracking=True)
    mobile = fields.Char('Mobile', tracking=True)
    email = fields.Char('Email', tracking=True)
    hostel_id = fields.Many2one('odoocms.hostel', 'Hostel', tracking=True)
    designation = fields.Char('Designation', tracking=True)
    appointment_date = fields.Date('Appointment Date', tracking=True)
    terminate_date = fields.Date('Terminate Date', tracking=True)
    active = fields.Boolean('Active', default=True, tracking=True)
    notes = fields.Text('Remarks', tracking=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('lock', 'Locked')
                              ], string='Status', default='draft', tracking=True)

    @api.model
    def create(self, values):
        result = super(OdooCMSHostelWarden, self).create(values)
        return result

    def unlink(self):
        return super(OdooCMSHostelWarden, self).unlink()

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'
