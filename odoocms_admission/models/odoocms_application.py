from odoo import fields, models, _, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools.safe_eval import safe_eval
import pdb
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from odoo.tools.safe_eval import safe_eval
from odoo import tools
import pdb
import logging

_logger = logging.getLogger(__name__)

try:
    from num2words import num2words
except ImportError:
    _logger.warning("The num2words python library is not installed, amount-to-text features won't be fully available.")
    num2words = None


class OdooCMSAdmissionApplication(models.Model):
    _name = 'odoocms.application'
    _description = 'Applications for the admission'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    READONLY_STATES = {
        'approve': [('readonly', True)],
        'open': [('readonly', True)],
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

    choice_one = fields.Many2one('odoocms.program', string='Choice 1')
    choice_two = fields.Many2one('odoocms.program', string='Choice 2')
    choice_three = fields.Many2one('odoocms.program', string='Choice 3')

    domicile = fields.Char(string='Domicile', states=READONLY_STATES)
    domicile_id = fields.Many2one('odoocms.domicile', string='Domicile ID', states=READONLY_STATES)
    first_name = fields.Char(string='First Name', help="First name of Student", states=READONLY_STATES)
    middle_name = fields.Char(string='Middle Name', help="Middle name of Student", states=READONLY_STATES)
    last_name = fields.Char(string='Last Name', help="Last name of Student", states=READONLY_STATES)
    name = fields.Char('Name', compute='_get_applicant_name', store=True)
    cnic = fields.Char(string='CNIC')
    image = fields.Binary(string='Image', attachment=True, help="Provide the image of the Student")

    email = fields.Char(string='Email', required=True, )
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    no_of_sibling = fields.Text(string='Brothers & Sisters you have? (Who is elder then you)')
    family_in_university = fields.Text(
        string='How many Brothers & Sister you have in University level Education or Completed their University Level Education?')
    # Added last 6
    father_name = fields.Char(string="Father Name")
    father_cnic = fields.Char(string='Father CNIC')
    father_email = fields.Char(string='Father Email')
    father_mobile = fields.Char(string='Father Mobile')
    father_occupation = fields.Char(string='Father Occupation')
    father_education = fields.Selection([
        ('matric', 'Matric'),
        ('intermediate', 'FA/Fsc or Equivalent'),
        ('bachlors', 'BA / BS or Equivalent'),
        ('postgraduate', 'M-PHIL / MS or Equivalent'),
        ('doctorate', 'PhD or Equivalent'),
        ('illiterate', 'Illiterate'),
    ], 'Father Education')
    father_status = fields.Selection([('alive', 'Alive'), ('deceased', 'Deceased')], 'Father Status', default='alive')

    mother_name = fields.Char(string="Mother Name")
    mother_education = fields.Selection([
        ('matric', 'Matric'),
        ('intermediate', 'FA/Fsc or Equivalent'),
        ('bachlors', 'BA / BS or Equivalent'),
        ('postgraduate', 'M-PHIL / MS or Equivalent'),
        ('doctorate', 'PhD or Equivalent'),
        ('illiterate', 'Illiterate'),
    ], 'Mother Education')
    mother_status = fields.Selection([('alive', 'Alive'), ('deceased', 'Deceased')], 'Mother Status', default='alive')
    single_parent = fields.Boolean('Single Parent', default=False)

    roll_number = fields.Char(string='Roll Number', compute='_compute_roll_number', store=True)
    lead_generate = fields.Boolean(string='Lead Generate', dafault=False)

    @api.depends('application_no')
    def _compute_roll_number(self):
        for rec in self:
            if rec.application_no:
                roll = 0
                roll = rec.application_no[-5:]
                rec.roll_number = roll

    father_profession = fields.Many2one('odoocms.profs', 'Father Profession')
    father_income = fields.Integer('Father Income')
    father_cell = fields.Char('Father Cell')
    guardian_name = fields.Char('Guardian Name')
    guardian_mobile = fields.Char('Guardian Mobile')
    degree = fields.Many2one('odoocms.degree', 'Last Degree')
    religion_id = fields.Many2one('odoocms.religion', string="Religion")

    emergency_name = fields.Char('Emergency Name')
    emergency_mobile = fields.Char('Emergency Mobile')
    emergency_relation = fields.Char('Emergency Relation')

    date_of_birth = fields.Date(string="Date Of Birth", required=True)
    gender = fields.Selection([('m', 'Male'), ('f', 'Female'), ('o', 'Other')],
                              string='Gender', default='m', tracking=True)  # char
    blood_group = fields.Selection(
        [('A+', 'A+ve'), ('B+', 'B+ve'), ('O+', 'O+ve'), ('AB+', 'AB+ve'),
         ('A-', 'A-ve'), ('B-', 'B-ve'), ('O-', 'O-ve'), ('AB-', 'AB-ve'), ('N', 'Not Known')],
        'Blood Group', default='N', tracking=True)
    nationality = fields.Many2one('res.country', string='Nationality', ondelete='restrict',
                                  help="Select the Nationality")

    application_no = fields.Char(string='Application  No', copy=False, readonly=True, index=True,
                                 default=lambda self: _('New'))
    application_date = fields.Datetime('Application Date', copy=False, states=READONLY_STATES,
                                       default=lambda self: fields.Datetime.now())

    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one('res.company', string='Institute', default=lambda self: self.env.user.company_id)

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

    description = fields.Text(string="Note")
    # class_id = fields.Many2one('odoocms.class', string="Class")

    document_count = fields.Integer(compute='_document_count', string='# Documents')
    verified_by = fields.Many2one('res.users', string='Verified by', help="The Document is Verified By")
    reject_reason = fields.Many2one('odoocms.application.reject.reason', string='Reject Reason',
                                    help="Reason of Application rejection")

    register_id = fields.Many2one('odoocms.admission.register', 'Admission Register', states=READONLY_STATES)
    academic_session_id = fields.Many2one('odoocms.academic.session', 'Academic Session',
                                          related='register_id.academic_session_id', store=True)
    career_id = fields.Many2one('odoocms.career', 'Academic Level', related='register_id.career_id', store=True)

    academic_ids = fields.One2many('odoocms.application.academic', 'application_id', 'Academics',
                                   states=READONLY_STATES)
    preference_ids = fields.One2many('odoocms.application.preference', 'application_id', 'Preferences',
                                     states=READONLY_STATES)

    ssc_marks = fields.Integer('SSC Marks', compute='_get_marks', store=True)
    inter_marks = fields.Integer('Inter Marks', compute='_get_marks', store=True)
    ug_cgpa = fields.Float(string="UG CGPA", compute='_get_marks', store=True)
    inter_total_marks = fields.Integer('Inter Total Marks', compute='_get_marks', store=True)
    repeat_times = fields.Integer('Repeat/Improvement Times', states=READONLY_STATES)

    is_additional = fields.Boolean('Is Additional Subject', states=READONLY_STATES)
    is_hafiz = fields.Boolean('Is Hafiz-e-Quran?', states=READONLY_STATES)

    entryID = fields.Char('Entry ID', states=READONLY_STATES, compute='_get_entry', store=True)
    entry_score = fields.Integer('Entry Score', states=READONLY_STATES)
    user_id = fields.Many2one('res.users', 'Login User')

    improvement_deduction = fields.Integer('Improvement', compute='_get_adjustments', store=True)
    additional_deduction = fields.Integer('Additional Subject', compute='_get_adjustments', store=True)
    hafiz_marks = fields.Integer('Hafiz-e-Quran', compute='_get_adjustments', store=True)
    adjusted_score = fields.Integer('Adjusted Score', compute='_get_adjustments', store=True)

    ssc_percentage = fields.Float('SSC Percentage', compute='_get_marks', digits=(8, 3), store=True)
    inter_percentage = fields.Float('Intermediate Percentage', compute='_get_adjustments', digits=(8, 3), store=True)
    ug_cgpa_percentage = fields.Float('UG Percentage', compute='_get_marks', digits=(8, 3), store=True)
    entry_percentage = fields.Float('Entry', compute='_get_merit_score', digits=(8, 3), store=True)

    merit_score = fields.Float('Merit Score', compute='_get_merit_score', digits=(8, 3), store=True)
    merit_number = fields.Integer('Merit Number')
    manual_score = fields.Float()

    # branch_code = fields.Text('Branch Code')
    # voucher_no = fields.Text('Voucher Number')
    # submission_date = fields.Date(string="Submission Date")
    # amount = fields.Integer('Voucher Amount')

    program_id = fields.Many2one('odoocms.program', 'Offered Program')
    preference = fields.Integer('Preference')
    student_id = fields.Many2one('odoocms.student', 'Student')
    quota_id = fields.Many2one('odoocms.admission.quota', 'Rural Quota', states=READONLY_STATES)
    quota_id2 = fields.Many2one('odoocms.admission.quota', 'Forces Quota', states=READONLY_STATES)
    dae_quota_id = fields.Many2one('odoocms.admission.quota', 'DAE Quota', states=READONLY_STATES)
    admission_quota_id = fields.Many2one('odoocms.admission.quota', 'Admission Quota')
    center_id = fields.Many2one('odoocms.admission.test.center', 'Test Center')
    slot_id = fields.Many2one('odoocms.admission.test.time', 'Time')
    batch_entry_test_id = fields.Many2one('batch.entry.test', 'Batch Entry Test ID')
    batch_interview_id = fields.Many2one('batch.interview', 'Batch Interview ID')
    batch_offered_program_id = fields.Many2one('batch.offered.program', 'Batch Offered Program ID')

    locked = fields.Boolean('Locked', default=False)
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm'), ('submit', 'Submit'), ('verified', 'Verified'),
         ('verification', 'Sent for Verification'),
         ('approve', 'Approve'), ('entry_test', 'Entry Test'), ('interview', 'Interview'),
         ('offered_program', 'Offered Program'), ('open', 'Open'),
         ('reject', 'Reject'), ('done', 'Done'), ], string='Status',
        default='draft', tracking=True)

    reject_reason_des = fields.Text('Reject Reason Description')
    inter_result_status = fields.Char('Result Status', default="Complete")
    merit_ids = fields.One2many('odoocms.application.merit', 'application_id', 'Merit Lists')

    scolarship_ids = fields.One2many('student.scolarship', 'application_id')

    def name_get(self):
        # return [(rec.id, (rec.name or '') + '-' + (rec.last_name or '')) for rec in self]

        return [(rec.id, (rec.name or '')) for rec in self]

    _sql_constraints = [
        ('cnic', 'unique(cnic)', "Another Application is already exists with this CNIC!")]

    @api.depends('cnic')
    def _get_entry(self):
        if self.cnic:
            self.entryID = self.cnic

    @api.model
    def create(self, vals):
        application = self.env['odoocms.application'].sudo().search([('cnic', '=', vals['cnic'])])
        if application:
            raise ValidationError(_("Application with same cnic already exist"))
        else:
            if vals.get('application_no', _('New')) == _('New'):
                register_id = self.env['odoocms.admission.register'].browse(vals['register_id'])
                if register_id.session_type == "fall":
                    vals['application_no'] = self.env['ir.sequence'].next_by_code('odoocms.application.fall') or _('New')
                elif register_id.session_type == "spring":
                    vals['application_no'] = self.env['ir.sequence'].next_by_code('odoocms.application.spring') or _('New')
                elif register_id.session_type == "summer":
                    vals['application_no'] = self.env['ir.sequence'].next_by_code('odoocms.application.summer') or _('New')
            res = super(OdooCMSAdmissionApplication, self).create(vals)
            if res:
                self.env.ref("odoocms_admission.application_submit_email_template").send_mail(self.id)
            return res

    def unlink(self):
        for rec in self:
            if rec.state != 'reject':
                raise ValidationError(_("Application can only be deleted after Rejecting it"))
            return super(OdooCMSAdmissionApplication, self).unlink()

    @api.depends('inter_marks', 'repeat_times', 'is_additional', 'is_hafiz')
    def _get_adjustments(self):
        for rec in self:
            rec.improvement_deduction = -1 * min(rec.repeat_times * 10,
                                                 20) if rec.repeat_times and rec.repeat_times > 0 else 0
            rec.additional_deduction = -10 if rec.is_additional else 0
            rec.hafiz_marks = 20 if rec.is_hafiz else 0
            rec.adjusted_score = rec.inter_marks + rec.improvement_deduction + rec.additional_deduction + rec.hafiz_marks
            rec.inter_percentage = (100.00 * rec.adjusted_score) / (rec.inter_total_marks or 1100) * 1

    @api.depends('ssc_marks', 'adjusted_score', 'entry_score')
    def _get_merit_score(self):
        for rec in self:
            rec.entry_percentage = 100.0 * rec.entry_score / 800 * 5
            rec.merit_score = rec.ssc_percentage + rec.inter_percentage + rec.entry_percentage

    @api.depends('academic_ids', 'academic_ids.obtained_marks', 'academic_ids.total_marks', 'academic_ids.degree_level')
    def _get_marks(self):
        for rec in self:
            for academic in rec.academic_ids:
                if academic.degree_level and academic.total_marks and academic.obtained_marks:
                    # if academic.degree_level == 'matric':
                    if academic.degree_level == 'Matric':  # SARFRAZ
                        academic.application_id.ssc_marks = academic.obtained_marks
                        academic.application_id.ssc_percentage = academic.percentage

                    if academic.degree_level == 'O-Level':  # SARFRAZ
                        academic.application_id.ssc_marks = academic.o_level_obtained
                        academic.application_id.ssc_percentage = academic.o_level_percentage

                    if academic.degree_level == 'A-Level':  # SARFRAZ
                        academic.application_id.inter_marks = academic.a_level_obtained

                    # if academic.degree_level == 'inter':
                    if academic.degree_level == 'Intermediate':  # SARFRAZ
                        academic.application_id.inter_marks = academic.obtained_marks
                        academic.application_id.inter_total_marks = academic.total_marks
                # if academic.degree_level == 'DAE': #SARFRAZ
                # 	academic.application_id.inter_marks = academic.obtained_marks
                # 	academic.application_id.inter_total_marks = academic.total_marks
                # if academic.degree_level != 'Matric': #Numan
                # 	rec.inter_marks = academic.obtained_marks
                # 	rec.inter_total_marks = academic.total_marks

    def send_to_verify(self):
        for rec in self:
            # document_ids = self.env['odoocms.documents'].search([('application_ref', '=', rec.id)])
            # if not document_ids:
            #	raise ValidationError(_('No Documents provided'))
            rec.write({'state': 'verification'})

    def entry_test(self):
        for rec in self:
            # if rec.student_application_ids:
            ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
            rec.ensure_one()
            template_id = rec.env['ir.model.data'].xmlid_to_res_id(
                'odoocms_admission.mail_template_batch_entry_test_ind', raise_if_not_found=False)
            rec.ensure_one()
            ctx = {
                'default_model': 'odoocms.application',
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'force_email': True,
                'email_to': self.email,
                'res_id': self.id,
                'res_model': self._name,
                'state': self.state,
            }
            return {
                'name': _('Compose Email'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(False, 'form')],
                'view_id': False,
                'target': 'new',
                'context': ctx,
            }

    def interview_btn(self):
        for rec in self:
            ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
            rec.ensure_one()
            template_id = rec.env['ir.model.data'].xmlid_to_res_id(
                'odoocms_admission.mail_template_batch_interview_ind', raise_if_not_found=False)

            rec.ensure_one()
            ctx = {
                'default_model': 'odoocms.application',
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'force_email': True,
                'email_to': self.email,
                'res_id': rec.id,
                'res_model': self._name,
                'state': self.state,
            }
            return {
                'name': _('Compose Email'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(False, 'form')],
                'view_id': False,
                'target': 'new',
                'context': ctx,
            }

    def offered_program_btn(self):
        for rec in self:
            ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
            rec.ensure_one()
            template_id = rec.env['ir.model.data'].xmlid_to_res_id(
                'odoocms_admission.mail_template_offered_program_ind', raise_if_not_found=False)

            rec.ensure_one()
            ctx = {
                'default_model': 'odoocms.application',
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'force_email': True,
                'email_to': self.email,
                'res_id': rec.id,
                'res_model': self._name,
                'state': self.state,
            }
            return {
                'name': _('Compose Email'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(False, 'form')],
                'view_id': False,
                'target': 'new',
                'context': ctx,
            }


    def reject_application(self):
        for rec in self:
            try:
                template_id = \
                    rec.env['ir.model.data'].get_object_reference('odoocms_admission', 'custom_mail_template_reject')[1]

            except ValueError:
                template_id = False

            ctx = {
                'default_model': 'odoocms.application',
                'default_res_id': self.ids[0],
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
            }
            return {
                'name': _('Compose Email'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(False, 'form')],
                'view_id': False,
                'target': 'new',
                'context': ctx,
            }

    # @api.multi
    # @api.constrains('birth_date')
    # def _check_birthdate(self):
    #    for record in self:
    #        if record.birth_date > fields.Date.today():
    #            raise ValidationError(_(
    #                "Birth Date can't be greater than current date!"))

    # @api.multi
    # @api.constrains('register_id', 'application_date')
    # def _check_admission_register(self):
    #    for rec in self:
    #        start_date = fields.Date.from_string(rec.register_id.start_date)
    #        end_date = fields.Date.from_string(rec.register_id.end_date)
    #        application_date = fields.Date.from_string(rec.application_date)
    #        if start_date > application_date  or application_date > end_date:
    #            raise ValidationError(_(
    #                "Application Date should be between Start Date & \
    #                End Date of Admission Register."))

    def application_verify(self):
        for rec in self:
            document_ids = self.env['odoocms.documents'].search([('application_ref', '=', rec.id)])
            if document_ids:
                doc_status = document_ids.mapped('state')
                if all(state in ('done', 'returned') for state in doc_status):
                    rec.write({
                        'verified_by': self.env.uid,
                        'state': 'approve'
                    })
                else:
                    raise ValidationError(_('All Documents are not Verified Yet, '
                                            'Please complete the verification'))

            # else:
            #	raise ValidationError(_('No Documents provided'))
            rec.write({'state': 'approve'})

    # def application_reject(self):

    def _document_count(self):
        for rec in self:
            document_ids = self.env['odoocms.documents'].search([('application_ref', '=', rec.id)])
            rec.document_count = len(document_ids)

    def _get_fee_amount(self):
        print("I am first fee")
        fee_structure = self.env['odoocms.fee.structure'].search(
            [('session_id', '=', self.academic_session_id.id)])
        payment_types = ['admissiontime', 'persemester', 'peryear']

        receipts = self.env['odoocms.receipt.type'].browse([1, 4, 6])
        fee_head_ids = receipts.mapped('fee_head_ids').ids
        fee_lines = fee_structure.head_ids.filtered(
            lambda l: l.fee_head_id.id in fee_head_ids
                      and l.payment_type in payment_types
            # and (not l.program_ids or self.program_id.id in l.program_ids.ids)
            # and (not l.semester_ids or 1 in l.semester_ids.ids)
        )

        total = 0.0
        for line in fee_lines.line_ids:
            if not line.domain or self.env['odoocms.student'].search(safe_eval(line.domain) + [('id', '=', self.id)]):
                total += float(line.amount_text)

        paid = 0.0
        prev_lists = self.env['odoocms.application.merit'].search([('application_id', '=', self.id)])
        for lst in prev_lists:
            paid += lst.amount
        return total - paid

    def document_view(self):
        self.ensure_one()
        domain = [
            ('application_id', '=', self.id)]
        return {
            'name': _('Documents'),
            'domain': domain,
            'res_model': 'odoocms.application.documents',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
				Click to Create for New Documents
				</p>'''),
            'limit': 80,
            'context': "{'default_application_id': %s}" % self.id
        }

    def create_student(self, view=False):
        if not self.date_of_birth:
            raise UserError('Data of Birth of %s - %s not Set.' % (self.entryID, self.name))

        semester = self.env['odoocms.semester'].search([('number', '=', 1)], limit=1)
        user = self.env['res.users'].search([('login', '=', self.entryID)])

        values = {
            'state': 'enroll',
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
            'user_id': self.user_id.id,

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
            'career_id': self.career_id.id,
            'program_id': self.program_id.id,
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

        if self.program_id:
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

    def create_application_user(self):
        group_portal = self.env.ref('base.group_portal')
        print(1111111111, group_portal)
        users_res = self.env['res.users']
        for record in self:
            if not record.user_id:
                data = {
                    'name': record.first_name + ' ' + (record.last_name or ''),
                    # 'name': record.name or '',
                    # 'partner_id': record.partner_id.id,
                    'login': record.entryID or record.email,
                    'password': record.mobile or record.entryID or '123456',
                    'groups_id': group_portal,
                }
                user_id = users_res.create(data)
                record.user_id = user_id.id

    def is_zero(self, amount):
        return tools.float_is_zero(amount, precision_rounding=2)

    def amount_to_text(self, amount):
        self.ensure_one()

        def _num2words(number, lang):
            try:
                return num2words(number, lang=lang).title()
            except NotImplementedError:
                return num2words(number, lang='en').title()

        if num2words is None:
            logging.getLogger(__name__).warning("The library 'num2words' is missing, cannot render textual amounts.")
            return ""

        formatted = "%.{0}f".format(2) % amount
        parts = formatted.partition('.')
        integer_value = int(parts[0])
        fractional_value = int(parts[2] or 0)

        lang_code = self.env.context.get('lang') or self.env.user.lang
        lang = self.env['res.lang'].search([('code', '=', lang_code)])
        amount_words = tools.ustr('{amt_value} {amt_word}').format(
            amt_value=_num2words(integer_value, lang=lang.iso_code),
            amt_word='.',
        )
        if not self.is_zero(amount - integer_value):
            amount_words += ' ' + 'and' + tools.ustr(' {amt_value} {amt_word}').format(
                amt_value=_num2words(fractional_value, lang=lang.iso_code),
                amt_word='.',
            )
        return amount_words


# class MailComposeMessageBET(models.TransientModel):
#     _inherit = 'mail.compose.message'
#
#     def action_send_mail(self):
#         odoocms_application = self.env['odoocms.application'].browse(self.res_id)
#         odoocms_application.write({'state': 'reject'})
#         return super(MailComposeMessageBET, self).action_send_mail()


class OdooCMSApplicationRejectReason(models.Model):
    _name = 'odoocms.application.reject.reason'
    _description = 'Reject Reasons'

    name = fields.Char(string="Reason", required=True,
                       help="Possible Reason for rejecting the Applications")
    code = fields.Char(string='Code')


class OdoocmsMeritList(models.Model):
    _name = 'odoocms.merit.list'
    _description = 'Merit List'
    _order = 'number'

    name = fields.Char('List Name')
    code = fields.Char('Code')
    number = fields.Integer('Number')


class OdoocmsMeritRegister(models.Model):
    _name = 'odoocms.merit.register'
    _description = 'Merit Register'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'register_id desc, merit_list_number desc'

    register_id = fields.Many2one('odoocms.admission.register', 'Application Register')
    name = fields.Char('List Name')
    date_list = fields.Date('Merit List Date')
    date_end = fields.Date('Closing Date', tracking=True)
    merit_list_id = fields.Many2one('odoocms.merit.list', 'Merit List')
    merit_list_number = fields.Integer('List Number', related='merit_list_id.number', store=True)
    remarks = fields.Text('Remarks')

    next_merit_register_id = fields.Many2one('odoocms.merit.register', 'Next Merit Register')
    prev_merit_register_id = fields.Many2one('odoocms.merit.register', 'Prev Merit Register')
    merit_application_ids = fields.One2many('odoocms.application.merit', 'merit_register_id', string='Merit Detail')


class OdoocmsApplicationMerit(models.Model):
    _name = 'odoocms.application.merit'
    _description = 'Application Merit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'application_id'
    _order = 'merit_register_id, merit_number, merit_list_number desc'

    merit_register_id = fields.Many2one('odoocms.merit.register', 'Merit Register', ondelete='cascade')
    merit_list_number = fields.Integer('List Number', related='merit_register_id.merit_list_id.number', store=True)
    register_id = fields.Many2one('odoocms.admission.register', 'Admission Register',
                                  related='merit_register_id.register_id', store=True)
    application_id = fields.Many2one('odoocms.application', string='Applicant')
    rural_quota_id = fields.Many2one('odoocms.admission.quota', 'Application Rural Quota',
                                     related='application_id.quota_id', store=True)
    forces_quota_id = fields.Many2one('odoocms.admission.quota', 'Application Forces Quota',
                                      related='application_id.quota_id2', store=True)
    dae_quota_id = fields.Many2one('odoocms.admission.quota', 'Application DAE Quota',
                                   related='application_id.dae_quota_id', store=True)
    entryID = fields.Char('Entry ID', related='application_id.entryID', store=True)
    program_id = fields.Many2one('odoocms.program', string='Program')
    preference = fields.Integer('Preference')
    merit_number = fields.Integer('Merit No.')
    program_merit_number = fields.Integer('Program Merit No.')
    quota_number = fields.Integer('Quota Merit No.')
    admission_on_quota = fields.Boolean('Admission on Quota', default=False)
    quota_id = fields.Many2one('odoocms.admission.quota', 'Admissioin Quota')
    date_interview = fields.Datetime('Interview Date & Time')
    amount = fields.Float('Fee Amount')
    locked = fields.Boolean('Locked', default=False)
    comments = fields.Text('Comments', readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Draft'), ('done', 'Done'), ('cancel', 'Cancel'), ('reject', 'Rejected'), ('absent', 'Absent')
    ], 'Status', default='draft')
    line_ids = fields.One2many('odoocms.application.merit.line', 'application_merit_id', 'Preferences')

    next_merit_app_id = fields.Many2one('odoocms.application.merit', 'Next Merit')
    prev_merit_app_id = fields.Many2one('odoocms.application.merit', 'Prev Merit')

    _sql_constraints = [
        ('application_merit', 'unique(application_id,merit_register_id)',
         "Another Merit already exists with this Application and Merit List!"), ]


class OdoocmsApplicationMeritLine(models.Model):
    _name = 'odoocms.application.merit.line'
    _description = 'Application Merit Line'

    application_merit_id = fields.Many2one('odoocms.application.merit', 'Merit Application', ondelete='cascade')
    merit_register_id = fields.Many2one('odoocms.merit.register', 'Merit Register',
                                        related='application_merit_id.merit_register_id')
    application_id = fields.Many2one('odoocms.application', string='Applicant',
                                     related='application_merit_id.application_id')
    program_id = fields.Many2one('odoocms.program', string='Program')
    preference = fields.Integer('Preference')
    program_merit_number = fields.Integer('Program Merit No.')
    quota_number = fields.Integer('Rural Merit No.')
    quota_number2 = fields.Integer('Forces Merit No.')
    dae_quota_number = fields.Integer('DAE Merit No.')
    quota_id = fields.Many2one('odoocms.admission.quota', 'Rural Areas Quota')
    quota_id2 = fields.Many2one('odoocms.admission.quota', 'Forces Quota')
    dae_quota_id = fields.Many2one('odoocms.admission.quota', 'DAE Quota')
    seats = fields.Integer('Seats')
    quota_seats = fields.Integer('Rural Seats')
    quota_seats2 = fields.Integer('Forces Seats')
    dae_seats = fields.Integer('DAE Seats')
    selected = fields.Boolean('Selected')
    admission_on_quota = fields.Boolean('Admission on Quota', default=False)


class OdoocmsApplicationPreference(models.Model):
    _name = 'odoocms.application.preference'
    _description = 'Application Preference'
    _order = 'application_id desc, preference'
    _rec_name = 'application_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    application_id = fields.Many2one('odoocms.application', string='Applicant', tracking=True, ondelete='cascade')
    cnic = fields.Char(related='application_id.cnic', string='CNIC', store=True)
    program_id = fields.Many2one('odoocms.program', string='Program', tracking=True)
    preference = fields.Integer(string='Preference', tracking=True)
    discipline_preference = fields.Integer(string='Discipline Preference', tracking=True, default=1)
    discipline_id = fields.Many2one(string='Discipline ID', related='program_id.discipline_id', store=True)
    discipline_name = fields.Char(related='discipline_id.name', store=True)
    # discipline_name = fields.Char( 'Discipline', compute='_discipline_name', store=True)
    type = fields.Selection([('Armed Forces', 'Armed Forces'), ('Regular', 'Regular')], 'Type', default='Regular',
                            tracking=True)
    sequence = fields.Integer()

    # @api.depends('preference')
    # def _discipline_name(self):
    # 	for each in self:
    # 		each.discipline_name = each.program_id.discipline_id.name

    _sql_constraints = [
        ('application_program', 'unique(application_id,program_id,preference,type)',
         "Another Preference already exists with this Application and Program!"), ]


class OdooCMSAdmissionApplicationAcademic(models.Model):
    _name = 'odoocms.application.academic'
    _description = 'Applications Academics'
    _rec_name = 'application_id'

    application_id = fields.Many2one('odoocms.application', 'Applicant', ondelete='cascade')
    sc_application_id = fields.Many2one('odoocms.sc.application', 'SC Applicant', ondelete='cascade')
    degree_level = fields.Selection(
        [('Matric', 'Matric'), ('Intermediate', 'Intermediate'), ('O-Level', 'O-Levels'), ('A-Level', 'A-Levels'),
         ('DAE', 'DAE'), ('UG', 'Under-Graduate')], 'Degree Level', required=1)

    degree = fields.Char('Degree')
    roll_number = fields.Char('Roll Number')
    result_awaiting = fields.Boolean('Result Awaiting', default=False)
    year = fields.Char('Passing Year')
    board = fields.Char('Board Name')
    subjects = fields.Char('Subjects/Specialization')
    total_marks = fields.Float('Total Marks')
    obtained_marks = fields.Float('Obtained Marks')
    percentage = fields.Float('Percentage')

    @api.onchange("total_marks", 'obtained_marks')
    def _compute_pecentage(self):
        for rec in self:
            if rec.total_marks and rec.obtained_marks:
                rec.percentage = (rec.obtained_marks / rec.total_marks) * 100

    physics_total_marks = fields.Integer('Physics Total Marks')
    math_total_marks = fields.Integer('Maths Total Marks')
    add_math_total_marks = fields.Integer('Add Maths/Bio Total Marks')
    chemistry_total_marks = fields.Integer('Chemistry Total Marks')
    computer_total_marks = fields.Integer('Computer Total Marks')

    is_additional_maths = fields.Char('Is Additional Maths', default='No')
    physics_marks = fields.Integer('Physics Obtained Marks')
    math_marks = fields.Integer('Maths Obtained Marks')
    add_math_marks = fields.Integer('Add Maths/Bio Obtained Marks')
    chemistry_marks = fields.Integer('Chemistry Obtained Marks')
    computer_marks = fields.Integer('Computer Obtained Marks')

    physics_marks_per = fields.Float('Physics Marks Percentage')
    math_marks_per = fields.Float('Maths Marks Percentage')
    add_math_marks_per = fields.Float('Add Maths/Bio Marks Percentage')
    chemistry_marks_per = fields.Float('Chemistry Marks Percentage')
    computer_marks_per = fields.Float('Computer Marks Percentage')

    dae_first_year_roll_number = fields.Integer('1st Year Roll Number')
    dae_first_year_total = fields.Integer('1st Year Total Marks')
    dae_first_year_obtained = fields.Integer('1st Year Obtained Marks')
    dae_first_year_percentage = fields.Float('1st Year Percentage')
    dae_sec_year_roll_number = fields.Integer('2nd Year Roll Number')
    dae_sec_year_total = fields.Integer('2nd Year Total Marks')
    dae_sec_year_obtained = fields.Integer('2nd Year Obtained Marks')
    dae_sec_year_percentage = fields.Float('2nd Year Percentage')
    dae_third_year_roll_number = fields.Integer('3rd Year Roll Number')
    dae_third_year_total = fields.Integer('3rd Year Total Marks')
    dae_third_year_obtained = fields.Integer('3rd Year Obtained Marks')
    dae_third_year_percentage = fields.Float('3rd Year Percentage')
    dae_totalmarks = fields.Integer('DAE Total Marks')
    dae_obtainedmarks = fields.Integer('DAE Obtained Marks')
    dae_percentage = fields.Float('DAE Percentage')
    dae_specialization = fields.Char('DAE Specialization')

    ug_university_name = fields.Char(string="University Name")
    ug_cgpa = fields.Float(string="CGPA")

    # Sarfraz Addition
    document_status = fields.Selection(
        [('Yes', 'Verified'), ('No', 'UnVerified'), ('Rejected', 'Rejected'), ('Pending', 'Pending')],
        string='Verified?', default="No")

    application_state = fields.Selection(string='Applicantion Status', related='application_id.state', store=True)

    def action_document_verified(self):
        application_id = self.env['odoocms.application']
        for rec in self:
            rec.document_status = 'Yes'
            print(11111111111111111111111111111111111111111)
            msg = "The Document (" + rec.degree_level + ") has been verified by the user " + self.env.user.login + " on " + str(
                fields.Datetime.now())
            rec.application_id.message_post(body=msg)
            application_id = rec.application_id
        count = 0
        for rec in application_id.academic_ids:
            if rec.document_status == 'Yes':
                count += 1
        if count >= 2:
            application_id.state = 'verified'

    def action_document_unverified(self):
        for rec in self:
            rec.document_status = 'No'
            print(2222222222222222222222222222222222222222222)
            msg = "The Document (" + rec.degree_level + ") has been Unverified by the user " + self.env.user.login + " on " + str(
                fields.Datetime.now())
            rec.application_id.message_post(body=msg)
            rec.application_id.state = 'confirm'

    def action_document_rejected(self):
        for rec in self:
            rec.document_status = 'Rejected'
            print(3333333333333333333333333333333333333333333)
            msg = "The Document (" + rec.degree_level + ") has been Rejected by the user " + self.env.user.login + " on " + str(
                fields.Datetime.now())
            rec.application_id.message_post(body=msg)
            rec.application_id.state = 'reject'


class OdooCMSAdmissionApplicationDocuments(models.Model):
    _name = 'odoocms.application.documents'
    _description = 'Applications Documents'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'student_id'

    student_id = fields.Many2one('odoocms.student', string='Student')
    application_id = fields.Many2one('odoocms.application', string='Applicant', ondelete='cascade')

    matric_scaned_copy = fields.Binary('Scanned Copy of Matric', attachment=True)
    matric_scaned_copy_name = fields.Text('Scanned Copy of Matric Name')
    matric_scaned_copy_size = fields.Text('Scanned Copy of Matric Size')

    inter_scaned_copy = fields.Binary('Scanned Copy of Inter', attachment=True)
    inter_scaned_copy_name = fields.Text('Scanned Copy Inter Name')
    inter_scaned_copy_size = fields.Text('Scanned Copy Inter Size')

    domicile_scaned_copy = fields.Binary('Scanned Copy of Domicile', attachment=True)
    domicile_scaned_copy_name = fields.Text('Scanned Copy Domicile Name')
    domicile_scaned_copy_size = fields.Text('Scanned Copy Domicile Size')

    salary_slip_scaned_copy = fields.Binary('Scanned Copy of Salary Slip', attachment=True)
    salary_slip_scaned_copy_name = fields.Text('Scanned Copy Salary Slip Name')
    salary_slip_scaned_copy_size = fields.Text('Scanned Copy Salary Slip Size')

    prc_scaned_copy = fields.Binary('Scanned Copy of PRC', attachment=True)
    prc_scaned_copy_name = fields.Text('Scanned Copy PRC Name')
    prc_scaned_copy_size = fields.Text('Scanned Copy PRC Size')

    test_certificate = fields.Binary('Scanned Copy of Test', attachment=True)
    test_certificate_name = fields.Text('Scanned Copy Test Name')
    test_certificate_size = fields.Text('Scanned Copy Test Size')

    cnic_scanned_copy = fields.Binary('Scanned Copy of CNIC', attachment=True)
    cnic_scanned_copy_name = fields.Text('Scanned Copy CNIC Name')
    cnic_scanned_copy_size = fields.Text('Scanned Copy CNIC Size')

    hafiz_scaned_copy = fields.Binary('Scanned Copy of Hafiz-e-Quran', attachment=True)
    hafiz_scaned_copy_name = fields.Text('Scanned Copy Hafiz-e-Quran Name')
    hafiz_scaned_copy_size = fields.Text('Scanned Copy Hafiz-e-Quran Size')

    challan_copy = fields.Binary('Scanned Copy of Challan', attachment=True)
    challan_name = fields.Text('Scanned Copy Challan Name')
    challan_size = fields.Text('Scanned Copy Challan Size')


class OdoocmsAdmissionConfirmFee(models.Model):
    _name = 'odoocms.admission.confirm.fee'
    _description = 'Admission confirm Fee'

    entryID = fields.Char('Entry ID', readonly=True, states={'draft': [('readonly', False)]})
    application_id = fields.Many2one('odoocms.application', string='Applicant', compute='_get_application', store=True)
    merit_id = fields.Many2one('odoocms.application.merit', 'Merit')
    date_paid = fields.Date('Date', readonly=True, states={'draft': [('readonly', False)]})
    amount = fields.Float('Amount', readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], 'Status', default='draft', readonly=True,
                             states={'draft': [('readonly', False)]})

    @api.depends('entryID')
    def _get_application(self):
        for rec in self:
            if rec.entryID:
                application = self.env['odoocms.application'].search([('entryID', '=', rec.entryID)])
                if application:
                    rec.application_id = application.id

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Admission Confirm Fee'),
            'template': '/odoocms_admission/static/xls/odoocms_admission_confirm_fee.xls'
        }]


class OdooCMSAdmissionHafizQuranResult(models.Model):
    _name = 'odoocms.application.hafiz.quran.result'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hafiz Quran Result'

    name = fields.Char('Name', required=1)
    total_marks = fields.Integer('Total Marks', required=1)
    obtained_marks = fields.Integer('Obtained Marks', required=1)
    application_id = fields.Many2one('odoocms.application', 'Applicant')
    date = fields.Datetime('Date')


class OdoocmsApplicationCondidateVer(models.Model):
    _name = 'odoocms.condidate.verification'
    _description = 'Application Candidate Verification'

    name = fields.Char(string='Name')
    cnic = fields.Char('CNIC', required=True)
    mobile = fields.Char(string='Mobile', required=True)
    is_verified = fields.Boolean('Is Verified')


class OdoocmsApplicationBoard(models.Model):
    _name = 'odoocms.application.board'
    _description = 'Education Board'

    name = fields.Char(string='Name', required=True)
    sh_name = fields.Char(string='Short Name')
    code = fields.Char('Code')
    city_id = fields.Many2one('odoocms.city', 'City')


class OdoocmsApplicationPassingYear(models.Model):
    _name = 'odoocms.application.passing.year'
    _description = 'Application Passing Year'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='code')
    matric = fields.Boolean('Matric', default=True)
    inter = fields.Boolean('Intermediate', default=True)
    ug = fields.Boolean('Under Graduate', default=True)


class ScolarshipRequest(models.Model):
    _name = 'student.scolarship'

    scolarship_id = fields.Many2one('odoocms.fee.waiver.type', string='Scolarship', required=True)
    status = fields.Selection([
        ('approved', 'Approved'),
        ('not_approved', 'Not Approved')
    ], string='Status', default='not_approved')
    application_id = fields.Many2one('odoocms.application')