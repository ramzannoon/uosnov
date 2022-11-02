from odoo import fields, models, _, api
import logging
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


_logger = logging.getLogger(__name__)

try:
    from num2words import num2words
except ImportError:
    _logger.warning("The num2words python library is not installed, amount-to-text features won't be fully available.")
    num2words = None


class OdooCMSAdmissionSCApplication(models.Model):
    _name = 'odoocms.sc.application'
    _description = 'Applications for the SC admission'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    READONLY_STATES = {
        'approve': [('readonly', True)],
        'done': [('readonly', True)],
        'reject': [('readonly', True)],
    }

    @api.depends('first_name', 'middle_name', 'last_name')
    def _get_applicant_name(self):
        for applicant in self:
            name = applicant.first_name or ''
            if applicant.middle_name:
                name = name + ' ' + applicant.middle_name
            if applicant.last_name:
                name = name + ' ' + applicant.last_name
            applicant.name = name

    state = fields.Selection(
        [('draft', 'Draft'), ('approve', 'Approve'), ('reject', 'Reject'), ('done', 'Done'), ], string='Status',
        default='draft', tracking=True)

    first_name = fields.Char(string='First Name', help="First name of Student", states=READONLY_STATES)
    middle_name = fields.Char(string='Middle Name', help="Middle name of Student", states=READONLY_STATES)
    last_name = fields.Char(string='Last Name', help="Last name of Student", states=READONLY_STATES)

    register_id = fields.Many2one('odoocms.admission.register', 'Admission Register', states=READONLY_STATES)
    academic_session_id = fields.Many2one('odoocms.academic.session', 'Academic Session',
                                          related='register_id.academic_session_id', store=True)
    student_id = fields.Many2one('odoocms.student', 'Student')
    is_hafiz = fields.Boolean('Is Hafiz-e-Quran?', states=READONLY_STATES)

    entryID = fields.Char('Entry ID', states=READONLY_STATES, compute='_get_entry', store=True)
    application_no = fields.Char(string='Application  No', copy=False, readonly=True, index=True,
                                 default=lambda self: _('New'))
    application_date = fields.Datetime('Application Date', copy=False, states=READONLY_STATES,
                                       default=lambda self: fields.Datetime.now())
    course_id = fields.Many2one('odoocms.short.course', string="Selected Course", required=True)

    date_of_birth = fields.Date(string="Date Of Birth", required=True)
    nationality = fields.Many2one('res.country', string='Nationality', ondelete='restrict',
                                  help="Select the Nationality")
    domicile = fields.Char(string='Domicile', states=READONLY_STATES)
    domicile_id = fields.Many2one('odoocms.domicile', string='Domicile ID', states=READONLY_STATES)

    name = fields.Char('Name', compute='_get_applicant_name', store=True)
    cnic = fields.Char(string='CNIC')
    image = fields.Binary(string='Image', attachment=True, help="Provide the image of the Student")

    email = fields.Char(string='Email', required=True, )
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    gender = fields.Selection([('m', 'Male'), ('f', 'Female'), ('o', 'Other')],
                              string='Gender', default='m', tracking=True)
    no_of_sibling = fields.Text(string='Brothers & Sisters you have? (Who is elder then you)')
    family_in_university = fields.Text(
        string='How many Brothers & Sister you have in University level Education or Completed their University Level Education?')
    # Added last 6
    father_name = fields.Char(string="Father Name")
    father_cnic = fields.Char(string='Father CNIC')
    father_email = fields.Char(string='Father Email')
    father_mobile = fields.Char(string='Father Mobile')
    father_occupation = fields.Char(string='Father Occupation')
    father_income = fields.Integer('Father Income')
    father_education = fields.Selection([
        ('matric', 'Matric'),
        ('intermediate', 'FA/Fsc or Equivalent'),
        ('bachlors', 'BA / BS or Equivalent'),
        ('postgraduate', 'M-PHIL / MS or Equivalent'),
        ('doctorate', 'PhD or Equivalent'),
        ('illiterate', 'Illiterate'),
    ], 'Father Education')
    father_status = fields.Selection([('alive', 'Alive'), ('deceased', 'Deceased')], 'Father Status', default='alive')

    guardian_name = fields.Char('Guardian Name')
    guardian_occupation = fields.Char(string='Occupation')
    guardian_cnic = fields.Char('CNIC')
    guardian_relation = fields.Char('Relation')
    guardian_mobile = fields.Char(string='Mobile')
    guardian_landline = fields.Char(string='Landline')
    guardian_address = fields.Char(string='Residential Address')

    emergency_name = fields.Char('Emergency Name')
    emergency_mobile = fields.Char('Emergency Mobile')
    emergency_relation = fields.Char('Emergency Relation')

    roll_number = fields.Char(string='Roll Number', compute='_compute_roll_number', store=True)

    active = fields.Boolean(string='Active', default=True)
    religion_id = fields.Many2one('odoocms.religion', string="Religion")
    blood_group = fields.Selection(
        [('A+', 'A+ve'), ('B+', 'B+ve'), ('O+', 'O+ve'), ('AB+', 'AB+ve'),
         ('A-', 'A-ve'), ('B-', 'B-ve'), ('O-', 'O-ve'), ('AB-', 'AB-ve'), ('N', 'Not Known')],
        'Blood Group', default='N', tracking=True, required=True)

    street = fields.Char(string='Street', help="Enter the First Part of Address")
    street2 = fields.Char(string='Street2', help="Enter the Second Part of Address")
    city = fields.Char(string='City', help="Enter the City Name")
    zip = fields.Char(change_default=True)
    state_id = fields.Many2one("res.country.state", string='Country State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', help="Select the Country")

    is_same_address = fields.Boolean(string="Permanent Address same as above", default=False,
                                     help="Tick the field if the Present and permanent address is same")
    per_street = fields.Char(string='Per. Street', help="Enter the First Part of Permanent Address")
    per_street2 = fields.Char(string='Per. Street2', help="Enter the First Part of Permanent Address")
    per_city = fields.Char(string='Per. City', help="Enter the City Name of Permanent Address")
    per_zip = fields.Char(change_default=True)
    per_state_id = fields.Many2one("res.country.state", string='Per State', ondelete='restrict',
                                   domain="[('country_id', '=?', per_country_id)]")
    per_country_id = fields.Many2one('res.country', string='Per. Country', ondelete='restrict',
                                     help="Select the Country")
    academic_ids = fields.One2many('odoocms.application.academic', 'sc_application_id', 'Academics',
                                   states=READONLY_STATES)
    reject_reason = fields.Many2one('odoocms.application.reject.reason', string='Reject Reason',
                                    help="Reason of Application rejection")
    description = fields.Text(string="Note")

    voucher_status = fields.Selection([('reject', 'Rejected'), ('accept', 'Accepted')], 'Verification Status')
    voucher_image = fields.Binary('Voucher', store=True)
    voucher_number = fields.Char('Voucher Number')
    date_voucher = fields.Date('Voucher Submission Date')
    date_submission = fields.Date('Voucher upload Date')
    company_id = fields.Many2one('res.company', string='Company')

    def application_verify(self):
        for rec in self:
            rec.write({'state': 'approve'})

    def create_student(self, view=False):
        if not self.date_of_birth:
            raise UserError('Data of Birth of %s - %s not Set.' % (self.entryID, self.name))

        semester = self.env['odoocms.semester'].search([('number', '=', 1)], limit=1)
        user = self.env['res.users'].search([('login', '=', self.entryID)])

        values = {
            'state2': 'enroll',
            'name': self.name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'father_name': self.father_name,

            'cnic': self.cnic,
            'gender': self.gender,
            'date_of_birth': self.date_of_birth,
            'blood_group': self.blood_group,
            'religion_id': self.religion_id.id,
            'nationality': self.nationality.id,

            'email': self.email,
            'mobile': self.mobile,
            'phone': self.phone,
            'image_1920': self.image,

            'id_number': self.entryID,
            'entryID': self.entryID,
            # 'user_id': self.user_id.id,

            'street': self.street,
            'street2': self.street2,
            'city': self.city,
            'zip': self.zip,
            'state_id': self.state_id.id,
            'country_id': self.country_id.id,

            'is_same_address': self.is_same_address,
            'per_street': self.per_street,
            'per_street2': self.per_street2,
            'per_city': self.per_city,
            'per_zip': self.per_zip,
            'per_state_id': self.per_state_id.id,
            'per_country_id': self.per_country_id.id,

            'application_id': self.id,
            # 'career_id': self.career_id.id,
            'sc_program_id': self.course_id.id,
            'session_id': self.academic_session_id.id,
            # 'academic_semester_id': self.register_id.academic_semester_id.id,
            'semester_id': semester.id,

            # 'admission_no': ,
            'company_id': self.company_id.id,
        }
        if user:
            values['partner_id'] = user.partner_id.id
        if not self.is_same_address:
            pass
        else:
            values.update({
                'per_street': self.street,
                'per_street2': self.street2,
                'per_city': self.city,
                'per_zip': self.zip,
                'per_state_id': self.state_id.id,
                'per_country_id': self.country_id.id,
            })

        if self.course_id:
            student = self.env['odoocms.student'].create(values)
        else:
            raise UserError(_("Please Enter Offered Program"))

        self.write({
            'state': 'done',
            'student_id': student.id,
        })

        if view:
            return {
                'name': _('Student'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'odoocms.student',
                'type': 'ir.actions.act_window',
                'res_id': student.id,
                'context': self.env.context
            }
        else:
            return student
