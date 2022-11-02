from datetime import date
from odoo import http
from .. import main
import pdb
from odoo.exceptions import UserError
from odoo.http import content_disposition, Controller, request, route
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.tools.translate import _


class StudentTranscript(CustomerPortal):
    @http.route(['/student/unofficial/transcript/download/'], type='http', auth="user", website=True)
    def student_unofficial_transcript_download(self, id=0, **kw):
        report_type = "docp"
        values, success, student = main.prepare_portal_values(request)
        if not success:
            return request.render("odoocms_student_portal.student_error", values)
        return self._show_report(model=student, report_type=report_type, report_ref='odoocms_exam.action_report_student_transcript_docp', download="download")
