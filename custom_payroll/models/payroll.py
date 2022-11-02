# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrContractInherit(models.Model):
    _inherit = 'hr.contract'

    basic = fields.Float(string="Basic")
    utility = fields.Float(string="Utility")
    house_rent = fields.Float(string="House Rent")
    inflation = fields.Float(string="Inflation Allowance")

    trial_date_end = fields.Date('Probation Period',
                                 help="End date of the trial period (if there is one).")

    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('renew', 'Renew'),
        ('close', 'Expired'),
        ('resign', 'Resign'),
        ('layoff', 'Layoff'),
        ('cancel', 'Cancelled')
    ], string='Status', group_expand='_expand_states', copy=False,
        tracking=True, help='Status of the contract', default='draft')

    # Allownces
    conveyance = fields.Float(string="Conveyance")
    mobile_allowance = fields.Float(string="Mobile Allowance")
    meal_allowance = fields.Float(string="Meal Allowance")
    fuel_allowance = fields.Float(string="Fuel Allowance")
    medical_allowance = fields.Float(string="Medical Allowance")
    insurance_allowance = fields.Float(string="Insurance Allowance")

    # Deductions
    income_tax = fields.Float(string="Income Tax")
    advances = fields.Float(string="Advances")
    eobi = fields.Float(string="EOBI")
    provident_fund = fields.Float(string="Provident Fund")
    pessi = fields.Float(string="PESSI")
    other_deductions = fields.Float(string="Other Deductions")

    # Allowances
    arears = fields.Float(string="Arears / Reimbursement")
    car_allowance = fields.Float(string="Car Monetization  Allowance")
    driver_allowance = fields.Float(string="Driver Allowance")
    over_time = fields.Float(string="Over Time")

    # Deductions
    unpaid_leaves = fields.Float(string="Absents / Leaves Without Pay")


# class HrPayslipInherit(models.Model):
#     _inherit = 'hr.payslip'
#
#     unpaid_leave = fields.Float(string="Leaves Without Pay")
#
