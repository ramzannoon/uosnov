from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    transcript_fee = fields.Integer(string='Transcript Fee', config_parameter='odoocms_fee.transcript_fee', default=10)
    degree_fee = fields.Integer(string='Degree Fee', config_parameter='odoocms_fee.degree_fee', default=10)
    refundable_journal_id = fields.Many2one('account.journal', string='Refundable Journal', config_parameter='odoocms_fee.refundable_journal_id')

    # Copy From cms_registration
    repeat_receipt_type = fields.Many2one('odoocms.receipt.type', string='Course Repeat Receipt Type', config_parameter='odoocms_fee.repeat_receipt_type')
    sm_defer_receipt_type = fields.Many2one('odoocms.receipt.type', string='Term Defer Receipt Type', config_parameter='odoocms_fee.sm_defer_receipt_type')
    sm_resume_receipt_type = fields.Many2one('odoocms.receipt.type', string='Term Resume Receipt Type', config_parameter='odoocms_fee.sm_resume_receipt_type')
    latefee_receipt_type = fields.Many2one('odoocms.receipt.type', string='Late Fee Receipt Type', config_parameter='odoocms_fee.latefee_receipt_type')
    re_checking_receipt_type = fields.Many2one('odoocms.receipt.type', string='Course Re-Checking Receipt Type', config_parameter='odoocms_fee.re_checking_receipt_type')
    re_checking_subject_limit = fields.Integer(string='Re-Checking Subjects Limit', config_parameter='odoocms_fee.re_checking_subject_limit', default='1')
    degree_receipt_type = fields.Many2one('odoocms.receipt.type', string='Degree Receipt Type', config_parameter='odoocms_fee.degree_receipt_type')

    # Installment Limits
    max_installment_no = fields.Char(string='Max Installment No.', config_parameter='odoocms_fee.max_installment_no', default='5')

    # First fifteen days of Due Date
    first_due_date_days = fields.Char(string='1st Due Date Days', config_parameter='odoocms_fee.first_due_date_days', default='15')
    # After fifteen days up to one month after Due Date
    second_due_date_days = fields.Char(string='2nd Due Date Days', config_parameter='odoocms_fee.second_due_date_days', default='30')

    # Fines
    fine_charge_type = fields.Selection([('percentage', 'Percentage'),
                                         ('fixed', 'Fixed Amount'),
                                         ], config_parameter='odoocms_fee.fine_charge_type', default='percentage', string="Fine Charge Type")
    first_due_date_fine = fields.Char(string='First Due Date Fine', config_parameter='odoocms_fee.first_due_date_fine', default='5')
    second_due_date_fine = fields.Char(string='Second Due Date Fine', config_parameter='odoocms_fee.second_due_date_fine', default='10')

    # Configuration for Hostel Fee Month, for how many months Fee should be Charged
    hostel_fee_charge_months = fields.Char(string='Hostel Fee Charge', config_parameter='odoocms_fee.hostel_fee_charge_months', default='6')

    # Configuration for Tax Rate to be Charge on Fee
    tax_rate = fields.Char(string="Tax Rate", config_parameter='odoocms_fee.tax_rate', default='5')
    taxable_amount = fields.Char(string="Taxable Amount", config_parameter='odoocms_fee.taxable_amount', default='200000')

    challan_validity_days = fields.Char(string='Challan Valid Days', config_parameter='odoocms_fee.challan_validity_days', default='30')

    ug_first_semester_defer_value = fields.Char(string='UG First Semester Defer Value', config_parameter='odoocms_fee.ug_first_semester_defer_value', default='100')
    pg_first_semester_defer_value = fields.Char(string='PG First Semester Defer Value', config_parameter='odoocms_fee.pg_first_semester_defer_value', default='50')
    second_semester_defer_value = fields.Char(string='Second Semester Defer Value', config_parameter='odoocms_fee.second_semester_defer_value', default='25')

    local_student_credit_hour_fee = fields.Char(string='Local Student Course Fee', config_parameter='odoocms_fee.local_student_credit_hour_fee', default='5000')
    foreign_student_credit_hour_fee = fields.Char(string='Foreign Student Course Fee', config_parameter='odoocms_fee.foreign_student_credit_hour_fee', default='40')

    # Hostel Fee Generation Schedule
    hostel_fee_charge_timing = fields.Selection([('semester_fee', 'With Semester Fee'),
                                                 ('separate_fee', 'Separate Receipt'),
                                                 ], config_parameter='odoocms_fee.hostel_fee_charge_timing', default='separate_fee', string="Hostel Fee Charge Timing")
