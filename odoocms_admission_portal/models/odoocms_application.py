import re

from odoo import fields, models, _, api
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.tools.safe_eval import safe_eval
import pdb
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from odoo.http import content_disposition, Controller, request, route
import random


class OdooCMSAdmissionApplication(models.Model):
    _inherit = 'odoocms.application'

    @api.depends('street', 'street2', 'city')
    def _get_postal_address(self):
        for applicant in self:
            name = applicant.street or ''
            if applicant.street2:
                name = name + ' ' + applicant.street2
            if applicant.city:
                name = name + ', ' + applicant.city
            applicant.postal_address = name

    # domicile_id = fields.Many2one('odoocms.domicile', string='Domicile ID')
    passport = fields.Char(string='Passport')
    Landline = fields.Char(string='Landline No')

    is_forces_quota = fields.Boolean(string='Any Force Quota?', default=False)
    forces_quota = fields.Char(string='Forces Quota')
    is_rural_quota = fields.Boolean(string='Any Rural Quota?', default=False)
    rural_quota = fields.Char(string='Rural Quota')

    is_dual_nationality = fields.Boolean(string='Dual Nationality', default=False)
    province_id = fields.Many2one('odoocms.province', string='Province')
    province2 = fields.Char(string='Other Province')

    per_province = fields.Char(string='Province')
    per_province2 = fields.Char(string='Other Province')

    present_country_id = fields.Many2one('res.country', string='Present Country')
    present_province = fields.Char(string='Province')
    present_province2 = fields.Char(string='Other Province')

    guardian_name = fields.Char('Guardian Name')
    guardian_cnic = fields.Char('CNIC')
    guardian_occupation = fields.Char(string='Occupation')
    father_income = fields.Char(string='Father Income')
    guardian_relation = fields.Char('Relation')
    guardian_mobile = fields.Char(string='Mobile')
    guardian_landline = fields.Char(string='Landline')
    guardian_address = fields.Char(string='Residential Address')

    voucher_image = fields.Binary(string='Fee Voucher', attachment=True)
    voucher_number = fields.Char(string='Voucher Number')
    voucher_date = fields.Date(string='Date')
    voucher_amount = fields.Char(string='Amount')

    fee_voucher_state = fields.Selection([
        ('no', 'Not Downloaded Yet'),
        ('download', 'Not Uploaded Yet'),
        ('upload0', 'Fee Submitted'),
        ('upload', 'Not Verified Yet'),
        ('verify', 'Verified'),
        ('unverify', 'Un-Verified')
    ], default='no')

    # SARFRAZ Changes
    # Should be managed by the portal when student download Fee voucher
    application_download_date = fields.Date('Application Download Date', )
    fee_voucher_download_date = fields.Date('Fee Voucher Download Date',
                                            help="This field is defined for the Fee Voucher Downloaded Dashboard. Required in the Tree View")
    # Should be managed by the portal when student Upload Fee voucher
    fee_voucher_upload_date = fields.Date('Fee Voucher Upload Date',
                                          help="This field is defined for the Fee Voucher Upload Dashboard. Required in the Tree View")
    # Should be managed by the portal when Fee voucher is verified
    fee_voucher_verified_date = fields.Date('Fee Voucher Verified Date',
                                            help="This field is defined for the Fee Voucher Verified Dashboard. Required in the Tree View")
    # No of Days Passed After Verification, it will be calculated
    no_of_days_after_verification = fields.Integer('No of Days Passed after Verification')

    test_roll_no = fields.Char(string='Test Roll Number')
    test_type = fields.Char(string='Test Type', default='UET')
    test_total_marks = fields.Integer(string='Total Marks')
    test_obtained_marks = fields.Integer(string='Obtained Marks')
    test_percentage = fields.Float(string='Percentage')
    interview_percentage = fields.Float(string='Percentage')
    test_date = fields.Date(string='Date')

    finance_ass = fields.Boolean('Financial Assistance Required?', default=False)
    finance_ass_duration = fields.Selection([
        ('one', 'One Year'), ('two', 'Two Years'), ('three', 'Three Years'), ('four', 'Four Years')],
        'Assistance Duration')
    finance_ass_amount = fields.Integer('Assistance Amount1')
    finance_ass_amt = fields.Selection([
        ('one', '100000-200000'), ('two', '200000-400000'), ('four', '400000-600000'), ('full', 'Full Tution Fee')],
        'Assistance Amount')
    postal_address = fields.Char('Postal Address', compute='_get_postal_address', store=True)

    is_any_disability = fields.Boolean(string='Any Disability?', default=False)
    disability = fields.Char(string='Disability')

    is_any_disease = fields.Boolean(string='Is Any Disease?', default=False)
    disease = fields.Char(string='Disease')

    get_info_from = fields.Selection(
        [('University Website', 'University Website'), ('Newspapers', 'Newspapers'), ('Social Media', 'Social Media'),
         ('NEC Awareness Sessions', 'NEC Awareness Sessions'),
         ('Leaflet at NTS Test Centres', 'Leaflet at NTS Test Centres'),
         ('Own College / Institutions', 'Own College / Institutions'), ('Panaflex / billboard', 'Panaflex / billboard'),
         ('Friends / relatives', 'Friends / relatives'), ('TV', 'TV'),
         ('Radio', 'Radio')],
        string='How you came to know about US?', default='University Website')

    step_number = fields.Integer(string='Step Number', default=0)

    # For Entry Test Verification
    cbt_password = fields.Char(String='CBT Password')
    entry_test_status = fields.Selection([('Yes', 'Pass'), ('No', 'No'), ('Rejected', 'Fail')], string='Verified?',
                                         default="No")

    # New Flow of Entry Test
    entry_test_of_marks = fields.Integer('Total Marks')
    entry_test_obtained_marks = fields.Integer('Obtained Marks')
    ET_percentage = fields.Integer('ET Percentage %', compute="_get_ET_Percentage", store=True)
    entry_test_status1 = fields.Selection([('No', 'No'), ('Yes', 'Pass'), ('Rejected', 'Fail')], string='Status',
                                         default="No")
    interview_total_marks = fields.Integer('Total Marks')
    marks_obtained = fields.Integer('Marks Obtained')
    IM_percentage = fields.Integer('IM Percentage %', compute="_get_IM_percentage", store=True)
    entry_test_status2 = fields.Selection([('No', 'No'), ('Yes', 'Pass'), ('Rejected', 'Fail')], string='Status',
                                         default="No")

    # Inter_percentage
    inter_percentage = fields.Float('Intermediate Percentage', compute='_get_marks', digits=(8, 3), store=True)
    physics_percentage = fields.Float('Physics Percentage', compute='_get_marks', digits=(8, 3), store=True)
    chemistry_percentage = fields.Float('Chemistry/Computer Percentage', compute='_get_marks', digits=(8, 3),
                                        store=True)
    math_percentage = fields.Float('Maths/Add Maths', compute='_get_marks', digits=(8, 3), store=True)
    physics_marks = fields.Integer('Physics Marks', compute='_get_marks', digits=(8, 3), store=True)
    chemistry_marks = fields.Integer('Chemistry/Computer Marks', compute='_get_marks', digits=(8, 3), store=True)
    math_marks = fields.Integer('Maths/Add Maths Marks', compute='_get_marks', digits=(8, 3), store=True)

    inter_specialization = fields.Selection(
        [('p-che-m', 'Physics-Chemistry-Maths'), ('p-com-m', 'Physics-Computer-Maths'),
         ('a-p-che-m', 'A-levels/Physics-Chemistry-Maths'), ('a-p-com-m', 'A-levels/Physics-Computer-Maths'),
         ('p-che-com-m', 'Physics-Chemistry-Computer-Maths'), ('p-che-adm', 'Physics-Chemistry-Add-Maths')
            , ('p-che-b', 'Physics-Chemistry-Biology'), ('dae-e', 'DAE-Electrical'), ('dae-m', 'DAE-Mechanical'),
         ('dae-c', 'DAE-Civil')],
        string='Majors', compute='_get_marks', store=True)

    # aggregate_percentage
    ssc_aggregates = fields.Float('SSC Aggregate', compute='compute_aggregate', digits=(8, 3), store=True)
    inter_aggregates = fields.Float('Inter Aggregate', compute='compute_aggregate', digits=(8, 3), store=True)
    ug_aggregates = fields.Float('UG Aggregate', compute='compute_aggregate', digits=(8, 3), store=True)
    entry_aggregates = fields.Float('Entry Aggregate', compute='compute_aggregate', digits=(8, 3), store=True)
    interview_aggregates = fields.Float('Interview Aggregate', compute='compute_aggregate', digits=(8, 3), store=True)
    total_aggregates = fields.Float('Total Aggregate', compute='compute_aggregate', digits=(8, 3), store=True)

    physics_aggregates = fields.Float('Physics Aggregate', compute='compute_aggregate', digits=(8, 3), store=True)
    math_aggregates = fields.Float('Math Aggregate/Add Maths', compute='compute_aggregate', digits=(8, 3), store=True)
    chemistry_aggregates = fields.Float('Chemistry/Computer Aggregate', compute='compute_aggregate', digits=(8, 3),
                                        store=True)

    @api.depends('entry_test_of_marks', 'entry_test_obtained_marks')
    def _get_ET_Percentage(self):
        for rec in self:
            if rec.entry_test_of_marks and rec.entry_test_obtained_marks:
                rec.ET_percentage = (rec.entry_test_obtained_marks / rec.entry_test_of_marks) * 100
                rec.test_obtained_marks = rec.entry_test_obtained_marks
                rec.test_percentage = rec.ET_percentage
                rec.entry_aggregates = (rec.test_percentage * (rec.register_id.entry_test / 100))

    @api.depends('interview_total_marks', 'marks_obtained')
    def _get_IM_percentage(self):
        for rec in self:
            if rec.interview_total_marks and rec.marks_obtained:
                rec.IM_percentage = (rec.marks_obtained / rec.interview_total_marks) * 100
                rec.interview_percentage = rec.IM_percentage
                rec.interview_aggregates = (rec.interview_percentage * (rec.register_id.interview_number / 100))

    def make_army_pre(self):
        for rec in self.search([('quota_id2', '!=', False), ('state', '=', 'confirm'), ('register_id', '=', 6)]):
            preference_ids = rec.preference_ids
            pre_list = rec.preference_ids.mapped('preference')
            for pre in preference_ids:
                self.env['odoocms.application.preference'].create(
                    {'application_id': rec.id, 'program_id': pre.program_id.id, 'type': 'Armed Forces',
                     'preference': random.choice(pre_list)})

    def write(self, vals):
        result = super().write(vals)
        # if self.test_type == 'NAT':
        #     self.test_percentage = self.test_obtained_marks

        return result

    @api.depends('academic_ids', 'academic_ids.obtained_marks', 'academic_ids.total_marks', 'academic_ids.degree_level',
                 'academic_ids.is_additional_maths')
    def _get_marks(self):
        for rec in self:
            for academic in rec.academic_ids:
                # if academic.degree_level and academic.total_marks and academic.obtained_marks:
                # if academic.degree_level == 'matric':
                if academic.degree_level == 'Matric':  # SARFRAZ
                    academic.application_id.ssc_marks = academic.obtained_marks
                    academic.application_id.ssc_percentage = academic.percentage

                if academic.degree_level == 'O-Level':  # SARFRAZ
                    academic.application_id.ssc_marks = academic.o_level_obtained
                    academic.application_id.ssc_percentage = academic.o_level_percentage

                if academic.degree_level == 'A-Level':  # SARFRAZ
                    academic.application_id.ssc_marks = academic.o_level_obtained
                    academic.application_id.ssc_percentage = academic.o_level_percentage

                    # academic.application_id.inter_result_status = academic.inter_result_status
                    # academic.application_id.inter_marks = academic.a_level_obtained
                    # academic.application_id.inter_percentage = academic.a_level_percentage
                    # academic.application_id.math_percentage = academic.a_level_math_percentage
                    # academic.application_id.physics_percentage = academic.a_level_physics_percentage
                    # grade_list = ['', 'A*', 'A', 'B', 'C', 'D', 'E', 'F', 'G']
                    # per_list = [0, 90, 85, 75, 65, 55, 45, 40, 35]
                    # academic.application_id.physics_marks = per_list[grade_list.index(academic.a_level_physics)] or 0
                    # academic.application_id.math_marks = per_list[grade_list.index(academic.a_level_math)] or 0
                    #
                    # if academic.inter_result_status == 'Complete':
                    #     if academic.a_level_che and academic.a_level_percentage >= 60:
                    #         academic.application_id.chemistry_percentage = academic.a_level_che_percentage
                    #         academic.application_id.chemistry_marks = per_list[
                    #                                                       grade_list.index(academic.a_level_che)] or 0
                    #         academic.application_id.inter_specialization = 'a-p-che-m'
                    #     elif academic.a_level_com:
                    #         academic.application_id.chemistry_percentage = academic.a_level_com_percentage
                    #         academic.application_id.inter_specialization = 'a-p-com-m'
                    #         academic.application_id.chemistry_marks = per_list[
                    #                                                       grade_list.index(academic.a_level_com)] or 0
                    #     elif academic.a_level_che and academic.a_level_percentage < 60 and academic.a_level_com:
                    #         academic.application_id.chemistry_percentage = academic.a_level_com_percentage
                    #         academic.application_id.chemistry_marks = per_list[
                    #                                                       grade_list.index(academic.a_level_com)] or 0
                    #         academic.application_id.inter_specialization = 'a-p-com-m'
                    #
                    #     elif academic.a_level_che and academic.a_level_percentage < 60 and not academic.a_level_com:
                    #         academic.application_id.chemistry_percentage = academic.a_level_com_percentage
                    #         academic.application_id.chemistry_marks = per_list[
                    #                                                       grade_list.index(academic.a_level_che)] or 0
                    #         academic.application_id.inter_specialization = 'a-p-com-m'
                    # else:
                    #     if academic.a_level_che:
                    #         academic.application_id.chemistry_percentage = academic.a_level_che_percentage
                    #         academic.application_id.chemistry_marks = per_list[
                    #                                                       grade_list.index(academic.a_level_che)] or 0
                    #         academic.application_id.inter_specialization = 'a-p-che-m'
                    #     elif academic.a_level_com:
                    #         academic.application_id.chemistry_percentage = academic.a_level_com_percentage
                    #         academic.application_id.inter_specialization = 'a-p-com-m'
                    #         academic.application_id.chemistry_marks = per_list[
                    #                                                       grade_list.index(academic.a_level_com)] or 0

                if academic.degree_level == 'Intermediate':  # SARFRAZ
                    academic.application_id.inter_result_status = academic.inter_result_status
                    academic.application_id.inter_marks = academic.obtained_marks
                    academic.application_id.inter_percentage = academic.percentage
                    academic.application_id.physics_percentage = academic.physics_marks_per
                    academic.application_id.physics_marks = academic.physics_marks
                    if academic.subjects == 'Pre-Engineering':
                        academic.application_id.chemistry_percentage = academic.chemistry_marks_per
                        academic.application_id.math_percentage = academic.math_marks_per
                        academic.application_id.inter_specialization = 'p-che-m'
                        academic.application_id.math_marks = academic.math_marks
                        academic.application_id.chemistry_marks = academic.chemistry_marks
                    elif academic.subjects == 'ICS':
                        academic.application_id.chemistry_percentage = academic.computer_marks_per
                        academic.application_id.math_percentage = academic.math_marks_per
                        academic.application_id.inter_specialization = 'p-com-m'
                        academic.application_id.math_marks = academic.math_marks
                        academic.application_id.chemistry_marks = academic.computer_marks
                    elif academic.subjects == 'Pre-Medical':
                        academic.application_id.chemistry_percentage = academic.chemistry_marks_per
                        academic.application_id.math_percentage = academic.add_math_marks_per
                        if academic.is_additional_maths == 'Yes':
                            academic.application_id.inter_specialization = 'p-che-adm'
                        else:
                            academic.application_id.inter_specialization = 'p-che-b'
                        academic.application_id.math_marks = academic.add_math_marks
                        academic.application_id.chemistry_marks = academic.chemistry_marks
                    else:
                        academic.application_id.chemistry_percentage = 0
                        academic.application_id.math_percentage = 0
                        academic.application_id.math_marks = 0
                        academic.application_id.chemistry_marks = 0

                if academic.degree_level == 'UG':  # DANISH
                    academic.application_id.ug_cgpa = academic.obtained_marks
                    academic.application_id.ug_cgpa_percentage = academic.percentage

                if academic.degree_level == 'DAE':  # SARFRAZ
                    academic.application_id.inter_marks = academic.dae_obtainedmarks
                    academic.application_id.inter_percentage = academic.dae_percentage
                    academic.application_id.math_percentage = academic.math_marks_per
                    academic.application_id.physics_percentage = academic.physics_marks_per
                    academic.application_id.chemistry_percentage = academic.chemistry_marks_per

                    academic.application_id.physics_marks = academic.physics_marks
                    academic.application_id.math_marks = academic.math_marks
                    academic.application_id.chemistry_marks = academic.chemistry_marks

                    if academic.dae_specialization == 'Mechanical':
                        academic.application_id.inter_specialization = 'dae-m'
                    elif academic.dae_specialization == 'Electrical':
                        academic.application_id.inter_specialization = 'dae-e'
                    elif academic.dae_specialization == 'Civil':
                        academic.application_id.inter_specialization = 'dae-c'
    # Orignal
    # @api.depends('ssc_percentage', 'inter_percentage', 'register_id', 'register_id.matric_o_level_score',
    #              'register_id.intermediate', 'register_id.under_graduate', 'register_id.entry_test', 'register_id.physics_marks',
    #              'register_id.math_marks', 'register_id.chemistry_marks')
    # NEw
    @api.depends('ssc_percentage', 'inter_percentage', 'register_id', 'register_id.matric_o_level_score',
                 'register_id.intermediate', 'register_id.under_graduate', 'register_id.entry_test',
                 'register_id.entry_test',
                 'register_id.interview_number',
                 # 'register_id.physics_marks',
                 # 'register_id.math_marks', 'register_id.chemistry_marks',
                 'entry_aggregates','interview_aggregates')
    def compute_aggregate(self):
        print('Farooq 222')
        for rec in self:
            rec.ssc_aggregates = (rec.ssc_percentage * (rec.register_id.matric_o_level_score / 100))
            rec.inter_aggregates = (rec.inter_percentage * (rec.register_id.intermediate / 100))
            rec.ug_aggregates = (rec.ug_cgpa_percentage * (rec.register_id.under_graduate / 100))
            rec.entry_aggregates = (rec.test_percentage * (rec.register_id.entry_test / 100))
            rec.interview_aggregates = (rec.interview_percentage * (rec.register_id.interview_number / 100))
            # rec.physics_aggregates = (rec.physics_percentage * (rec.register_id.physics_marks / 100))
            # rec.math_aggregates = (rec.math_percentage * (rec.register_id.math_marks / 100))
            # rec.chemistry_aggregates = (rec.chemistry_percentage * (rec.register_id.chemistry_marks / 100))

            # rec.total_aggregates = rec.ssc_aggregates + rec.inter_aggregates + rec.ug_aggregates + rec.entry_aggregates + rec.physics_aggregates + rec.math_aggregates + rec.chemistry_aggregates
            rec.total_aggregates = rec.ssc_aggregates + rec.inter_aggregates + rec.ug_aggregates + rec.entry_aggregates + rec.interview_aggregates

    def verify_voucher(self):
        for rec in self:
            if rec.fee_voucher_state == 'upload':
                data = {
                    'fee_voucher_state': 'verify',
                    'fee_voucher_verified_date': date.today(),
                    'verified_by': self.env.uid,
                }
                template = self.env.ref('odoocms_admission_portal.admission_fee_voucher').sudo()
                fee_step = self.env['odoocms.application.steps'].sudo().search([('template', '=', template.id)])
                if rec.step_number + 1 == (fee_step.sequence):

                    data['step_number'] = (fee_step.sequence)
                else:
                    data['step_number'] = rec.step_number + 1

                rec.sudo().write(data)

                if (rec.is_dual_nationality):
                    template = self.env.ref('odoocms_admission_portal.mail_template_voucher_verified2')
                else:
                    template = self.env.ref('odoocms_admission_portal.mail_template_voucher_verified')
                post_message = rec.message_post_with_template(template.id, composition_mode='comment')

    def univerify_voucher(self):
        for rec in self:
            rec.fee_voucher_state = 'unverify'
            rec.verified_by = self.env.uid,
            template = self.env.ref('odoocms_admission_portal.mail_template_voucher_un_verified')
            post_message = rec.message_post_with_template(template.id, composition_mode='comment')

    # This is to download the report
    def _show_report(self, model, report_type, report_ref, download=False):
        if report_type not in ('html', 'pdf', 'text'):
            raise UserError(_("Invalid report type: %s") % report_type)

        # method_name = 'render_qweb_%s' % (report_type)
        # report = getattr(report_sudo, method_name)([model.id], data={'report_type': report_type})[0]
        report = self.env.ref(report_ref).render_qweb_pdf(model.ids)[0]
        reporthttpheaders = [
            ('Content-Type', 'application/pdf' if report_type == 'pdf' else 'text/html'),
            ('Content-Length', len(report)),
        ]
        if report_type == 'pdf' and download:
            filename = "%s.pdf" % (re.sub('\W+', '-', model.application_no))
            reporthttpheaders.append(('Content-Disposition', content_disposition(filename)))

            if report_ref == 'odoocms_admission_portal.admission_final_report':
                self.write({
                    'application_download_date': date.today(),
                })
        return request.make_response(report, headers=reporthttpheaders)

    # These are Dashboard Functions
    def get_application_details(self):
        if self.sudo().search([], limit=1):
            return self
        else:
            return False

    def action_entry_test_verified(self):
        for rec in self:
            rec.entry_test_status = 'Yes'
            msg = "The Entry Test has been verified by the user " + self.env.user.login + " on " + str(
                fields.Datetime.now())
            rec.message_post(body=msg)
            count = 0
            for academic in rec.academic_ids:
                if academic.document_status == 'Yes':
                    count += 1
            if count >= 2:
                rec.state = 'verified'

    def action_entry_test_unverified(self):
        for rec in self:
            rec.entry_test_status = 'No'
            msg = "The Entry Test has been Unverified by the user " + self.env.user.login + " on " + str(
                fields.Datetime.now())
            rec.message_post(body=msg)
            rec.state = 'confirm'

    def action_entry_test_rejected(self):
        for rec in self:
            rec.entry_test_status = 'Rejected'
            msg = "The Entry Test has been Rejected by the user " + self.env.user.login + " on " + str(
                fields.Datetime.now())
            rec.message_post(body=msg)
            rec.state = 'reject'

    @api.model
    def get_total_registration_list_view(self):
        return {'registration_list_id': self.env.ref('odoocms_admission_portal.view_odoocms_application_tree1').id}

    @api.model
    def get_downloaded_list_view(self):
        return {'downloaded_list_id': self.env.ref('odoocms_admission_portal.view_odoocms_application_tree2').id}

    @api.model
    def get_upload_list_view(self):
        return {'upload_list_id': self.env.ref('odoocms_admission_portal.view_odoocms_application_tree3').id}

    @api.model
    def get_verified_list_view(self):
        return {'verified_list_id': self.env.ref('odoocms_admission_portal.view_odoocms_application_tree4').id}

    @api.model
    def get_unverified_list_view(self):
        return {'unverified_list_id': self.env.ref('odoocms_admission_portal.view_odoocms_application_tree5').id}

    @api.model
    def get_final_score_list_view(self):
        return {'final_score_list_id': self.env.ref('odoocms_admission_portal.view_odoocms_application_tree6').id}

    @api.model
    def get_confirm_applications_list_view(self):
        return {
            'confirm_applications_list_id': self.env.ref('odoocms_admission_portal.view_odoocms_application_tree1').id}

    def cron_compute_aggregate(self, register_id, state):
        for rec in self.search([('register_id', '=', register_id), ('state', '=', state)]):
            for academic in rec.academic_ids:
                if academic.degree_level in ('Intermediate', 'DAE'):
                    if academic.physics_total_marks and academic.physics_marks:
                        academic.physics_marks_per = academic.physics_marks / academic.physics_total_marks * 100
                    if academic.math_total_marks and academic.math_marks:
                        academic.math_marks_per = academic.math_marks / academic.math_total_marks * 100
                    if academic.add_math_total_marks and academic.add_math_marks:
                        academic.add_math_marks_per = academic.add_math_marks / academic.add_math_total_marks * 100
                    if academic.chemistry_total_marks and academic.chemistry_marks:
                        academic.chemistry_marks_per = academic.chemistry_marks / academic.chemistry_total_marks * 100
                    if academic.computer_total_marks and academic.computer_marks:
                        academic.computer_marks_per = academic.computer_marks / academic.computer_total_marks * 100

                if academic.degree_level == 'Matric':  # SARFRAZ
                    academic.percentage = academic.obtained_marks / academic.total_marks * 100

                if academic.degree_level == 'O-Level':  # SARFRAZ
                    academic.o_level_percentage = academic.o_level_obtained / academic.o_level_total * 100

                if academic.degree_level == 'A-Level':  # SARFRAZ
                    academic.a_level_percentage = academic.a_level_obtained / academic.a_level_total * 100

                if academic.degree_level == 'Intermediate':  # SARFRAZ
                    academic.percentage = academic.obtained_marks / academic.total_marks * 100

                if academic.degree_level == 'DAE':  # SARFRAZ
                    academic.dae_percentage = academic.dae_obtainedmarks / academic.dae_totalmarks * 100

        self._get_marks()
        self.compute_aggregate()


