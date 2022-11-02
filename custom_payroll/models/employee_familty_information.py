# -*- coding: utf-8 -*-
from odoo import models, fields, api


class EmployeeFamilyInformation(models.Model):
    _name = 'employee.family.information'
    _description = 'Employee Family Information'

    employee_id = fields.Many2one('hr.employee', string="Employees")
    name = fields.Char(string='Name')
    relationship = fields.Selection([('parent', 'Parent'),
                                     ('wife', 'Wife'),
                                     ('children', 'Children')], string="Relationship")
    cnic_no = fields.Char(string='CNIC/B-Form')
    dob = fields.Date(string='DOB')
