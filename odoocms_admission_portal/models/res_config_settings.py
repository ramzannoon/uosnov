# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    registration_fee = fields.Float(string='Registration Fee', default=1000.00 , config_parameter='odoocms_admission_portal.registration_fee')
    additional_fee = fields.Float(string='Additional Fee', default=1000.00 , config_parameter='odoocms_admission_portal.additional_fee')
    registration_fee_international = fields.Float(string='Registration Fee International', default=100.00 , config_parameter='odoocms_admission_portal.registration_fee_international')
    account_payable = fields.Char(string = "1st: Fee Payable At", config_parameter='odoocms_admission_portal.account_payable')
    account_title = fields.Char(string ='1st: Account Title', config_parameter='odoocms_admission_portal.account_title')
    account_no = fields.Char(string ='1st: Account Number', config_parameter='odoocms_admission_portal.account_no')

    account_payable2 = fields.Char(string = "2nd: Fee Payable At", config_parameter='odoocms_admission_portal.account_payable2')
    account_title2 = fields.Char(string ='2nd: Account Title',  config_parameter='odoocms_admission_portal.account_title2')
    account_no2 = fields.Char(string ='2nd: Account Number', config_parameter='odoocms_admission_portal.account_no2')


class Company(models.Model):
    _inherit = 'res.company'

    admission_mail = fields.Char(string='Admission office Email')
    admission_phone = fields.Char(string='Admission office Phone')
    admission_invoice = fields.Integer('Admission Invoice',default=4)