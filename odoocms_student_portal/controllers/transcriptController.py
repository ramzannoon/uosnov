from datetime import date
from odoo import http
from . import main
import pdb
from odoo.exceptions import UserError
from odoo.http import content_disposition, Controller, request, route
from odoo.tools.translate import _


class StudentTranscript(http.Controller):
    def _show_report(self, model, report_type, report_ref, download=False):
        # if report_type not in ('html', 'pdf', 'text'):
        #     raise UserError(_("Invalid report type: %s") % report_type)
        #
        report_sudo = request.env.ref(report_ref).sudo()
        #
        # if not isinstance(report_sudo, type(request.env['ir.actions.report'])):
        #     raise UserError(_("%s is not the reference of a report") % report_ref)

        method_name = 'render_qweb_doc'

        report = getattr(report_sudo, method_name)([model.id], data={'report_type': 'docp'})[0]

        reporthttpheaders = [
            ('Content-Type', 'application/pdf' if report_type == 'docp' else 'text/html'),
            ('Content-Length', report),
        ]

        if report_type == 'pdf' and download:
            filename = "transcript.pdf"
            reporthttpheaders.append(('Content-Disposition', content_disposition(filename)))
        return request.make_response(report, headers=reporthttpheaders)


    @http.route(['/student/unofficial/transcript/download/'], type='http', auth="user", website=True)
    def student_unofficial_transcript_download(self, id=0, **kw):
        report_type = "pdf"
        values, success, student = main.prepare_portal_values(request)
        if not success:
            return request.render("odoocms_student_portal.student_error", values)
        survey_input_ids = http.request.env['survey.user_input'].sudo().search([('partner_id', '=', values['partner'].id)])
        if survey_input_ids:
            for survey in survey_input_ids:
                if (survey.state == 'new' or survey.state == 'skip') and survey.survey_id.state == 'open':
                    return request.redirect('/student/qa/feedback')

        transcript = http.request.env['odoocms.student'].sudo().search([('id', '=', student.id)])

        # invoice_sudo.download_time = datetime.now()
        return self._show_report(model=transcript, report_type=report_type, report_ref='odoocms_exam.action_report_student_transcript_docp', download="download")
