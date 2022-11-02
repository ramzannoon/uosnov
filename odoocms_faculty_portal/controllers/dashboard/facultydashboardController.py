import json
from datetime import date
from .. import main
from odoo import http
from odoo.http import content_disposition, Controller, request, route
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import UserError
from odoo.tools.translate import _
import pdb


class FacultyDashboard(http.Controller):
    def _show_report(self, model, report_type, report_ref, download=False):
        if report_type not in ('html', 'pdf', 'text'):
            raise UserError(_("Invalid report type: %s") % report_type)

        report_sudo = request.env.ref(report_ref).sudo()

        if not isinstance(report_sudo, type(request.env['ir.actions.report'])):
            raise UserError(_("%s is not the reference of a report") % report_ref)

        method_name = 'render_qweb_%s' % (report_type)
        report = getattr(report_sudo, method_name)([model.id], data={'report_type': report_type})[0]
        reporthttpheaders = [
            ('Content-Type', 'application/pdf' if report_type == 'pdf' else 'text/html'),
            ('Content-Length', len(report)),
        ]
        if report_type == 'pdf' and download:
            filename = "survey_report.pdf"
            reporthttpheaders.append(('Content-Disposition', content_disposition(filename)))
        return request.make_response(report, headers=reporthttpheaders)
    @http.route(['/faculty/dashboard'], type='http', auth="user", website=True, method=['GET', 'POST'])
    def f_dashboard(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_web.portal_error", values)
            teacherEvaluationsSelfReport = http.request.env['survey.survey'].sudo().search(
                [('faculty_staff_id', '=', faculty_staff.id), ('template_seq_no', '=', 'Temp/0002'),
                 ('state', '!=', 'draft')])
            teacherEvaluationsCourseReport = http.request.env['survey.survey'].sudo().search(
                [('faculty_staff_id', '=', faculty_staff.id), ('template_seq_no', '=','Temp/0001'),
                 ('state', '!=', 'draft')])



            #journal_publication_data = request.env['odoocms.nrp.publications.journal'].sudo().search([('faculty_staff_id', '=', faculty_staff.id), ('state', 'in', ['l20'])])
            #conference_publication_data = request.env['odoocms.nrp.publications.conference'].sudo().search([('faculty_staff_id', '=', faculty_staff.id), ('state', 'in', ['l20'])])
            #editorial_publication_data = request.env['odoocms.nrp.publications.editorial'].sudo().search([('faculty_staff_id', '=', faculty_staff.id), ('state', 'in', ['l20'])])
            #training_publication_data = request.env['odoocms.nrp.training'].sudo().search([('faculty_staff_id', '=', faculty_staff.id), ('state', 'in', ['l20'])])
            #intellectual_publication_data = request.env['odoocms.nrp.intellectual'].sudo().search([('faculty_staff_id', '=', faculty_staff.id), ('state', 'in', ['l20'])])
            #project_publication_data = request.env['odoocms.nrp.project'].sudo().search([('faculty_staff_id', '=', faculty_staff.id), ('state', 'in', ['l20'])])

            #journal_p_total_count, conference_p_total_count, editorial_p_total_count, training_p_total_count, project_p_total_count, intellectual_p_total_count = len(journal_publication_data), len(conference_publication_data), len(editorial_publication_data), len(training_publication_data), len(project_publication_data), len(intellectual_publication_data)
            workload = http.request.env['odoocms.team.workload'].sudo().search([('faculty_staff_id', '=', faculty_staff.id),('term_id','=',values['config_term'])], limit=1)
            today_classes = http.request.env['odoocms.class.attendance'].sudo().search([('faculty_id', '=', faculty_staff.id), ('date_class', '=', date.today())])
            lectures = http.request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id), ('term_id', '=', values['config_term']), ('component_id.name', 'in', ['lecture'])])
            labs = http.request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id), ('term_id', '=', values['config_term']), ('component_id.name', 'in', ['lab'])])
            #publications = journal_p_total_count + conference_p_total_count + editorial_p_total_count

            values.update({
                'lectures': len(lectures) or 0,
                'labs': len(labs) or 0,
                'workload': workload,
                'today_classes': today_classes,
                'teacherEvaluationsSelfReport': teacherEvaluationsSelfReport,
                'teacherEvaluationsCourseReport': teacherEvaluationsCourseReport,
                #'publications': publications,
                'active_menu': 'dashboard',
                #'journal_p_total_count': journal_p_total_count,
                #'conference_p_total_count': conference_p_total_count,
                #'editorial_p_total_count': editorial_p_total_count,
                #'training_p_total_count': training_p_total_count,
                #'project_p_total_count': project_p_total_count,
                #'intellectual_p_total_count': intellectual_p_total_count
            })
            return http.request.render('odoocms_faculty_portal.faculty_dashboard_new', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_web.portal_error', values)

    @http.route(['/faculty/dashboard/feedback/self'], type='http', auth="user", website=True, method=['GET'])
    def faculty_self_evaluation(self, **kw):
        try:
            comments_fac_feed = []
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_web.portal_error", values)
            teacherEvaluations = http.request.env['survey.survey'].sudo().search([('faculty_staff_id', '=', faculty_staff.id), ('template_seq_no', '=', 'Temp/0002'), ('state', '!=', 'draft')])
            for teacherEvaluation in teacherEvaluations:  # ,order='write_date desc',limit=1    for limiting and getting latest record
                teacherEvaluation.prepare_result(http.request.env['survey.question'].sudo().search([('survey_id', '=', teacherEvaluation.id), ('question_type', '=', 'matrix')]), current_filters=False)
                # teacherEvaluations = http.request.env['survey.survey'].sudo().search([('faculty_staff_id', '=', faculty.id), ('survey_form_type', '=', 2), ('state', '!=', 'draft')],limit=1)
                courseEvaluations_questions = http.request.env['survey.question'].sudo().search([('survey_id', '=', teacherEvaluation.id), ('question_type', '=', 'free_text')])
                # courseEvaluations_question = http.request.env['survey.quesion'].sudo().search([('survey_id', '=', courseEvaluation.id)])
                for courseEvaluations_question in courseEvaluations_questions:
                    for user_input_id in teacherEvaluation.user_input_ids:
                        if user_input_id.state == 'done':
                            courseEvaluations_user_input = http.request.env['survey.user_input_line'].sudo().search([('survey_id', '=', teacherEvaluation.id), ('question_id', '=', courseEvaluations_question.id), ('user_input_id', '=', user_input_id.id)])
                            if not courseEvaluations_user_input.value_free_text == 'false':
                                comments_fac_feed.append({'id': teacherEvaluation.title, 'title': teacherEvaluation.title, 'comments': courseEvaluations_user_input.value_free_text})
            courses = []
            drill = []
            summary = []
            for course in teacherEvaluations:

                courses.append({'name': course.title, 'title': course.title, 'data': [{'y': course.weighted_avg, 'drilldown': course.title, 'name': course.title, 'title': course.title}]})
                scaleData = [['Excellent', course.excellent], ['Very Good', course.vgood], ['Good', course.good], ['Average', course.avg], ['Poor', course.poor]]
                drill.append({'name': course.title, 'id': course.title, 'title': course.title, 'data': scaleData})
                summary.append({'id': course.title, 'title': course.title, 'total_registered':course.answer_count, 'answeres': course.answer_done_count, 'weightage': course.weighted_avg, 'rating': course.rating})

            data = {
                'series': courses,
                'dr': drill,
                'summary': summary,
                'comments_fac_feed': comments_fac_feed,
            }
        except Exception as e:
            data = {
                'message': e or False
            }

        data = json.dumps(data)
        return data

    @http.route(['/faculty/dashboard/feedback/course'], type='http', auth="user", website=True, method=['GET'])
    def faculty_course_evaluation(self, **kw):
        try:
            comments_fac_course = []
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_web.portal_error", values)

            courseEvaluations = http.request.env['survey.survey'].sudo().search([('faculty_staff_id', '=', faculty_staff.id), ('template_seq_no', '=', 'Temp/0001'), ('state', '!=', 'draft')])
            for courseEvaluation in courseEvaluations:  # ,order='write_date desc',limit=1    for limiting and getting latest record
                courseEvaluation.prepare_result(http.request.env['survey.question'].sudo().search([('survey_id', '=', courseEvaluation.id), ('question_type', '=', 'matrix')]), current_filters=False)
                courseEvaluations_questions = http.request.env['survey.question'].sudo().search([('survey_id', '=', courseEvaluation.id), ('question_type', '=', 'free_text')])
                # courseEvaluations_question = http.request.env['survey.quesion'].sudo().search([('survey_id', '=', courseEvaluation.id)])
                for courseEvaluations_question in courseEvaluations_questions:
                    for user_input_id in courseEvaluation.user_input_ids:
                        if user_input_id.state == 'done':
                            courseEvaluations_user_input = http.request.env['survey.user_input_line'].sudo().search([('survey_id', '=', courseEvaluation.id), ('question_id', '=', courseEvaluations_question.id), ('user_input_id', '=', user_input_id.id)])
                            if not courseEvaluations_user_input.value_free_text == 'false':
                                comments_fac_course.append({'id': courseEvaluation.title, 'title': courseEvaluation.title, 'comments': courseEvaluations_user_input.value_free_text})
            courses = []
            drill = []
            summary = []
            # course.user_input_ids.user_input_line_ids[7].value_free_text
            for course in courseEvaluations:
                courses.append({'name': course.title, 'title': course.title, 'data': [{'y': course.weighted_avg, 'drilldown': course.title, 'title': course.title, 'name': course.title}]})
                scaleData = [['Excellent', course.excellent], ['Very Good', course.vgood], ['Good', course.good], ['Average', course.avg], ['Poor', course.poor]]
                drill.append({'name': course.title, 'id': course.title, 'data': scaleData})
                summary.append({'id': course.title, 'title': course.title, 'total_registered':course.answer_count, 'answeres': course.answer_done_count, 'weightage': course.weighted_avg, 'rating': course.rating})
            data = {
                'series': courses,
                'dr': drill,
                'summary': summary,
                'comments_fac_course': comments_fac_course,
            }
        except Exception as e:
            data = {
                'message': e or False
            }
        data = json.dumps(data)
        return data

    @http.route(['/faculty/feedback/report/p/download'], type='http', method=['POST'], csrf=False, auth="user", website=True)
    def faculty_feedback_report_p_download(self, id=0, **kw):
        report_type = "pdf"
        id = int(kw.get('survey_id'))
        fac = int(kw.get('faculty_staff_id'))
        values, success, faculty_staff = main.prepare_portal_values(request)
        if not success:
            return request.render("odoocms_student_portal.student_error", values)
        report = http.request.env['survey.survey'].sudo().search(
            [('id', '=', id),('faculty_staff_id','=',fac)])
        #invoice = http.request.env['account.move'].sudo().search([('id', '=', id), ('faculty_staff', '=', faculty_staff.id)])
        # invoice_sudo.download_time = datetime.now()
        return self._show_report(model=report, report_type=report_type,report_ref='cms_surveys.report_prepare_result', download="download")
