from odoo import models, fields, _, api
from odoo.exceptions import UserError
import pdb


class SurveysTemplate(models.TransientModel):
    _name = 'survey.sada.class_audit'
    _description = 'Class Audit Creation Wizard For SADA'

    template = fields.Many2one(comodel_name='survey.survey', string='Template', required=True,
                               domain=[('type', '=', 'template')], )
    template_seq_no = fields.Char(related='template.template_seq_no', string='Template ID', required=False, )
    survey_form_type = fields.Many2one(related='template.survey_form_type', string='Form Types')
    survey_form_type_name = fields.Char(related='survey_form_type.name', string='Form Types Name', required=False, )
    # For SADA
    faculty_staff_id = fields.Many2one('odoocms.faculty.staff', string='Faculty')
    student_id = fields.Many2one('odoocms.student', string='Student')
    class_id = fields.Many2one('odoocms.class', string='Class', )

    course_detail_line = fields.One2many('survey.sada.class_audit.line', 'course_detail', string='Detail')

    campus_id = fields.Many2one(comodel_name='odoocms.campus', string='Campus',
                                required=False, )
    institute_id = fields.Many2one(comodel_name='odoocms.institute', string='School', required=False, )

    career_id = fields.Many2one(comodel_name='odoocms.career', string='Academic Level', required=False, )

    department_id = fields.Many2one(comodel_name='odoocms.department', string='Department', required=False, )
    hod_id = fields.Many2one(comodel_name='hr.employee', string='Auditor', required=False, )
    # hod_id = fields.Many2one(comodel_name='hr.employee', related='department_id.hod_id', string='HOD', required=False, )
    program_id = fields.Many2one(comodel_name='odoocms.program', string='Program', required=False, )

    start_date = fields.Datetime(string="Start Date", required=True, default=fields.Datetime.now, )
    end_date = fields.Datetime(string="End Date", required=True, default=fields.Datetime.now, )

    term_id = fields.Many2one('odoocms.academic.term', string='Academic Term')
    primary_class_id = fields.Many2one(comodel_name='odoocms.class.primary', string='Primary Class', )
    section_id = fields.Many2one('odoocms.batch.section', string='Section', )

    def create_survey_form(self):
        for rec in self:
            if rec.template:
                rec.template.start_date = rec.start_date
                rec.template.end_date = rec.end_date
                rec.template.survey_form_type = rec.survey_form_type
                # rec.template.institute_id = rec.institute_id
                # for course_detail in rec.course_detail_line:
                if rec.course_detail_line.class_id and rec.course_detail_line.faculty_staff_id:
                    if rec.template_seq_no == 'Temp/0012':
                        if rec.institute_id and rec.department_id:
                            rec.template.institute_id = rec.institute_id
                            # rec.institute_id = rec.institute_id
                            rec.template.campus_id = rec.institute_id.campus_id
                            rec.template.department_id = rec.department_id
                            for course_detail in rec.course_detail_line:
                                survey = self.template.copy(None)

                                already_exists = self.env['survey.survey'].sudo().search(
                                    [('id', '!=', survey.id), ('title', '=', survey.title),
                                     ('state', '=', 'open')])
                                if already_exists:
                                    raise UserError(
                                        _("Duplicate Survey is not Allowed. Survey already exists with: \n Title = ' %s '" % (
                                            already_exists.title)))
                                survey.institute_id = rec.institute_id
                                survey.template_seq_no = rec.template_seq_no
                                survey.term_id = rec.term_id
                                survey.faculty_staff_id = course_detail.faculty_staff_id
                                survey.class_id = course_detail.class_id
                                if rec.department_id:
                                    survey.department_id = rec.department_id
                                if survey.class_id.code:
                                    survey.title = survey.title + ' - ' + survey.faculty_staff_id.name + ' - ' + survey.class_id.code + ' - ' + rec.term_id.code
                                else:
                                    survey.title = survey.title + ' - ' + survey.faculty_staff_id.name  + ' - ' + rec.term_id.code
                                already_exists = self.env['survey.survey'].sudo().search(
                                    [('id', '!=', survey.id), ('title', '=', survey.title),
                                     ('state', '=', 'open')])
                                if already_exists:
                                    raise UserError(
                                        _("Duplicate Survey is not Allowed. Survey already exists with: \n Title = ' %s '" % (
                                            already_exists.title)))
                                survey_question_ids = self.env['survey.question'].search(
                                    [('survey_id', '=', survey.id)])
                                if rec.hod_id:
                                    vals = {
                                        'survey_id': survey.id,
                                        'input_type': 'link',
                                        'partner_id': rec.hod_id.user_id.partner_id.id,
                                        'email': rec.hod_id.user_partner_id.email or rec.hod_id.user_id.login,
                                        'deadline': rec.template.end_date,
                                        'question_ids': survey_question_ids,
                                    }
                                    self.env['survey.user_input'].sudo().create(vals)
                                    survey.state = 'open'

                        elif rec.institute_id and not rec.department_id:
                            rec.template.institute_id = rec.institute_id
                            # rec.institute_id = rec.institute_id
                            rec.template.campus_id = rec.institute_id.campus_id
                            if rec.term_id:
                                rec.template.term_id = rec.term_id

                            # for department in rec.institute_id.department_ids:
                            #     rec.template.department_id = department
                            if not rec.template_seq_no == 'Temp/0003':
                                    for course_detail in rec.course_detail_line:
                                        survey = self.template.copy(None)

                                        already_exists = self.env['survey.survey'].sudo().search(
                                            [('id', '!=', survey.id), ('title', '=', survey.title),
                                             ('state', '=', 'open')])
                                        if already_exists:
                                            raise UserError(
                                                _("Duplicate Survey is not Allowed. Survey already exists with: \n Title = ' %s '" % (
                                                    already_exists.title)))
                                        survey.institute_id = rec.institute_id
                                        survey.template_seq_no = rec.template_seq_no
                                        survey.term_id = rec.term_id
                                        survey.faculty_staff_id = course_detail.faculty_staff_id
                                        survey.class_id = course_detail.class_id
                                        # if department:
                                        #     survey.department_id = department
                                        if survey.class_id.code:
                                            survey.title = survey.title + ' - ' + survey.faculty_staff_id.name + ' - ' + survey.class_id.code + ' - ' + rec.term_id.code
                                        else:
                                            survey.title = survey.title + ' - ' + survey.faculty_staff_id.name + ' - ' + rec.term_id.code
                                        already_exists = self.env['survey.survey'].sudo().search(
                                            [('id', '!=', survey.id), ('title', '=', survey.title),
                                             ('state', '=', 'open')])
                                        if already_exists:
                                            raise UserError(
                                                _("Duplicate Survey is not Allowed. Survey already exists with: \n Title = ' %s '" % (
                                                    already_exists.title)))
                                        survey_question_ids = self.env['survey.question'].search(
                                            [('survey_id', '=', survey.id)])
                                        if rec.hod_id:
                                            vals = {
                                                'survey_id': survey.id,
                                                'input_type': 'link',
                                                'partner_id': rec.hod_id.user_id.partner_id.id,
                                                'email': rec.hod_id.user_partner_id.email or rec.hod_id.user_id.login,
                                                'deadline': rec.template.end_date,
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

class SurveysDetailTemplate(models.TransientModel):
    _name = 'survey.sada.class_audit.line'
    _description = 'Class Audit Detail Creation For SADA'

    course_detail = fields.Many2one('survey.sada.class_audit', string='Detail')
    faculty_staff_id = fields.Many2one('odoocms.faculty.staff', string='Faculty')
    class_id = fields.Many2one('odoocms.class', string='Class Name', )

    # student_ids = fields.Many2many('odoocms.student', 'rel_survey_student', 'survey_id', 'student_id',
    #                                string='Students',
    #                                required=False, )
    # student_course_comp_ids = fields.Many2many('odoocms.student.course.component',
    #                                            'rel_survey_student_course_component', 'survey_id', 'student_id',
    #                                            string='Courses Students',
    #                                            required=False, )