from odoo import http
from odoo.http import request
from . import main
import pdb


class FacultyFeedback(http.Controller):
    @http.route(['/faculty/survey'], type='http', auth="user", website=True)
    def faculty_feedback_survey(self, **kw):
        values, success, faculty_staff = main.prepare_portal_values(request)
        if not success:
            return request.render("odoocms_faculty_portal.faculty_error", values)

        partner = request.env.user.partner_id
        survey_input_ids = http.request.env['survey.user_input'].sudo().search([('partner_id', '=', partner.id)])

        teacher_evals = []
        course_evals=[]

        for survey_input in survey_input_ids.filtered(lambda l: l.survey_id.template_seq_no == 'Temp/0003' and l.survey_id.state != 'draft'):
            teacher_evals.append({'survey': survey_input.survey_id, 'token': survey_input.token, 'status': survey_input.state})
        for survey_input in survey_input_ids.filtered(lambda l: (l.survey_id.template_seq_no == 'Temp/0009' or l.survey_id.template_seq_no == 'Temp/0016') and l.survey_id.state != 'draft'):
            course_evals.append({'survey': survey_input.survey_id, 'token': survey_input.token, 'status': survey_input.state})
        for survey_input in survey_input_ids.filtered(lambda l: l.survey_id.template_seq_no == 'Temp/0012' and l.survey_id.state != 'draft'):
            class_audit_hod.append({'survey': survey_input.survey_id, 'token': survey_input.token, 'status': survey_input.state})
       
        color = ['md-bg-deep-purple-A200', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                 'md-bg-blue-grey-500', 'md-bg-deep-purple-300','md-bg-deep-orange-600',  'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400']

        values.update({
            'faculty_surveys': teacher_evals,
            'course_surveys':course_evals,
            'active_menu': 'feedback',
            'color':color,
        })
        return http.request.render('odoocms_faculty_portal.faculty_survey',values)
