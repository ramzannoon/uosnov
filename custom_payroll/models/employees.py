# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HREmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    employee_address = fields.Char(string="Employee Address")
    religion = fields.Char(string="Religion")
    blood_group = fields.Selection([('a+', 'A+'), ('a-', 'A-'), ('b+', 'B+'), ('b-', 'B-'), ('o+', 'O+'), ('o-', 'O-'),
                                    ('ab-', 'AB-'), ('ab+', 'AB+')],
                                   string='Blood Group', required=True, default='a+', tracking=True)
    emergency_address = fields.Char(string="Emergency Contact Address")

    ref_one_name = fields.Char(string="Ref one Name")
    ref_one_phone = fields.Char(string="Ref one Phone")
    ref_one_relation = fields.Char(string="Ref one Relation")

    ref_two_name = fields.Char(string="Ref two Name")
    ref_two_phone = fields.Char(string="Ref two Phone")
    ref_two_relation = fields.Char(string="Ref two Relation")

    employee_type = fields.Many2one('employee.type', string="Employee Type")
    father_name = fields.Char(string="Husband/Father Name")
    next_to_kin = fields.Char(string="Next to Kin")
    number_of_next_to_kin = fields.Char(string="Number of Next to Kin")
    permanent_address = fields.Char(string="Permanent Address")

    family_information_ids = fields.One2many('employee.family.information', 'employee_id', string='Family Information')
