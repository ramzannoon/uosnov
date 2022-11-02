import pdb
from datetime import date
from datetime import date
from odoo import http
from .. import main
import pdb
from odoo.exceptions import UserError
from odoo.http import content_disposition, Controller, request, route
from odoo.tools.translate import _


class StudentResult(http.Controller):
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
            filename = "exam_slip.pdf"
            reporthttpheaders.append(('Content-Disposition', content_disposition(filename)))
        return request.make_response(report, headers=reporthttpheaders)

    @http.route(['/student/results'], type='http', auth="user", website=True)
    def StudentResulthome(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)

            # survey_input_ids = http.request.env['survey.user_input'].sudo().search([('partner_id', '=', values['partner'].id)])
            # if survey_input_ids:
            #     for survey in survey_input_ids:
            #         if (survey.state == 'new' or survey.state == 'skip') and survey.survey_id.state == 'open':
            #             return request.redirect('/student/qa/feedback')
            
            color = ['md-bg-deep-purple-A200','md-bg-deep-orange-600', 'md-bg-green-800','md-bg-cyan-700', 'md-bg-light-blue-600','md-bg-deep-orange-900', 'md-bg-indigo-500',  'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300','md-bg-teal-800', 'md-bg-purple-500','md-bg-pink-800','md-bg-deep-orange-A200','md-bg-brown-400']
            personal_info, date_sheet = student.get_datesheet(student.term_id.id)

            #exams = http.request.env['odoocms.student.exams'].sudo().search([('student_id','=',student.id),('id','=',id)])
            values.update({
                 'color': color,
                 'date_sheet': date_sheet or False
            })
            return http.request.render('odoocms_student_portal.student_portal_result_classes',values)
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Results',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/results/id/<int:id>'], type='http', auth="user", website=True)
    def student_result_detail(self, id=0, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            student_course = http.request.env['odoocms.student.course'].sudo().search([('student_id','=',student.id),('id','=',id)])

            if not student_course:
                values = {
                    'error_message': 'not student'
                }
                return http.request.render('odoocms_student_portal.student_error', values)
            values.update({
                'student_course': student_course,
            })
            return http.request.render('odoocms_student_portal.student_portal_result_detail',values)
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Result Selective View',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/roll/number/download/<int:id>/'], type='http', auth="user", website=True)
    def student_invoice_download(self, id=0, **kw):
        report_type = "pdf"
        values, success, student = main.prepare_portal_values(request)
        if not success:
            return request.render("odoocms_student_portal.student_error", values)

        #invoice = http.request.env['account.move'].sudo().search([('id', '=', id)])
        exam_slip = http.request.env['odoocms.student'].sudo().search([('id', '=', id)])
        id = "action_student_id_card"
        model = "odoocms.student"
        # invoice_sudo.download_time = datetime.now()
        return self._show_report(model=exam_slip, report_type=report_type, report_ref='odoocms_exam.action_report_student_exam_slip', download="download")

        # idcard download
        # id_card = http.request.env['odoocms.student'].sudo().search([('id', '=', id)])
        # id = "action_student_id_card"
        # model = "odoocms.student"
        # # invoice_sudo.download_time = datetime.now()
        # return self._show_report(model=id_card, report_type=report_type, report_ref='odoocms.action_student_id_card', download="download")