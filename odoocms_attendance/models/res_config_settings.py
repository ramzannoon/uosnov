# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    attendance_req_per = fields.Float(string='Attendance Percentage Required', config_parameter='odoocms_attendance.attendance_req_per',default = 75 )

