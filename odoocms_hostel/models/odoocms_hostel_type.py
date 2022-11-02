# See LICENSE file for full copyright and licensing details.
from lxml import etree
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta as rd
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class OdooCMSHostelFreeUnits(models.Model):
    _name = 'odoocms.hostel.free.units'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'This Model Will Contain the Information About Hostels Free Units'

    name = fields.Char('Name', tracking=True)
    sequence = fields.Integer('Sequence')
    hostel_id = fields.Many2one('odoocms.hostel', 'Hostel', tracking=True, index=True)
    from_date = fields.Date('From Date', tracking=True)
    to_date = fields.Date('To Date', tracking=True)
    free_units = fields.Float('Fee Units', tracking=True)
    state = fields.Selection([('draft', 'Draft'), ('lock', 'Locked')], string='Status', default='draft', tracking=True)

    @api.model
    def create(self, values):
        result = super(OdooCMSHostelFreeUnits, self).create(values)
        if not result.name:
            result.name = self.env['ir.sequence'].next_by_code('odoocms.hostel.fee.units')
        return result

    def unlink(self):
        return super(OdooCMSHostelFreeUnits, self).unlink()

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'


class OdooCMSHostelType(models.Model):
    _name = 'odoocms.hostel.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'This Model Will Contain the Information About the type of Hostel'

    name = fields.Char('Hostel Name', required=True, help="Name of Hostel")
    code = fields.Char('Code', tracking=True)
    sequence = fields.Char('Sequence')
    type = fields.Selection([('Boys', 'Boys'),
                             ('Girls', 'Girls'),
                             ('Common', 'Common')], 'Hostel Type', help="Type of Hostel", required=True, default='Boys', tracking=True, index=True)
    other_info = fields.Text('Other Information')
    active = fields.Boolean('Active', default=True)
    room_ids = fields.One2many('odoocms.hostel.room', 'hostel_type_id', 'Rooms')
    state = fields.Selection([('draft', 'Draft'), ('lock', 'Locked')], string='Status', default='draft', tracking=True)

    @api.model
    def create(self, values):
        result = super(OdooCMSHostelType, self).create(values)
        return result

    def unlink(self):
        return super(OdooCMSHostelType, self).unlink()

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'
