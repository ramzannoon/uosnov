from odoo import fields, models, api


class HRApplicant(models.Model):
    _inherit = "hr.applicant"

    address = fields.Char('Address',)
    zip_code = fields.Integer('Zip Code')
    country = fields.Char('Country')
    city = fields.Char(string="City")
    province = fields.Char('Province')
    birth_date = fields.Date('Birth Date')
    citizen = fields.Boolean('City Residence')
    worked_before = fields.Boolean('Worked Before')
    skills = fields.Char('Skills')
    qualification = fields.Char('Qualification')

    current_employment = fields.Char('Current Employment')
    position = fields.Char('Position')
    sallary = fields.Char('Sallary Expected')
    proposed_sallary_new = fields.Char('Proposed Sallary')
    reason = fields.Char('Reason')
    resume_attach = fields.Binary(string='Resume', attachment=True)
    signature_attach = fields.Binary(string='Signature', attachment=True)

    reference_1 = fields.Char('Reference 1')
    relationship = fields.Char('Relationship')
    years_Acquainted = fields.Char('Years Acquainted')
    reference_1_phone = fields.Char('Phone')
    reference_1_email = fields.Char('Email')

    reference_2 = fields.Char('Reference 2')
    relationship_reference_2 = fields.Char('Relationship')
    years_Acquainted_2 = fields.Char('Years Acquainted')
    reference_2_phone = fields.Char('Phone')
    reference_2_email = fields.Char('Email')

    high_school = fields.Char('Masters')
    number_of_years_attended = fields.Char('Number of Years Attended')
    graduated = fields.Boolean('Graduated')
    area_of_degree_stud = fields.Char('Area of Degree/Study')

    high_school_2 = fields.Char('MS/MPhil')
    number_of_years_attended_2 = fields.Char('Number of Years Attended')
    graduated_2 = fields.Boolean('Graduated')
    # area_of_degree_stud = fields.Char('Area of Degree/Study')

    empl_desired_position_applying_for = fields.Char('Position Applied for')
    desired_date = fields.Date('Date')
    empl_desired_sallary = fields.Char('Desired Sallary')

    previous_employer_1 = fields.Char('Previous Employment 1')
    previous_employer_start_date = fields.Date('Start Date')
    previous_employer_end_date = fields.Date('End Date')
    previous_employer_salary = fields.Char('Previous Sallary')
    previous_employer_position = fields.Char('Position')
    previous_employer_reasonleave = fields.Char('Reason for leave')


    previous_employer_2 = fields.Char('Previous Employment 2')
    previous_employer_start_date_2 = fields.Date('Start Date')
    previous_employer_end_date_2 = fields.Date('End Date')
    previous_employer_salary_2 = fields.Char('Previous Sallary')
    previous_employer_position_2 = fields.Char('Position')
    previous_employer_reasonleave_2 = fields.Char('Reason for leave')
    country = fields.Char("Country")

    def open_website_url(self):
        # self.ensure_one()
        # res = self.open_website_url()
        # res['url'] = self.website_url
        return







