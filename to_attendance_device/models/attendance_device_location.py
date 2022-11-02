from odoo import models, fields

from odoo.addons.base.models.res_partner import _tz_get


class AttendanceDeviceLocation(models.Model):
    _name = 'attendance.device.location'
    _description = 'Device Location'

    name = fields.Char(string='Name', required=True, translate=True)
    tz = fields.Selection(_tz_get, string='Time zone', default=lambda self: self.env.context.get('tz') or self.env.user.tz,
                          help="The device's timezone, used to output proper date and time values "
                               "inside attendance reports. It is important to set a value for this field.")