class OdooCMSAdmissionApplicationAcademic(models.Model):
    _inherit = 'odoocms.application.academic'

    o_level_total = fields.Integer('Total Marks', default=0)
    o_level_obtained = fields.Integer('Obtained Marks', default=0)
    o_level_percentage = fields.Float('Percentage', default=0)

    grade_aa = fields.Integer('A* Grades')
    grade_a = fields.Integer('A Grades')
    grade_b = fields.Integer('B Grades')
    grade_c = fields.Integer('C Grades')
    grade_d = fields.Integer('D Grades')
    grade_e = fields.Integer('E Grades')
    grade_f = fields.Integer('F Grades')
    grade_g = fields.Integer('G Grades')

    a_level_total = fields.Integer('Total Marks', default=0)
    a_level_obtained = fields.Integer('Obtained Marks', default=0)
    a_level_percentage = fields.Float('Percentage', default=0)

    a_level_grade_aa = fields.Integer('A* Grades')
    a_level_grade_a = fields.Integer('A Grades')
    a_level_grade_b = fields.Integer('B Grades')
    a_level_grade_c = fields.Integer('C Grades')
    a_level_grade_d = fields.Integer('D Grades')
    a_level_grade_e = fields.Integer('E Grades')
    a_level_grade_f = fields.Integer('F Grades')
    a_level_grade_g = fields.Integer('G Grades')

    a_level_math = fields.Char('Math Grade')
    a_level_che = fields.Char('Che Grade')
    a_level_com = fields.Char('Computer Grade')
    a_level_physics = fields.Char('Physucs Grade')
    a_level_math_percentage = fields.Float('Math Grade Percentage', default=0)
    a_level_che_percentage = fields.Float('Che Grade Percentage', default=0)
    a_level_com_percentage = fields.Float('Com Grade Percentage', default=0)
    a_level_physics_percentage = fields.Float('Physics Grade Percentage', default=0)

    inter_result_status = fields.Char('Result Status', default="Complete")
    dae_result_status = fields.Char('Result Status', default="Complete")


