from odoo import models, fields, _, api
from odoo.exceptions import UserError
import pdb


class SurveysTemplate(models.TransientModel):
    _name = 'survey.wizard_sada'
    _description = 'Survey Creation Wizard For SADA'

    template = fields.Many2one(comodel_name='survey.survey', string='Template', required=True,
                               domain=[('type', '=', 'template')], )
    template_seq_no = fields.Char(related='template.template_seq_no', string='Template ID', required=False, )
    survey_form_type = fields.Many2one(related='template.survey_form_type', string='Form Types')
    survey_form_type_name = fields.Char(related='survey_form_type.name', string='Form Types Name', required=False, )
    # For SADA
    faculty_staff_id = fields.Many2one('odoocms.faculty.staff', string='Faculty')
    student_id = fields.Many2one('odoocms.student', string='Student')
    class_id = fields.Many2one('odoocms.class', string='Class', )

    course_detail_line = fields.One2many('survey.wizard_sada.line', 'course_detail', string='Detail')

    campus_id = fields.Many2one(comodel_name='odoocms.campus', string='Campus',
                                required=False, )
    institute_id = fields.Many2one(comodel_name='odoocms.institute', string='School', required=False, )

    career_id = fields.Many2one(comodel_name='odoocms.career', string='Academic Level', required=False, )

    department_id = fields.Many2one(comodel_name='odoocms.department', string='Department', required=False, )

    program_id = fields.Many2one(comodel_name='odoocms.program', string='Program', required=False, )

    start_date = fields.Datetime(string="Start Date", required=True, default=fields.Datetime.now, )
    end_date = fields.Datetime(string="End Date", required=True, default=fields.Datetime.now, )

    term_id = fields.Many2one('odoocms.academic.term', string='Academic Term')
    primary_class_id = fields.Many2one(comodel_name='odoocms.class.primary', string='Primary Class', )
    section_id = fields.Many2one('odoocms.batch.section', string='Section', )

    def create_survey_form(self):
        for rec in self:
            if rec.template:
                self.template.start_date = self.start_date
                self.template.end_date = self.end_date
                self.template.survey_form_type = self.survey_form_type
                self.template.institute_id = self.institute_id
                if rec.class_id:
                    if self.template_seq_no == 'Temp/0001' or self.template_seq_no == 'Temp/0002' \
                            or self.template_seq_no == 'Temp/0004' or self.template_seq_no == 'Temp/0008' \
                            or self.template_seq_no == 'Temp/0005':
                        self.template.section_id = self.section_id
                        for course_detail in self.course_detail_line:
                            self.template.faculty_staff_id = course_detail.faculty_staff_id
                            self.template.class_id = rec.class_id
                            self.template.term_id = rec.term_id
                            # self.template.batch_id = rec.class_id.batch_id
                            # self.template.department_id = rec.class_id.batch_id.department_id
                            # self.template.institute_id = rec.class_id.batch_id.institute_id

                            survey = self.template.copy(None)

                            survey.batch_id = rec.class_id.batch_id
                            survey.department_id = rec.class_id.batch_id.department_id
                            survey.institute_id = rec.class_id.batch_id.institute_id
                            survey.term_id = rec.class_id.term_id

                            already_exists = self.env['survey.survey'].sudo().search(
                                [('id', '!=', survey.id), ('title', '=', survey.title),
                                 ('state', '=', 'open')])
                            if already_exists:
                                raise UserError(
                                    _("Duplicate Survey is not Allowed. Survey already exists with: \n Title = ' %s '" % (
                                        already_exists.title)))
                            if course_detail.faculty_staff_id:
                                survey.title = survey.title + '-' + course_detail.faculty_staff_id.name

                            already_exists = self.env['survey.survey'].sudo().search(
                                [('id', '!=', survey.id), ('title', '=', survey.title),
                                 ('state', '=', 'open')])
                            for record in already_exists:
                                if record:
                                    raise UserError(
                                        _("Duplicate Survey is not Allowed. Survey already exists with: \n Title = ' %s '" % (
                                            record.title)))

                            survey.template_seq_no = self.template_seq_no
                            survey_question_ids = self.env['survey.question'].search(
                                [('survey_id', '=', survey.id)])
                            # for student in rec.course_detail_line.sudo().student_course_comp_ids:
                            for student in course_detail.sudo().student_course_comp_ids:
                                if student:
                                    vals = {
                                        'survey_id': survey.id,
                                        'input_type': 'link',
                                        'partner_id': student.student_id[0].partner_id.id,
                                        'email': student.student_id[0].user_id.login,
                                        'deadline': self.template.end_date,
                                        'question_ids': survey_question_ids,
                                    }
                                    self.env['survey.user_input'].sudo().create(vals)
                                    survey.state = 'open'

            self.template.start_date = False
            self.template.end_date = False
            self.template.class_id = False
            self.template.primary_class_id = False


class SurveysDetailTemplate(models.TransientModel):
    _name = 'survey.wizard_sada.line'
    _description = 'Survey Creation For SADA Details'

    course_detail = fields.Many2one('survey.wizard_sada', string='Detail')
    faculty_staff_id = fields.Many2one('odoocms.faculty.staff', string='Faculty')
    class_id = fields.Many2one('odoocms.class', related='course_detail.class_id', string='Class', )

    student_ids = fields.Many2many('odoocms.student', 'rel_survey_student', 'survey_id', 'student_id',
                                   string='Students',
                                   required=False, )
    student_course_comp_ids = fields.Many2many('odoocms.student.course.component',
                                               'rel_survey_student_course_component', 'survey_id', 'student_id',
                                               string='Courses Students',
                                               required=False, )