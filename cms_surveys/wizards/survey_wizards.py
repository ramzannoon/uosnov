from odoo import models, fields, _, api
from odoo.exceptions import UserError
from collections import Counter, OrderedDict
from itertools import product

import pdb


class SurveysTemplate(models.TransientModel):
    _name = 'survey.wizard'
    _description = 'Survey Creation Wizard'

    template = fields.Many2one(comodel_name='survey.survey', string='Template', required=True,
                               domain=[('type', '=', 'template')], )
    template_seq_no = fields.Char(related='template.template_seq_no', string='Template ID', required=False, )
    survey_form_type = fields.Many2one(related='template.survey_form_type', string='Form Types')
    survey_form_type_name = fields.Char(related='survey_form_type.name', string='Form Types Name', required=False, )

    domain_rule = fields.Char('Domain Rule')
    student_id = fields.Many2one('odoocms.student', string='Student')
    faculty_department_id = fields.Many2one(comodel_name='odoocms.department', string='Department', required=False, )
    faculty_institute_id = fields.Many2one(comodel_name='odoocms.institute', string='Faculty Institute',
                                           required=False, )

    campus_id = fields.Many2one(comodel_name='odoocms.campus', string='Campus',
                                required=False, )
    institute_id = fields.Many2one(comodel_name='odoocms.institute', string='School', required=False, )

    career_id = fields.Many2one(comodel_name='odoocms.career', string='Academic Level', required=False, )

    department_id = fields.Many2one(comodel_name='odoocms.department', string='Department', required=False, )

    program_id = fields.Many2one(comodel_name='odoocms.program', string='Program', required=False, )

    batch_id = fields.Many2one(comodel_name='odoocms.batch', string='Batch', required=False, )
    batch_ids = fields.Many2many('odoocms.batch', 'relsurvey_wizard', 'survey_id', 'batch_id', 'Batch',
                                 required=False, )

    start_date = fields.Datetime(string="Start Date", required=True, default=fields.Datetime.now, )
    end_date = fields.Datetime(string="End Date", required=True, default=fields.Datetime.now, )

    term_id = fields.Many2one('odoocms.academic.term', string='Academic Term')
    primary_class_id = fields.Many2one(comodel_name='odoocms.class.primary', string='Primary Class', )
    class_id = fields.Many2one('odoocms.class.primary', string='Class', )
    section_id = fields.Many2one('odoocms.batch.section', string='Section', )

    def create_survey_form(self):

        for rec in self:
            if rec.template:
                if self.start_date >= self.end_date:
                    raise UserError(
                        _("End date should be after Start Date: "))
                else:
                    self.template.start_date = self.start_date
                    self.template.end_date = self.end_date
                    self.template.survey_form_type = self.survey_form_type
                    for batch_id in self.batch_ids:
                        if self.template_seq_no == 'Temp/0001' or self.template_seq_no == 'Temp/0002' \
                                or self.template_seq_no == 'Temp/0004' or self.template_seq_no == 'Temp/0008' \
                                or self.template_seq_no == 'Temp/0005':
                            if batch_id:

                                self.template.batch_id = batch_id
                                if not self.program_id:
                                    self.template.program_id = batch_id.program_id
                                elif not self.department_id:
                                    self.template.department_id = batch_id.department_id
                                elif not self.career_id:
                                    self.template.career_id = batch_id.career_id
                                elif not self.institute_id:
                                    self.template.institute_id = batch_id.program_id.institute_id
                                elif not self.campus_id:
                                    self.template.campus_id = batch_id.program_id.institute_id.campus_id
                            elif self.program_id:
                                self.template.program_id = self.program_id
                                if not self.department_id:
                                    self.template.department_id = self.program_id.department_id
                                elif not self.career_id:
                                    self.template.career_id = self.program_id.career_id
                                elif not self.institute_id:
                                    self.template.institute_id = self.program_id.institute_id
                                elif not self.campus_id:
                                    self.template.campus_id = self.program_id.institute_id.campus_id
                            elif self.department_id:
                                self.template.department_id = self.department_id
                                if not self.institute_id:
                                    self.template.institute_id = self.department_id.institute_id
                                elif not self.campus_id:
                                    self.template.campus_id = self.department_id.institute_id.campus_id
                            else:
                                raise UserError(_('Invalid Filter, Required Batch Field'))
                            for section_id in batch_id.section_ids:
                                if section_id:
                                    if self.template_seq_no == 'Temp/0004' or self.template_seq_no == 'Temp/0008' or self.template_seq_no == 'Temp/0005':
                                        if self.section_id:
                                            self.template.section_id = self.section_id
                                            survey = self.template.copy(None)

                                            already_exists = self.env['survey.survey'].sudo().search(
                                                [('id', '!=', survey.id), ('title', '=', survey.title),
                                                 ('state', '=', 'open')])
                                            if already_exists:
                                                raise UserError(
                                                    _("Duplicate Survey is not Allowed. Survey already exists with: \n Title = ' %s '" % (
                                                        already_exists.title)))
                                            survey.template_seq_no = self.template_seq_no
                                            survey_question_ids = self.env['survey.question'].sudo().search(
                                                [('survey_id', '=', survey.id)])
                                            for student in section_id.sudo().student_ids:
                                                if student:
                                                    vals = {
                                                        'survey_id': survey.id,
                                                        'input_type': 'link',
                                                        'partner_id': student[0].partner_id.id,
                                                        'email': student[0].user_id.login,
                                                        'course_id': survey.course_id.id,
                                                        'career_id': student[0].career_id.id,
                                                        'deadline': self.template.end_date,
                                                        'question_ids': survey_question_ids,
                                                    }
                                                    self.env['survey.user_input'].sudo().create(vals)
                                                    survey.state = 'open'
                                                else:
                                                    ValueError(
                                                        _('No Student Registered under Section:  %s' % section_id.code))
                                            break
                                        else:
                                            self.template.section_id = section_id
                                        survey = self.template.copy(None)

                                        already_exists = self.env['survey.survey'].sudo().search(
                                            [('id', '!=', survey.id), ('title', '=', survey.title),
                                             ('state', '=', 'open')])
                                        if already_exists:
                                            raise UserError(
                                                _("Duplicate Survey is not Allowed. Survey already exists with: \n Title = ' %s '" % (
                                                    already_exists.title)))
                                        survey.template_seq_no = self.template_seq_no
                                        survey_question_ids = self.env['survey.question'].search(
                                            [('survey_id', '=', survey.id)])
                                        for student in section_id.sudo().student_ids:
                                            if student:
                                                vals = {
                                                    'survey_id': survey.id,
                                                    'input_type': 'link',
                                                    'partner_id': student[0].partner_id.id,
                                                    'email': student[0].user_id.login,
                                                    'course_id': survey.course_id.id,
                                                    'career_id': student[0].career_id.id,
                                                    'deadline': self.template.end_date,
                                                    'question_ids': survey_question_ids,
                                                }
                                                self.env['survey.user_input'].sudo().create(vals)
                                                survey.state = 'open'
                                            else:
                                                ValueError(
                                                    _('No Student Registered under Section:  %s' % section_id.code))
                                    else:
                                        for primary_class in section_id.primary_class_ids.filtered(
                                                lambda l: l.term_id == batch_id.term_id):
                                            if primary_class:
                                                for component_class in primary_class.class_ids:
                                                    self.template.class_id = component_class
                                                    self.template.faculty_staff_id = component_class.faculty_staff_id
                                                    survey = self.template.copy(None)

                                                    already_exists = self.env['survey.survey'].sudo().search(
                                                        [('id', '!=', survey.id), ('title', '=', survey.title),
                                                         ('state', '=', 'open')])
                                                    if already_exists:
                                                        raise UserError(
                                                            _("Duplicate Survey is not Allowed. Survey already exists with: \n Title = ' %s '" % (
                                                                already_exists.title)))
                                                    survey.template_seq_no = self.template_seq_no
                                                    survey.term_id = component_class.term_id
                                                    survey_question_ids = self.env['survey.question'].sudo().search(
                                                        [('survey_id', '=', survey.id)])
                                                    for student in component_class.registration_component_ids.sudo().student_id:
                                                        if student:
                                                            vals = {
                                                                'survey_id': survey.id,
                                                                'input_type': 'link',
                                                                'partner_id': student[0].partner_id.id,
                                                                'email': student[0].user_id.login,
                                                                'course_id': survey.course_id.id,
                                                                'career_id': student[0].career_id.id,
                                                                'deadline': self.template.end_date,
                                                                'question_ids': survey_question_ids,
                                                            }
                                                            self.env['survey.user_input'].sudo().create(vals)
                                                            survey.state = 'open'
                                                        else:
                                                            ValueError(_(
                                                                'No Student Registered under Component Class:  %s' % component_class.code))
                                            else:
                                                ValueError(_('No primary class Exist Under Batch: %s ' % batch_id.name))
                        elif self.template_seq_no == 'Temp/0010' or self.template_seq_no == 'Temp/0011':
                            if self.faculty_institute_id:
                                self.template.institute_id = self.faculty_institute_id
                                self.template.campus_id = self.faculty_institute_id.campus_id
                            elif self.institute_id:
                                self.template.institute_id = self.institute_id
                                self.template.campus_id = self.institute_id.campus_id
                            survey = self.template.copy(None)

                            already_exists = self.env['survey.survey'].sudo().search(
                                [('id', '!=', survey.id), ('title', '=', survey.title),
                                 ('state', '=', 'open')])
                            if already_exists:
                                raise UserError(
                                    _("Duplicate Survey is not Allowed. Survey already exists with: \n Title = ' %s '" % (
                                        already_exists.title)))
                            survey.template_seq_no = self.template_seq_no
                            survey_question_ids = self.env['survey.question'].search(
                                [('survey_id', '=', survey.id)])
                            for faculty_id in self.template.institute_id.faculty_ids:
                                # self.template.faculty_staff_id = faculty_id
                                vals = {
                                    'survey_id': survey.id,
                                    'input_type': 'link',
                                    'partner_id': faculty_id.employee_id.user_partner_id.id,
                                    'email': faculty_id.employee_id.user_partner_id.email,
                                    'deadline': self.template.end_date,
                                    'question_ids': survey_question_ids,
                                }
                                self.env['survey.user_input'].sudo().create(vals)
                                survey.state = 'open'
                        elif self.template_seq_no == 'Temp/0006':
                            if self.student_id:
                                self.template.student_id = self.student_id
                                self.template.batch_id = self.student_id.batch_id
                                self.template.program_id = batch_id.program_id
                                self.template.department_id = batch_id.department_id
                                self.template.career_id = batch_id.career_id
                                self.template.institute_id = batch_id.program_id.institute_id
                                self.template.campus_id = batch_id.program_id.institute_id.campus_id
                            elif self.program_id:
                                self.template.program_id = self.program_id
                                self.template.department_id = self.program_id.department_id
                                self.template.career_id = self.program_id.career_id
                                self.template.institute_id = self.program_id.institute_id
                                self.template.campus_id = self.program_id.institute_id.campus_id
                            elif self.department_id:
                                self.template.department_id = self.department_id
                                self.template.institute_id = self.department_id.institute_id
                                self.template.campus_id = self.department_id.institute_id.campus_id
                            self.template.copy(None)

                        elif self.template_seq_no == 'Temp/0009' or self.template_seq_no == 'Temp/0016':
                            for section_id in batch_id.section_ids:
                                for primary_class in section_id.primary_class_ids.filtered(
                                        lambda l: l.term_id == batch_id.term_id):
                                    if primary_class:
                                        assessments_values = {}
                                        assessments = OrderedDict()
                                        assessments_name = []
                                        assessments_count = []
                                        # answers = OrderedDict()
                                        # # options = OrderedDict()
                                        res = dict()
                                        self.template.primary_class_id = primary_class
                                        self.template.faculty_staff_id = primary_class.grade_staff_id
                                        self.template.term_id = primary_class.term_id
                                        if batch_id:
                                            self.template.section_id = section_id
                                            self.template.batch_id = batch_id
                                            self.template.program_id = batch_id.program_id
                                            self.template.department_id = batch_id.department_id
                                            self.template.career_id = batch_id.career_id
                                            self.template.institute_id = batch_id.program_id.institute_id
                                            self.template.campus_id = batch_id.program_id.institute_id.campus_id

                                        for component_class in primary_class.class_ids:
                                            Assignments = 0
                                            # assessment_component_class_search = self.env['odoocms.assessment.component'].sudo().search(
                                            #      [('class_id', '=', component_class.id)])
                                            # assessment_component_class_search = self.env['odoocms.assessment'].sudo().search(
                                            #      [('class_id', '=', component_class.id)])
                                            # assessment_component_class = self.env[
                                            #     'odoocms.assessment.component'].read_group((
                                            #     [('class_id', '=', component_class.id)]), fields=['assessment_type_id'],
                                            #     groupby=['assessment_type_name'])

                                            assessment_component_class = self.env['odoocms.assessment'].read_group((
                                                                                            [('class_id', '=', component_class.id)]), fields=['assessment_component_id'],
                                                                                            groupby=['assessment_component_id'])

                                            for i in range(len(assessment_component_class)):
                                                if assessment_component_class[i]['assessment_component_id'] and assessment_component_class[i]['assessment_component_id_count']:
                                                    assessments_name.append(assessment_component_class[i]['assessment_component_id'][1])
                                                    # assessments_name.append(assessment_component_class[i]['assessment_component_id'])
                                                    assessments_count.append(assessment_component_class[i]['assessment_component_id_count'])

                                        countA = 0
                                        countBplus = 0
                                        countB = 0
                                        countCplus = 0
                                        countC = 0
                                        countDplus = 0
                                        countD = 0
                                        countF = 0
                                        countW = 0
                                        countI = 0
                                        student_grad = self.env['odoocms.student.course'].sudo().search(
                                            [('primary_class_id', '=', primary_class.id)])
                                        for student in student_grad:
                                            if student.grade == 'A':
                                                countA += 1
                                            elif student.grade == 'B+':
                                                countBplus += 1
                                            elif student.grade == 'B':
                                                countB += 1
                                            elif student.grade == 'C+':
                                                countCplus += 1
                                            elif student.grade == 'C':
                                                countC += 1
                                            elif student.grade == 'D+':
                                                countDplus += 1
                                            elif student.grade == 'D':
                                                countD += 1
                                            elif student.grade == 'F':
                                                countF += 1
                                            elif student.grade == 'W':
                                                countW += 1
                                            elif student.grade == 'I':
                                                countI += 1

                                        self.template.course_count_a = countA
                                        self.template.course_count_b_plus = countBplus
                                        self.template.course_count_b = countB
                                        self.template.course_count_c_plus = countCplus
                                        self.template.course_count_c = countC
                                        self.template.course_count_d_plus = countDplus
                                        self.template.course_count_d = countD
                                        self.template.course_count_f = countF
                                        self.template.course_count_w = countW
                                        self.template.course_count_i = countI

                                        if self.template.faculty_staff_id.id:
                                            survey = self.template.copy(None)
                                            already_exists = self.env['survey.survey'].sudo().search(
                                                [('id', '!=', survey.id), ('title', '=', survey.title),
                                                 ('state', '=', 'open')])
                                            if already_exists:
                                                raise UserError(
                                                    _("Duplicate Survey is not Allowed. Survey already exists with: \n Title = ' %s '" % (
                                                        already_exists.title)))
                                            survey.template_seq_no = self.template_seq_no
                                            if self.template.faculty_staff_id and self.template.term_id.code:
                                                survey.title = survey.title + ' - ' + self.template.faculty_staff_id.name + ' - '  + self.template.term_id.code
                                            else:
                                                survey.title = survey.title + ' - ' + self.template.faculty_staff_id.name
                                            already_exists = self.env['survey.survey'].sudo().search(
                                                [('id', '!=', survey.id), ('title', '=', survey.title),
                                                 ('state', '=', 'open')])
                                            if already_exists:
                                                raise UserError(
                                                    _("Duplicate Survey is not Allowed. Survey already exists with: \n Title = ' %s '" % (
                                                        already_exists.title)))
                                            survey_question_ids = self.env['survey.question'].sudo().search(
                                                [('survey_id', '=', survey.id)])
                                            for i in range(assessments_count.__len__()):
                                                assessments_values= {
                                                    'survey_id': survey.id,
                                                    'primary_class_id': primary_class.id,
                                                    'assessment_name': assessments_name[i],
                                                    'count': assessments_count[i],
                                                }
                                                self.env['survey.course_rev.assesments_types'].sudo().create(assessments_values)
                                            vals = {
                                                'survey_id': survey.id,
                                                'input_type': 'link',
                                                'partner_id': primary_class.grade_staff_id.user_id.partner_id.id,
                                                'email': primary_class.grade_staff_id.user_id.login,
                                                'deadline': self.template.end_date,
                                                'question_ids': survey_question_ids,
                                            }
                                            self.env['survey.user_input'].sudo().create(vals)
                                            survey.state = 'open'
                    if self.template_seq_no == 'Temp/0012' or self.template_seq_no == 'Temp/0003':
                        if self.faculty_institute_id and self.faculty_department_id:
                            self.template.institute_id = self.faculty_institute_id
                            self.institute_id = self.faculty_institute_id
                            self.template.campus_id = self.faculty_institute_id.campus_id
                            self.template.department_id = self.faculty_department_id
                            if not self.template_seq_no == 'Temp/0003':
                                faculty_ids = self.env['odoocms.hr.emp.rec.master'].search(
                                    [('hr_emp_placed_dept', '=', self.template.department_id.id),
                                     ('hr_emp_status', '=', 'A'),
                                     ('hr_emp_category', '=', 'F')])
                                for faculty_id in faculty_ids:
                                    self.template.faculty_staff_id = self.env['odoocms.faculty.staff'].sudo().search(
                                        [('id', '=', faculty_id.faculty_staff_id.id)])
                                    if self.term_id:
                                        self.template.term_id = self.term_id
                                    if self.template.faculty_staff_id.employee_id != self.faculty_department_id.hod_id:
                                        courses = self.env['odoocms.class.primary'].read_group(
                                            [('grade_staff_id', '=', self.template.faculty_staff_id.id),
                                             ('term_id', '=', self.term_id.id)], fields=['course_id'],
                                            groupby=['course_id'])
                                        for i in range(len(courses)):
                                            courses_catalog = self.env['odoocms.course'].search(
                                                [('id', '=', courses[i]['course_id'][0])])
                                            class_id = self.env['odoocms.class.primary'].search([
                                                ('grade_staff_id', '=', self.template.faculty_staff_id.id),
                                                ('term_id', '=', self.term_id.id), ('course_id', '=', courses[i]['course_id'][0])])
                                            survey = self.template.copy(None)

                                            already_exists = self.env['survey.survey'].sudo().search(
                                                [('id', '!=', survey.id), ('title', '=', survey.title),
                                                 ('state', '=', 'open')])
                                            if already_exists:
                                                raise UserError(
                                                    _("Duplicate Survey is not Allowed. Survey already exists with: \n Title = ' %s '" % (
                                                        already_exists.title)))
                                            survey.institute_id = self.faculty_institute_id
                                            survey.template_seq_no = self.template_seq_no
                                            survey.term_id = self.term_id
                                            if self.faculty_department_id:
                                                survey.department_id = self.faculty_department_id
                                            if class_id[0]:
                                                survey.title = survey.title + ' - ' + self.template.faculty_staff_id.name + ' - ' + class_id[0].code + ' - ' + self.term_id.code
                                                # survey.title = survey.title + ' - ' + self.template.faculty_staff_id.name + ' - ' + courses_catalog.code + ' - ' + self.term_id.code
                                            else:
                                                survey.title = survey.title + ' - ' + self.template.faculty_staff_id.name + self.term_id.code
                                            already_exists = self.env['survey.survey'].sudo().search(
                                                [('id', '!=', survey.id), ('title', '=', survey.title),
                                                 ('state', '=', 'open')])
                                            if already_exists:
                                                raise UserError(
                                                    _("Duplicate Survey is not Allowed. Survey already exists with: \n Title = ' %s '" % (
                                                        already_exists.title)))
                                            survey_question_ids = self.env['survey.question'].sudo().search(
                                                [('survey_id', '=', survey.id)])
                                            if self.faculty_department_id.hod_id:
                                                vals = {
                                                    'survey_id': survey.id,
                                                    'input_type': 'link',
                                                    'partner_id': self.faculty_department_id.hod_id.user_id.partner_id.id,
                                                    'email': self.faculty_department_id.hod_id.user_partner_id.email or self.faculty_department_id.hod_id.user_id.login,
                                                    'deadline': self.template.end_date,
                                                    'question_ids': survey_question_ids,
                                                }
                                                self.env['survey.user_input'].sudo().create(vals)
                                            survey.state = 'open'
                            else:
                                faculty_ids = self.env['odoocms.hr.emp.rec.master'].search(
                                    [('hr_emp_placed_dept', '=', self.template.department_id.id),
                                     ('hr_emp_status', '=', 'A'),
                                     ('hr_emp_category', '=', 'F')])
                                for faculty_id in faculty_ids:
                                    survey = self.template.copy(None)

                                    already_exists = self.env['survey.survey'].sudo().search(
                                        [('id', '!=', survey.id), ('title', '=', survey.title),
                                         ('state', '=', 'open')])
                                    if already_exists:
                                        raise UserError(
                                            _("Duplicate Survey is not Allowed. Survey already exists with: \n Title = ' %s '" % (
                                                already_exists.title)))
                                    survey.institute_id = self.faculty_institute_id
                                    survey.template_seq_no = self.template_seq_no

                                    if self.faculty_department_id:
                                        survey.department_id = self.faculty_department_id
                                    if self.term_id:
                                        survey.term_id = self.term_id
                                        survey.title = survey.title + ' - ' + faculty_id.faculty_staff_id.name + ' - ' + self.term_id.code
                                    already_exists = self.env['survey.survey'].sudo().search(
                                        [('id', '!=', survey.id), ('title', '=', survey.title),
                                         ('state', '=', 'open')])
                                    if already_exists:
                                        raise UserError(
                                            _("Duplicate Survey is not Allowed. Survey already exists with: \n Title = ' %s '" % (
                                                already_exists.title)))
                                    survey_question_ids = self.env['survey.question'].search(
                                        [('survey_id', '=', survey.id)])
                                    if faculty_id:
                                        vals = {
                                            'survey_id': survey.id,
                                            'input_type': 'link',
                                            'partner_id': faculty_id.faculty_staff_id.user_partner_id.id,
                                            'email': faculty_id.faculty_staff_id.user_partner_id.email,
                                            'deadline': self.template.end_date,
                                            'question_ids': survey_question_ids,
                                        }
                                        self.env['survey.user_input'].sudo().create(vals)
                                    survey.state = 'open'

                        elif self.faculty_institute_id and not self.faculty_department_id:
                            self.template.institute_id = self.faculty_institute_id
                            self.institute_id = self.faculty_institute_id
                            self.template.campus_id = self.faculty_institute_id.campus_id
                            if self.term_id:
                                self.template.term_id = self.term_id

                            for department in self.faculty_institute_id.department_ids:
                                self.template.department_id = department
                                if not self.template_seq_no == 'Temp/0003':
                                    faculty_ids = self.env['odoocms.hr.emp.rec.master'].sudo().search(
                                        [('hr_emp_placed_dept', '=', self.template.department_id.id),
                                         ('hr_emp_status', '=', 'A'),
                                         ('hr_emp_category', '=', 'F')])
                                    for faculty_id in faculty_ids:
                                        self.template.faculty_staff_id = self.env['odoocms.faculty.staff'].sudo().search(
                                            [('id', '=', faculty_id.faculty_staff_id.id)])
                                        if self.template.faculty_staff_id.employee_id != department.hod_id:
                                            courses = self.env['odoocms.class.primary'].read_group(
                                                [('grade_staff_id', '=', self.template.faculty_staff_id.id),
                                                 ('term_id', '=', self.term_id.id)], fields=['course_id'],
                                                groupby=['course_id'])
                                            for i in range(len(courses)):
                                                courses_catalog = self.env['odoocms.course'].sudo().search(
                                                    [('id', '=', courses[i]['course_id'][0])])
                                                class_id = self.env['odoocms.class.primary'].sudo().search([
                                                    ('grade_staff_id', '=', self.template.faculty_staff_id.id),
                                                    ('term_id', '=', self.term_id.id),
                                                    ('course_id', '=', courses[i]['course_id'][0])])
                                                survey = self.template.copy(None)

                                                already_exists = self.env['survey.survey'].sudo().search(
                                                    [('id', '!=', survey.id), ('title', '=', survey.title),
                                                     ('state', '=', 'open')])
                                                if already_exists:
                                                    raise UserError(
                                                        _("Duplicate Survey is not Allowed. Survey already exists with: \n Title = ' %s '" % (
                                                            already_exists.title)))
                                                survey.institute_id = self.faculty_institute_id
                                                survey.department_id = department
                                                survey.template_seq_no = self.template_seq_no
                                                survey.term_id = self.term_id
                                                if class_id.code:
                                                    survey.title = survey.title + ' - ' + self.template.faculty_staff_id.name + ' - ' + class_id.code + ' - ' + self.term_id.code
                                                # if courses_catalog.code:
                                                #     survey.title = survey.title + ' - ' + self.template.faculty_staff_id.name + ' - ' + courses_catalog.code + ' - ' + self.term_id.code
                                                else:
                                                    survey.title = survey.title + ' - ' + self.template.faculty_staff_id.name + self.term_id.code

                                                already_exists = self.env['survey.survey'].sudo().search(
                                                    [('id', '!=', survey.id), ('title', '=', survey.title),
                                                     ('state', '=', 'open')])
                                                if already_exists:
                                                    raise UserError(
                                                        _("Duplicate Survey is not Allowed. Survey already exists with: \n Title = ' %s '" % (
                                                            already_exists.title)))
                                                survey_question_ids = self.env['survey.question'].search(
                                                    [('survey_id', '=', survey.id)])
                                                if department.hod_id:
                                                    vals = {
                                                        'survey_id': survey.id,
                                                        'input_type': 'link',
                                                        'partner_id': department.hod_id.user_id.partner_id.id,
                                                        'email': department.hod_id.user_partner_id.email or department.hod_id.user_id.login,
                                                        'deadline': self.template.end_date,
                                                        'question_ids': survey_question_ids,
                                                    }
                                                    self.env['survey.user_input'].sudo().create(vals)
                                                survey.state = 'open'
                                else:
                                    faculty_ids = self.env['odoocms.hr.emp.rec.master'].search(
                                        [('hr_emp_placed_dept', '=', self.template.department_id.id),
                                         ('hr_emp_status', '=', 'A'),
                                         ('hr_emp_category', '=', 'F')])
                                    for faculty_id in faculty_ids:
                                        survey = self.template.copy(None)

                                        already_exists = self.env['survey.survey'].sudo().search(
                                            [('id', '!=', survey.id), ('title', '=', survey.title),
                                             ('state', '=', 'open')])
                                        if already_exists:
                                            raise UserError(
                                                _("Duplicate Survey is not Allowed. Survey already exists with: \n Title = ' %s '" % (
                                                    already_exists.title)))
                                        survey.institute_id = self.faculty_institute_id
                                        survey.template_seq_no = self.template_seq_no

                                        if department:
                                            survey.department_id = department
                                        if self.term_id:
                                            survey.term_id = self.term_id
                                            survey.title = survey.title + ' - ' + faculty_id.faculty_staff_id.name + ' - ' + self.term_id.code
                                        already_exists = self.env['survey.survey'].sudo().search(
                                            [('id', '!=', survey.id), ('title', '=', survey.title),
                                             ('state', '=', 'open')])
                                        if already_exists:
                                            raise UserError(
                                                _("Duplicate Survey is not Allowed. Survey already exists with: \n Title = ' %s '" % (
                                                    already_exists.title)))
                                        survey_question_ids = self.env['survey.question'].search(
                                            [('survey_id', '=', survey.id)])
                                        if faculty_id:
                                            vals = {
                                                'survey_id': survey.id,
                                                'input_type': 'link',
                                                'partner_id': faculty_id.faculty_staff_id.user_partner_id.id,
                                                'email': faculty_id.faculty_staff_id.user_partner_id.email,
                                                'deadline': self.template.end_date,
                                                'question_ids': survey_question_ids,
                                            }
                                            self.env['survey.user_input'].sudo().create(vals)
                                        survey.state = 'open'

                    elif self.template_seq_no == 'Temp/0010' or self.template_seq_no == 'Temp/0011':
                        if self.faculty_institute_id:
                            self.template.institute_id = self.faculty_institute_id
                            self.template.campus_id = self.faculty_institute_id.campus_id
                        elif self.institute_id:
                            self.template.institute_id = self.institute_id
                            self.template.campus_id = self.institute_id.campus_id
                        survey = self.template.copy(None)

                        already_exists = self.env['survey.survey'].sudo().search(
                            [('id', '!=', survey.id), ('title', '=', survey.title),
                             ('state', '=', 'open')])
                        if already_exists:
                            raise UserError(
                                _("Duplicate Survey is not Allowed. Survey already exists with: \n Title = ' %s '" % (
                                    already_exists.title)))
                        survey.template_seq_no = self.template_seq_no
                        survey_question_ids = self.env['survey.question'].search(
                            [('survey_id', '=', survey.id)])
                        for faculty_id in self.template.institute_id.faculty_ids:
                            vals = {
                                'survey_id': survey.id,
                                'input_type': 'link',
                                'partner_id': faculty_id.employee_id.user_partner_id.id,
                                'email': faculty_id.employee_id.user_partner_id.email,
                                'deadline': self.template.end_date,
                                'question_ids': survey_question_ids,
                            }
                            self.env['survey.user_input'].sudo().create(vals)
                        survey.state = 'open'

                    self.template.start_date = False
                    self.template.end_date = False
                    self.template.class_id = False
                    self.template.primary_class_id = False
                    self.template.faculty_staff_id = False
                    self.template.term_id = False
                    self.template.institute_id = False
                    self.template.department_id = False
                    self.template.batch_id = False
                    self.template.section_id = False
