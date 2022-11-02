# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    allow_repeat_wo_fee = fields.Boolean(string='Allow Course Repeat before Fee Submit', config_parameter='odoocms_registration.allow_repeat_wo_fee')
    re_checking_subject_limit = fields.Integer(string='Re-Checking Subjects Limit', config_parameter='odoocms_registration.re_checking_subject_limit',default='1')
    
    allow_portal_course_del = fields.Boolean(string='Allow Course Deletion From Portal', config_parameter='odoocms_registration.allow_portal_course_del',default = False )

    repeat_allow_in_summer = fields.Boolean(string='Allow Repeat Courses in Summer', config_parameter='odoocms_registration.repeat_allow_in_summer')
    repeat_allow_in_winter = fields.Boolean(string='Allow Repeat Courses in Winter', config_parameter='odoocms_registration.repeat_allow_in_winter')

    no_registration_tags = fields.Char(string="No Registration Tags", config_parameter='odoocms_registration.no_registration_tags', default='withdrawal, suspension, suspension_of_registration')