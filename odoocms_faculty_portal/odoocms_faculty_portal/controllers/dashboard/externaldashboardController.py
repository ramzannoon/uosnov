import json
from datetime import date
from .. import main
from odoo import http
from odoo.http import request
import pdb


class ExternalDashboard(http.Controller):
    @http.route(['/external/dashboard'], type='http', auth="user", website=True, method=['GET', 'POST'])
    def f_dashboard(self, **kw):
        try:

            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_web.portal_error", values)
            #journal_publication_data = request.env['odoocms.nrp.publications.journal'].sudo().search([('faculty_staff_id', '=', faculty_staff.id), ('state', 'in', ['l20'])])
            #conference_publication_data = request.env['odoocms.nrp.publications.conference'].sudo().search([('faculty_staff_id', '=', faculty_staff.id), ('state', 'in', ['l20'])])
            #editorial_publication_data = request.env['odoocms.nrp.publications.editorial'].sudo().search([('faculty_staff_id', '=', faculty_staff.id), ('state', 'in', ['l20'])])
            #training_publication_data = request.env['odoocms.nrp.training'].sudo().search([('faculty_staff_id', '=', faculty_staff.id), ('state', 'in', ['l20'])])
            #intellectual_publication_data = request.env['odoocms.nrp.intellectual'].sudo().search([('faculty_staff_id', '=', faculty_staff.id), ('state', 'in', ['l20'])])
            #project_publication_data = request.env['odoocms.nrp.project'].sudo().search([('faculty_staff_id', '=', faculty_staff.id), ('state', 'in', ['l20'])])

            #journal_p_total_count, conference_p_total_count, editorial_p_total_count, training_p_total_count, project_p_total_count, intellectual_p_total_count = len(journal_publication_data), len(conference_publication_data), len(editorial_publication_data), len(training_publication_data), len(project_publication_data), len(intellectual_publication_data)
            today_classes = http.request.env['odoocms.class.attendance'].sudo().search([('faculty_id', '=', faculty_staff.id), ('date_class', '=', date.today())])
            lectures = http.request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id), ('term_id', '=', values['config_term']), ('component_id.name', 'in', ['lecture'])])
            labs = http.request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id), ('term_id', '=', values['config_term']), ('component_id.name', 'in', ['lab'])])
            #publications = journal_p_total_count + conference_p_total_count + editorial_p_total_count

            values.update({
                'lectures': len(lectures) or 0,
                'labs': len(labs) or 0,
                'workload': len(lectures) + len(labs),
                'today_classes': today_classes,
                #'publications': publications,
                'active_menu': 'dashboard',
                #'journal_p_total_count': journal_p_total_count,
                #'conference_p_total_count': conference_p_total_count,
                #'editorial_p_total_count': editorial_p_total_count,
                #'training_p_total_count': training_p_total_count,
                #'project_p_total_count': project_p_total_count,
                #'intellectual_p_total_count': intellectual_p_total_count
            })
            return http.request.render('odoocms_faculty_portal.external_dashboard', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_web.portal_error', values)

    # @http.route(['/faculty/dashboard/feedback/self'], type='http', auth="user", website=True, method=['GET'])
    # def faculty_self_evaluation(self, **kw):
    #     try:
    #         comments = []
    #         values, success, faculty_staff = main.prepare_portal_values(request)
    #         if not success:
    #             return request.render("odoocms_web.portal_error", values)
    #
    #         class_ids = request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id)])
    #         #  pp faculty_id._fields   to view all fields
    #         teacherEvaluations = http.request.env['survey.survey'].sudo().search([
    #             ('faculty_staff_id', '=', faculty_staff.id), ('survey_form_type', '=', 6), ('state', '!=', 'draft')])
    #
    #         for teacherEvaluation in teacherEvaluations:  # ,order='write_date desc',limit=1    for limiting and getting latest record
    #             teacherEvaluation.prepare_result(http.request.env['survey.question'].sudo().search([('survey_id', '=', teacherEvaluation.id), ('question_type', '=', 'matrix')]), current_filters=False)
    #
    #             # teacherEvaluations = http.request.env['survey.survey'].sudo().search([('faculty_staff_id', '=', faculty.id), ('survey_form_type', '=', 2), ('state', '!=', 'draft')],limit=1)
    #             courseEvaluations_questions = http.request.env['survey.question'].sudo().search([('survey_id', '=', teacherEvaluation.id), ('question_type', '=', 'free_text')])
    #
    #             # courseEvaluations_question = http.request.env['survey.quesion'].sudo().search([('survey_id', '=', courseEvaluation.id)])
    #             for courseEvaluations_question in courseEvaluations_questions:
    #                 for user_input_id in teacherEvaluation.user_input_ids:
    #                     courseEvaluations_user_input = http.request.env['survey.user_input_line'].sudo().search([('survey_id', '=', teacherEvaluation.id), ('question_id', '=', courseEvaluations_question.id), ('user_input_id', '=', user_input_id.id)])
    #                     if not courseEvaluations_user_input.value_free_text == 'false':
    #                         comments.append({'id': teacherEvaluation.class_id.code, 'comments': courseEvaluations_user_input.value_free_text})
    #         courses = []
    #         drill = []
    #         summary = []
    #
    #         for course in teacherEvaluations:
    #             courses.append({'name': course.class_id.code, 'data': [{'y': course.weighted_avg, 'drilldown': course.class_id.code, 'name': course.class_id.code}]})
    #             scaleData = [['Excellent', course.excellent], ['Very Good', course.vgood], ['Good', course.good], ['Average', course.avg], ['Poor', course.poor]]
    #             drill.append({'name': course.class_id.code, 'id': course.class_id.code, 'data': scaleData})
    #             summary.append({'id': course.class_id.code, 'weightage': course.weighted_avg, 'rating': course.rating})
    #
    #         data = {
    #             'series': courses,
    #             'dr': drill,
    #             'summary': summary,
    #             'comments': comments,
    #         }
    #
    #     except Exception as e:
    #         data = {
    #             'message': e or False
    #         }
    #
    #     data = json.dumps(data)
    #     return data
    #
    # @http.route(['/faculty/dashboard/feedback/course'], type='http', auth="user", website=True, method=['GET'])
    # def faculty_course_evaluation(self, **kw):
    #     try:
    #         comments = []
    #         values, success, faculty_staff = main.prepare_portal_values(request)
    #         if not success:
    #             return request.render("odoocms_web.portal_error", values)
    #
    #         class_ids = request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id)])
    #         #  pp faculty_id._fields   to view all fields
    #         courseEvaluations = http.request.env['survey.survey'].sudo().search([('faculty_staff_id', '=', faculty_staff.id), ('survey_form_type', '=', 5), ('state', '!=', 'draft')])
    #         for courseEvaluation in courseEvaluations:  # ,order='write_date desc',limit=1    for limiting and getting latest record
    #             courseEvaluation.prepare_result(http.request.env['survey.question'].sudo().search([('survey_id', '=', courseEvaluation.id), ('question_type', '=', 'matrix')]), current_filters=False)
    #
    #             courseEvaluations_questions = http.request.env['survey.question'].sudo().search([('survey_id', '=', courseEvaluation.id), ('question_type', '=', 'free_text')])
    #             # courseEvaluations_question = http.request.env['survey.quesion'].sudo().search([('survey_id', '=', courseEvaluation.id)])
    #             for courseEvaluations_question in courseEvaluations_questions:
    #                 for user_input_id in courseEvaluation.user_input_ids:
    #                     courseEvaluations_user_input = http.request.env['survey.user_input_line'].sudo().search([('survey_id', '=', courseEvaluation.id), ('question_id', '=', courseEvaluations_question.id), ('user_input_id', '=', user_input_id.id)])
    #                     if not courseEvaluations_user_input.value_free_text == 'false':
    #                         comments.append({'id': courseEvaluation.class_id.code, 'comments': courseEvaluations_user_input.value_free_text})
    #
    #         courses = []
    #         drill = []
    #         summary = []
    #         # course.user_input_ids.user_input_line_ids[7].value_free_text
    #         for course in courseEvaluations:
    #             courses.append({'name': course.class_id.code, 'data': [{'y': course.weighted_avg, 'drilldown': course.class_id.code, 'name': course.class_id.code}]})
    #             scaleData = [['Excellent', course.excellent], ['Very Good', course.vgood], ['Good', course.good], ['Average', course.avg], ['Poor', course.poor]]
    #             drill.append({'name': course.class_id.code, 'id': course.class_id.code, 'data': scaleData})
    #             summary.append({'id': course.class_id.code, 'weightage': course.weighted_avg, 'rating': course.rating})
    #
    #         data = {
    #             'series': courses,
    #             'dr': drill,
    #             'summary': summary,
    #             'comments': comments,
    #         }
    #
    #     except Exception as e:
    #         data = {
    #             'message': e or False
    #         }
    #
    #     data = json.dumps(data)
    #     return data
