from odoo import models, fields, _, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class OdooCMSExamStaff(models.Model):
    _name = 'odoocms.exam.staff'
    _description = 'Exam Staff'
    _rec_name = 'first_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    first_name = fields.Char('First Name', required=True, tracking=True)
    last_name = fields.Char('Last Name', tracking=True)
    father_name = fields.Char(string="Father Name", tracking=True)
    cnic = fields.Char('CNIC', size=15, tracking=True)
    date_of_birth = fields.Date('Birth Date', required=True, tracking=True,
                                default=lambda self: self.compute_previous_year_date(fields.Date.context_today(self)))
    gender = fields.Selection([('m', 'Male'), ('f', 'Female'), ('o', 'Other')], 'Gender', tracking=True)
    marital_status = fields.Many2one('odoocms.marital.status', 'Marital Status', tracking=True)
    blood_group = fields.Selection(
        [('A+', 'A+ve'), ('B+', 'B+ve'), ('O+', 'O+ve'), ('AB+', 'AB+ve'),
         ('A-', 'A-ve'), ('B-', 'B-ve'), ('O-', 'O-ve'), ('AB-', 'AB-ve')],
        'Blood Group', tracking=True)
    religion_id = fields.Many2one('odoocms.religion', string="Religion", tracking=True)
    nationality = fields.Many2one('res.country', string='Nationality', ondelete='restrict', tracking=True)
    nationality_name = fields.Char(related='nationality.name', store=True)
    emergency_contact = fields.Char('Emergency Contact', tracking=True)
    emergency_mobile = fields.Char('Emergency Mobile', tracking=True)
    emergency_email = fields.Char('Emergency Email', tracking=True)
    emergency_address = fields.Char('Em. Address', tracking=True)
    per_state_id = fields.Many2one("res.country.state", string='Per State', ondelete='restrict',
                                   domain="[('country_id', '=?', per_country_id)]")
    per_country_id = fields.Many2one('res.country', string='Per. Country', ondelete='restrict')

    def compute_previous_year_date(self, strdate):
        tenyears = relativedelta(years=16)
        start_date = fields.Date.from_string(strdate)
        return fields.Date.to_string(start_date - tenyears)



class OdooCMSExamTag(models.Model):
    _name = 'odoocms.exam.tag'
    _description = 'Exam Tag'

    name = fields.Char("Tag", required=True)
    code = fields.Char('Tag Code')
    color = fields.Integer('Color Index')

    # Constraints
    @api.constrains('name')
    def _unique_name(self):
        Record = self.search([('name', '=', self.name)])
        if len(Record) > 1:
            raise ValidationError('Cannot have duplicated records for same Tag')