class OdooCMSAdmissionApplicationDocuments(models.Model):
    _inherit = 'odoocms.application.documents'

    hope_certificate_scanned_copy = fields.Binary('Scanned Copy of Hope Certificate', attachment=True)
    hope_certificate_scanned_copy_name = fields.Text('Scanned Copy of Hope Certificate')
    hope_certificate_scanned_copy_size = fields.Text('Scanned Copy of Hope Certificate')

    cnic_back_scanned_copy = fields.Binary('Scanned Copy of CNIC Back', attachment=True)
    cnic_back_scanned_copy_name = fields.Text('Scanned Copy of CNIC Back Name')
    cnic_back_scanned_copy_size = fields.Text('Scanned Copy of CNIC Back Size')

    dae_first_year = fields.Binary('Scanned Copy of DAE FY', attachment=True)
    dae_first_year_name = fields.Text('Scanned Copy of DAE FY Name')
    dae_first_year_size = fields.Text('Scanned Copy of DAE FY Size')

    dae_second_year = fields.Binary('Scanned Copy of DAE 2nd Y', attachment=True)
    dae_second_year_name = fields.Text('Scanned Copy of DAE 2nd Y Name')
    dae_second_year_size = fields.Text('Scanned Copy of DAE 2nd Y Size')

    dae_third_year = fields.Binary('Scanned Copy of DAE 3rd Y', attachment=True)
    dae_third_year_name = fields.Text('Scanned Copy of DAE 3rd Y Name')
    dae_third_year_size = fields.Text('Scanned Copy of DAE 3rd Y Size')


