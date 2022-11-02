# -*- coding: utf-8 -*-
from odoo import models, fields, api


class EmployeeType(models.Model):
    _name = 'employee.type'
    _description = 'Employee Type'

    name = fields.Char(string='Name')
