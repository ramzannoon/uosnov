# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import pdb


class OdooCMSHostelAdmissionApplications(models.Model):
    _name = "odoocms.hostel.admission.application"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hostel Admission Applications"
    _rec_name = 'application_type'
    name = fields.Char('Name', tracking=True)
    sequence = fields.Integer('Sequence')
    tuition_invoice_paid = fields.Selection([('paid', 'Paid'),
                                             ('unpaid', 'Unpaid')], string='Tuition Fee Paid', tracking=True)

    application_type = fields.Selection([('student', 'Student'),
                                         ('faculty', 'Faculty')], string='Application Type', tracking=True, default='student')

    student_id = fields.Many2one('odoocms.student', 'Student', index=True)
    student_name = fields.Char('Student Name', related='student_id.name', compute_sudo=True, store=True, tracking=True)
    student_code = fields.Char('Student ID', related='student_id.code', related_sudo=True, compute_sudo=True, store=True, tracking=True)
    cnic = fields.Char('CNIC', related='student_id.cnic', related_sudo=True, compute_sudo=True, store=True, tracking=True)

    gender = fields.Selection([('m', 'Male'),
                               ('f', 'Female'),
                               ('o', 'Other')], related='student_id.gender', string='Gender', index=True, related_sudo=True, compute_sudo=True, store=True, tracking=True)

    career_id = fields.Many2one('odoocms.career', 'Academic Level', related='student_id.career_id', related_sudo=True, compute_sudo=True, store=True, tracking=True, index=True)
    program_id = fields.Many2one('odoocms.program', 'Academic Program', related='student_id.program_id', related_sudo=True, compute_sudo=True, store=True, tracking=True, index=True)
    institute_id = fields.Many2one('odoocms.institute', 'School', related='student_id.institute_id', related_sudo=True, compute_sudo=True, store=True, tracking=True)
    institute_code = fields.Char(related='institute_id.code', string='School Code', store=True)
    discipline_id = fields.Many2one('odoocms.discipline', 'Discipline', related='student_id.discipline_id', related_sudo=True, compute_sudo=True, store=True, tracking=True)
    campus_id = fields.Many2one('odoocms.campus', 'Campus', related='student_id.campus_id', related_sudo=True, compute_sudo=True, store=True, tracking=True)
    term_id = fields.Many2one('odoocms.academic.term', 'Current Term', related='student_id.term_id', related_sudo=True, compute_sudo=True, store=True, tracking=True)
    session_id = fields.Many2one('odoocms.academic.session', 'Academic Session', related='student_id.session_id', related_sudo=True, compute_sudo=True, store=True, tracking=True)
    semester_id = fields.Many2one('odoocms.semester', 'Semester', related='student_id.semester_id', related_sudo=True, compute_sudo=True, store=True, tracking=True)
    batch_id = fields.Many2one('odoocms.batch', string='Batch', tracking=True)

    birth_date = fields.Date('Date of Birth', related='student_id.date_of_birth', related_sudo=True, compute_sudo=True, store=True, tracking=True)
    email = fields.Char('Email', related='student_id.email', related_sudo=True, compute_sudo=True, store=True, tracking=True)
    merit_no = fields.Char('Merit No')
    mobile = fields.Char('Mobile', related='student_id.mobile', related_sudo=True, compute_sudo=True, store=True, tracking=True)
    phone = fields.Char('Phone', related='student_id.phone', related_sudo=True, compute_sudo=True, store=True, tracking=True)
    domicile_id = fields.Many2one('odoocms.domicile', 'Domicile', related='student_id.domicile_id', related_sudo=True, compute_sudo=True, store=True, tracking=True)
    nust_registration_date = fields.Date('Date of Registration at NUST')

    # Permanent Data
    per_street = fields.Char(related='student_id.per_street', related_sudo=True, compute_sudo=True, store=True)
    per_street2 = fields.Char(related='student_id.per_street2', related_sudo=True, compute_sudo=True, store=True)
    per_city = fields.Char(related='student_id.per_city', related_sudo=True, compute_sudo=True, store=True)
    per_zip = fields.Char(change_default=True, related='student_id.per_zip', related_sudo=True, compute_sudo=True, store=True)
    per_state_id = fields.Many2one("res.country.state", string='Per State', ondelete='restrict', domain="[('country_id', '=?', per_country_id)]", related='student_id.per_state_id', related_sudo=True, compute_sudo=True, store=True)
    per_country_id = fields.Many2one('res.country', string='Per. Country', ondelete='restrict', related='student_id.per_country_id', related_sudo=True, compute_sudo=True, store=True)

    # Temporary Data
    temp_street = fields.Char('Temp Street', help='Tempory Address Street1')
    temp_street2 = fields.Char('Temp Street2')
    temp_city = fields.Char('Temp City')
    temp_zip = fields.Char('Temp Zip', change_default=True)
    temp_state_id = fields.Many2one("res.country.state", string='Temp State', ondelete='restrict', domain="[('country_id', '=?', temp_country_id)]")
    temp_country_id = fields.Many2one('res.country', string='Temp Country', ondelete='restrict')

    # Parent Data
    father_name = fields.Char('Father Name', related='student_id.father_name', tracking=True, store=True)
    father_income = fields.Integer('Father Income', related='student_id.father_income', tracking=True, store=True)
    occupation = fields.Char('Occupation')
    father_cnic = fields.Char('Father CNIC')
    father_mobile = fields.Char('Father Mobile')
    father_residence_phone = fields.Char('Father Residence Phone')
    father_email = fields.Char('Father Email')
    mother_mobile = fields.Char('Mother Cell No')
    office_no = fields.Char('Office No')

    # Medical Records
    any_medical_history = fields.Boolean('Any Medical History?')
    disease_detail = fields.Text('Disease Detail')
    regularly_taken_medicine = fields.Char('Regularly Taken Medicine')
    blood_group = fields.Selection([('A+', 'A+ve'), ('B+', 'B+ve'), ('O+', 'O+ve'),
                                    ('AB+', 'AB+ve'), ('A-', 'A-ve'), ('B-', 'B-ve'),
                                    ('O-', 'O-ve'), ('AB-', 'AB-ve')], string='Blood Group')

    # Relatives / Visitors
    visitor_ids = fields.One2many('odoocms.hostel.visitor', 'admission_application_id', 'Visitors')
    special_info_ids = fields.One2many('odoocms.hostel.student.special.info', 'hostel_adm_application_id', 'Special info')

    notes = fields.Text('Remarks', tracking=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('approved', 'Approved'),
                              ('rejected', 'Rejected')], string='Status', default='draft', tracking=True)

    hostel_id = fields.Many2one('odoocms.hostel', 'Hostel', tracking=True, index=True)
    room_type = fields.Many2one('odoocms.hostel.room.type', 'Room Type', tracking=True)
    room_id = fields.Many2one('odoocms.hostel.room', tracking=True)

    emergency_contact = fields.Char('Emergency Contact', related='student_id.emergency_contact', related_sudo=True, compute_sudo=True, store=True)
    emergency_mobile = fields.Char('Emergency Mobile', related='student_id.emergency_mobile', related_sudo=True, compute_sudo=True, store=True)
    emergency_email = fields.Char('Emergency Email', related='student_id.emergency_email', related_sudo=True, compute_sudo=True, store=True)
    emergency_address = fields.Char('Em. Address', related='student_id.emergency_address', related_sudo=True, compute_sudo=True, store=True)
    emergency_city = fields.Char('Em. Street', related='student_id.emergency_city', related_sudo=True, compute_sudo=True, store=True)

    father_job_location = fields.Char('Father Job Location/Address')
    guardian_name = fields.Char('Guardian Name', related='student_id.guardian_name', compute_sudo=True, store=True, tracking=True)
    guardian_occupation = fields.Char('Guardian Occupation')
    any_psychiatrists_problem = fields.Boolean('Suffering From any Psychiatrists Issue')

    spouse_name = fields.Char('Spouse Name')
    spouse_cnic = fields.Char('Spouse CNIC')
    spouse_mobile = fields.Char('Spouse Mobile')
    child_no = fields.Char('Number of Children')

    disability = fields.Boolean('Any Disability')
    disability_history = fields.Text('Disability History')

    orphan = fields.Boolean('Orphan')
    shaheed = fields.Boolean('Shaheed')
    undertaking = fields.Boolean('Undertaking')

    # Faculty
    faculty_id = fields.Many2one('odoocms.faculty.staff', 'Faculty', index=True)
    faculty_name = fields.Char('Faculty Name', related='faculty_id.name', compute_sudo=True, store=True, tracking=True)
    faculty_code = fields.Char('Faculty ID', related='faculty_id.code', related_sudo=True, compute_sudo=True,
                               store=True, tracking=True)
    faculty_cnic = fields.Char('CNIC', related_sudo=True, compute_sudo=True, store=True,
                               tracking=True)

    faculty_gender = fields.Selection([('m', 'Male'),
                                       ('f', 'Female'),
                                       ('o', 'Other')], related='faculty_id.gender', string='Gender', index=True,
                                      related_sudo=True, compute_sudo=True, store=True, tracking=True)

    faculty_birth_date = fields.Date('Date of Birth', related='faculty_id.date_of_birth', related_sudo=True, compute_sudo=True,
                                     store=True, tracking=True)
    faculty_email = fields.Char('Email', related='faculty_id.work_email', related_sudo=True, compute_sudo=True, store=True,
                                tracking=True)
    faculty_mobile = fields.Char('Mobile', related='faculty_id.mobile_phone', related_sudo=True, compute_sudo=True, store=True,
                                 tracking=True)
    faculty_phone = fields.Char('Phone', related='faculty_id.phone', related_sudo=True, compute_sudo=True, store=True,
                                tracking=True)
    faculty_term_id = fields.Many2one('odoocms.academic.term', 'Current Term', related='faculty_id.term_id', related_sudo=True, compute_sudo=True, store=True, tracking=True)

    # Permanent Data
    faculty_per_street = fields.Char(string="Street")
    faculty_per_street2 = fields.Char(string="Street 2")
    faculty_per_city = fields.Char(string="City")
    faculty_per_zip = fields.Char(string="Zip")
    faculty_per_state_id = fields.Many2one("res.country.state", string='Per State', ondelete='restrict',
                                           domain="[('country_id', '=?', per_country_id)]",
                                           related_sudo=True, compute_sudo=True, store=True)
    faculty_per_country_id = fields.Many2one('res.country', string='Per. Country', ondelete='restrict',
                                             related_sudo=True, compute_sudo=True,
                                             store=True)
    # Emergency Data
    faculty_emergency_contact = fields.Char('Emergency Contact', related='faculty_id.employee_id.emergency_contact', related_sudo=True, compute_sudo=True, store=True)
    faculty_emergency_mobile = fields.Char('Emergency Mobile', related='faculty_id.employee_id.emergency_phone', related_sudo=True, compute_sudo=True, store=True)
    faculty_emergency_address = fields.Char('Em. Address', related='faculty_id.employee_id.emergency_address', related_sudo=True, compute_sudo=True, store=True)

    # Parent Data
    faculty_father_name = fields.Char('Father Name', related='faculty_id.father_name', tracking=True, store=True)
    faculty_occupation = fields.Char('Occupation')
    faculty_father_cnic = fields.Char('Father CNIC')
    faculty_father_mobile = fields.Char('Father Mobile')
    faculty_father_residence_phone = fields.Char('Father Residence Phone')
    faculty_father_email = fields.Char('Father Email')
    faculty_mother_mobile = fields.Char('Mother Cell No')
    faculty_office_no = fields.Char('Office No')

    @api.model
    def create(self, values):
        result = super(OdooCMSHostelAdmissionApplications, self).create(values)
        if not result.name:
            result.name = self.env['ir.sequence'].next_by_code('odoocms.hostel.admission.application')
        return result

    def unlink(self):
        return super(OdooCMSHostelAdmissionApplications, self).unlink()

    def action_approve(self):
        for rec in self:
            rec.state = 'approved'

    def action_reject(self):
        for rec in self:
            rec.state = 'rejected'


