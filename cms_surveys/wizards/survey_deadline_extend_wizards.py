from odoo import models, fields, _, api
from odoo.exceptions import UserError
import pdb


class SurveysTemplate(models.TransientModel):
    _name = 'survey.wizard_deadline.extend'
    _description = 'Survey Deadline Extend Wizard '

    template = fields.Many2one(comodel_name='survey.survey', string='Template', required=True,
                               domain=[('type', '=', 'template')], )
    template_seq_no = fields.Char(related='template.template_seq_no', string='Template ID', required=False, )
    survey_form_type = fields.Many2one(related='template.survey_form_type', string='Form Types')
    survey_form_type_name = fields.Char(related='survey_form_type.name', string='Form Types Name', required=False, )
    # For Survey Extend
    faculty_staff_id = fields.Many2one('odoocms.faculty.staff', string='Faculty')
    student_id = fields.Many2one('odoocms.student', string='Student')
    class_id = fields.Many2one('odoocms.class', string='Class', )

    campus_id = fields.Many2one(comodel_name='odoocms.campus', string='Campus',
                                required=False, )
    institute_id = fields.Many2one(comodel_name='odoocms.institute', string='School', required=False, )

    career_id = fields.Many2one(comodel_name='odoocms.career', string='Academic Level', required=False, )

    department_id = fields.Many2one(comodel_name='odoocms.department', string='Department', required=False, )

    program_id = fields.Many2one(comodel_name='odoocms.program', string='Program', required=False, )

    start_date = fields.Datetime(string="Start Date", required=True, default=fields.Datetime.now, )
    end_date = fields.Datetime(string="Extended Deadline", required=True, default=fields.Datetime.now, )

    term_id = fields.Many2one('odoocms.academic.term', string='Academic Term')
    primary_class_id = fields.Many2one(comodel_name='odoocms.class.primary', string='Primary Class', )
    section_id = fields.Many2one('odoocms.batch.section', string='Section', )

    def extend_survey_deadline(self):
        for rec in self:
            if rec.template:
                if self.institute_id:
                    survey_exists = self.env['survey.survey'].sudo().search(
                        [('template_seq_no', '=', self.template_seq_no), ('institute_id', '=', self.institute_id.id),
                         ('survey_form_type', '=', self.survey_form_type.id), ('title', 'ilike', self.template.display_name)])
                    # ilike
                    if survey_exists:
                        for survey in survey_exists:
                            survey.end_date = self.end_date
                            survey.state = 'open'
                    else:
                        raise UserError(
                            _("No Survey exists for Institute: \n = '%s'" % (
                                self.institute_id.name)))