class OdooCMSAggregateConfig(models.Model):
    _name = 'odoocms.aggregate.config'
    _description = 'Aggregate Config'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', tracking=True)
    sequence = fields.Char('Sequence', tracking=True)
    matric_o_level_score = fields.Float('Matric / O-Level', default=10.0, tracking=True)
    intermediate = fields.Float('Intermediate', default=30.0, tracking=True)
    entry_test = fields.Float('Entry Test', default=60.0, tracking=True)


class OdoocmsMeritRegister(models.Model):
    _inherit = 'odoocms.merit.register'

    state = fields.Selection([('draft', 'Draft'), ('open', 'Open'), ('done', 'Done')], string='Status', default='draft',
                             tracking=True)

    def make_open(self):
        if self.state == 'draft':
            self.state = 'open'
            for app_merit in self.merit_application_ids:
                template = self.env.ref('odoocms_admission_portal.mail_template_application_merit_list')
                post_message = app_merit.message_post_with_template(template.id, composition_mode='comment')

    def back_to_draft(self):
        if self.state == 'open':
            self.state = 'draft'


class OdoocmsApplicationMerit(models.Model):
    _inherit = 'odoocms.application.merit'

    total_aggregates = fields.Float('Aggregates', related='application_id.total_aggregates', store=True)
    voucher_status = fields.Selection([('reject', 'Rejected'), ('accept', 'Accepted')], 'Verification Status')
    voucher_image = fields.Binary('Voucher', store=True)
    voucher_number = fields.Char('Voucher Number')
    date_voucher = fields.Date('Voucher Submission Date')
    date_submission = fields.Date('Voucher upload Date')
    application_no = fields.Char(related='application_id.application_no', store=True)

    def verify_applicant(self):
        self.voucher_status = 'accept'
        self.state = 'done'
        self.application_id.state = 'approve'
        if self.preference == 1:
            self.locked = True
        if self.locked:
            self.application_id.locked = True

    def reject_applicant(self):
        self.application_id.state = 'reject'
        self.application_id.message_post(body='Admission Cancelled after listing in Merit list.')
        self.state = 'reject'
        self.voucher_status = 'reject'

    def univerify_applicant(self):
        self.application_id.state = 'confirm'
        self.state = 'draft'
        self.voucher_status = False
        self.application_id.locked = False
        self.locked = False

    def mark_absent(self):
        self.application_id.state = 'reject'
        self.application_id.message_post(body='Admission Cancelled after listing in Merit list.')
        self.state = 'absent'
