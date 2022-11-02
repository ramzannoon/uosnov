from datetime import date
from odoo import http
from . import main
import pdb
from odoo.exceptions import UserError
from odoo.http import content_disposition, Controller, request, route
from odoo.tools.translate import _

class StudentInvoices(http.Controller):
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
            filename = "invoice.pdf"
            reporthttpheaders.append(('Content-Disposition', content_disposition(filename)))
        return request.make_response(report, headers=reporthttpheaders)
    
    @http.route(['/student/invoices'], type='http', auth="user", website=True)
    def Student_Invoice(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)

            survey_input_ids = http.request.env['survey.user_input'].sudo().search([('partner_id', '=', values['partner'].id)])
            if survey_input_ids:
                for survey in survey_input_ids:
                    if (survey.state == 'new' or survey.state == 'skip') and survey.survey_id.state == 'open':
                        return request.redirect('/student/qa/feedback')
            invoices = http.request.env['account.move'].sudo().search([('student_id','=',student.id),('state','=','posted'),('invoice_payment_state','in',('unpaid','in_payment','paid'))])
            values.update({
                'invoices' : invoices,
            })
            return http.request.render('odoocms_student_portal.studentInvoices',values)
        except Exception as e:
            data = {
                #'student_id': student.id,
                'name': 'invoice',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/invoices/download/<int:id>/'], type='http', auth="user", website=True)
    def student_invoice_download(self,id=0, **kw):
        report_type = "pdf"
        values, success, student = main.prepare_portal_values(request)
        if not success:
            return request.render("odoocms_student_portal.student_error", values)

        invoice = http.request.env['account.move'].sudo().search([('id', '=', id),('student_id','=',student.id)])
        # invoice_sudo.download_time = datetime.now()
        return self._show_report(model=invoice, report_type=report_type, report_ref='odoocms_fee.action_report_student_invoice_landscape', download="download")