class OdooCMSHostelVisitor(models.Model):
    _name = "odoocms.hostel.visitor"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hostel Visitor"

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence')
    cnic_no = fields.Char('NIC NO')
    relation_id = fields.Many2one('odoocms.hostel.visitor.relation', 'Visitor Relation')
    admission_application_id = fields.Many2one('odoocms.hostel.admission.application', 'Admission Application')
    student_id = fields.Many2one('odoocms.student', 'Student')
    faculty_id = fields.Many2one('odoocms.faculty', 'Student')
    cnic_front = fields.Binary('CNIC Front', attachment=True)
    cnic_back = fields.Binary('CNIC Back', attachment=True)


class OdooCMSHostelVisitorRelation(models.Model):
    _name = "odoocms.hostel.visitor.relation"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hostel Visitor Relation"

    sequence = fields.Integer('Sequence')
    name = fields.Char('Name', required=True, tracking=True, index=True)
    state = fields.Selection([('draft', 'Draft'), ('lock', 'Locked')], string='Status', default='draft', tracking=True)

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'


class OdooCMSHostelStudentSpecialInfo(models.Model):
    _name = "odoocms.hostel.student.special.info"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hostel Students Special Info"

    sequence = fields.Integer('Sequence')
    name = fields.Char('Name', tracking=True, default='New')
    info_type = fields.Selection([('accident', 'Accident'),
                                  ('student_analysis', 'Analysis of Student'),
                                  ('buddy_system', 'Buddy System'),
                                  ('family_issue', 'Family Issue'),
                                  ('other', 'Any Other')], string="Type", tracking=True, index=True)
    remarks = fields.Text('Remarks')
    date = fields.Date('Date', default=fields.Date.today())
    student_id = fields.Many2one('odoocms.student', 'Student')
    hostel_adm_application_id = fields.Many2one('odoocms.hostel.admission.application', 'Adm Application Ref.')

    state = fields.Selection([('draft', 'Draft'),
                              ('lock', 'Locked')], string='Status', default='draft', tracking=True)

    @api.model
    def create(self, values):
        result = super(OdooCMSHostelStudentSpecialInfo, self).create(values)
        if not result.name:
            result.name = self.env['ir.sequence'].next_by_code('odoocms.hostel.student.special.info')
        return result

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'


class OdooCMSHostelFacultySpecialInfo(models.Model):
    _name = "odoocms.hostel.faculty.special.info"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hostel Students Special Info"

    sequence = fields.Integer('Sequence')
    name = fields.Char('Name', tracking=True, default='New')
    info_type = fields.Selection([('accident', 'Accident'),
                                  ('student_analysis', 'Analysis of Student'),
                                  ('buddy_system', 'Buddy System'),
                                  ('family_issue', 'Family Issue'),
                                  ('other', 'Any Other')], string="Type", tracking=True, index=True)
    remarks = fields.Text('Remarks')
    date = fields.Date('Date', default=fields.Date.today())
    faculty_id = fields.Many2one('odoocms.faculty.staff', 'Faculty')
    hostel_adm_application_id = fields.Many2one('odoocms.hostel.admission.application', 'Adm Application Ref.')

    state = fields.Selection([('draft', 'Draft'),
                              ('lock', 'Locked')], string='Status', default='draft', tracking=True)

    @api.model
    def create(self, values):
        result = super(OdooCMSHostelFacultySpecialInfo, self).create(values)
        if not result.name:
            result.name = self.env['ir.sequence'].next_by_code('odoocms.hostel.faculty.special.info')
        return result

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'
