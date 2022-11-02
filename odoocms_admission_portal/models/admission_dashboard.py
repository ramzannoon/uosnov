# -*- coding: utf-8 -*-

from collections import defaultdict
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
from pytz import utc
from odoo import models, fields, api, _
from odoo.http import request
from odoo.tools import float_utils
ROUNDING_FACTOR = 16


class Employee(models.Model):
    _inherit = 'hr.employee'

    birthday = fields.Date('Date of Birth', groups="base.group_user")

    @api.model
    def get_user_employee_details(self):
        uid = request.session.uid
        employee = self.env['hr.employee'].sudo().search_read([('user_id', '=', uid)], limit=1)
        data = {
            'total_applications' : self.get_total_applications(),
            'total_invoice_downloaded': self.get_total_invoice_downloaded(),
            'total_invoice_uploaded': self.get_total_invoice_uploaded(),
            'total_voucher_verified': self.get_total_voucher_verified(),
            'total_voucher_unverified': self.get_total_voucher_unverified(),
            'total_academic_detail': self.get_total_academic_detail(),
            'total_document_uploaded': self.get_total_document_uploaded(),
            'total_admissions': self.get_total_admissions(),
            'total_final_applicant_score': self.get_total_final_applicant_score(),
            'total_confirm_applicants': self.get_confirm_applications(),
        }

        if employee:
            employee[0].update(data)
            return employee
        else:
            return False


    @api.model
    def get_total_applications(self):
        rec_count=0
        registers = self.env['odoocms.admission.register'].search([('state', '=', 'application')])
        if registers:
            rec_count = self.env['odoocms.application'].search_count([('register_id','in',registers.ids)])
        return rec_count

    @api.model
    def get_confirm_applications(self):
        rec_count = 0
        registers = self.env['odoocms.admission.register'].search([('state', '=', 'application')])
        if registers:
            rec_count = self.env['odoocms.application'].search_count([('register_id', 'in', registers.ids),('state','=','confirm')])
        return rec_count

    @api.model
    def get_total_invoice_downloaded(self):
        rec_count = 0
        registers = self.env['odoocms.admission.register'].search([('state', '=', 'application')])
        if registers:
            rec_count = self.env['odoocms.application'].search_count([('register_id', 'in', registers.ids),('fee_voucher_state','!=','no')])
        return rec_count

    @api.model
    def get_total_invoice_uploaded(self):
        rec_count = 0
        registers = self.env['odoocms.admission.register'].search([('state', '=', 'application')])
        if registers:
            rec_count = self.env['odoocms.application'].search_count(
                [('register_id', 'in', registers.ids), ('fee_voucher_state', '=', 'upload')])
        return rec_count

    @api.model
    def get_total_voucher_verified(self):
        rec_count = 0
        registers = self.env['odoocms.admission.register'].search([('state', '=', 'application')])
        if registers:
            rec_count = self.env['odoocms.application'].search_count(
                [('register_id', 'in', registers.ids), ('fee_voucher_state', '=', 'verify')])
        return rec_count

    @api.model
    def get_total_voucher_unverified(self):
        rec_count = 0
        registers = self.env['odoocms.admission.register'].search([('state', '=', 'application')])
        if registers:
            rec_count = self.env['odoocms.application'].search_count(
                [('register_id', 'in', registers.ids), ('fee_voucher_state', '=', 'unverify')])
        return rec_count

    @api.model
    def get_total_academic_detail(self):
        rec_count = 0
        template = self.env.ref('odoocms_admission_portal.education_top_detail')
        step = self.env['odoocms.application.steps'].sudo().search([('template', '=', template.id)])
        
        registers = self.env['odoocms.admission.register'].search([('state', '=', 'application')])
        if registers:
            rec_count = self.env['odoocms.application'].search_count(
                [('register_id', 'in', registers.ids), ('step_number', '=', step.sequence)])
        return rec_count

    @api.model
    def get_total_document_uploaded(self):
        rec_count = 0
        template = self.env.ref('odoocms_admission_portal.admission_documents_upload')
        step = self.env['odoocms.application.steps'].sudo().search([('template', '=', template.id)])
        
        registers = self.env['odoocms.admission.register'].search([('state', '=', 'application')])
        if registers:
            rec_count = self.env['odoocms.application'].search_count(
                [('register_id', 'in', registers.ids), ('step_number', '=', step.sequence)])
        return rec_count

    @api.model
    def get_total_admissions(self):
        rec_count = 0
        registers = self.env['odoocms.admission.register'].search([('state', '=', 'application')])
        if registers:
            rec_count = self.env['odoocms.application'].search_count(
                [('register_id', 'in', registers.ids), ('state', '=', 'done')])
        return rec_count

    @api.model
    def get_total_final_applicant_score(self):
        rec_count = 0
        registers = self.env['odoocms.admission.register'].search([('state', '=', 'application')])
        if registers:
            rec_count = self.env['odoocms.application'].search_count(
                [('register_id', 'in', registers.ids), ('state', '=', 'done')])
        return rec_count
