from datetime import date
from odoo import http
from .. import main
import pdb
from odoo.exceptions import UserError
from odoo.http import content_disposition, Controller, request, route
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.tools.translate import _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

import logging
_logger = logging.getLogger(__name__)
class Exams_portal_results(http.Controller):

    @http.route(['/faculty/grade/sheet/report/download/'], method=['POST'], csrf=False, type='http', auth="user", website=True)
    def fac_final_grade_report_download(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            report_type = "pdf"
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            # dmc = http.request.env['odoocms.student'].sudo().search([('id', '=', student.id)])
            if faculty_staff:
                batch_id = int(kw.get('grade_class_batch_id'))
                batch_name = kw.get('grade_class_batch_name')
                term_id = int(kw.get('grade_class_term_id'))
                term_name = kw.get('grade_class_term_name')
                primary_class_id = int(kw.get('grade_class_primary_class_id'))
                primary_class_name = kw.get('grade_class_primary_class_name')
                # {'id': 5, 'batch_id': (2907, 'PNEC/GL-2015B(MECH)'), 'term_id': (5, 'Fall 2020'),
                #  'primary_class_id': (60985, 'ME499-PNEC/GL-2015B(MECH)-0268-1162-Final Year Project')
                datas = {

                    'ids': [],
                    'form': {'id': faculty_staff.id, 'batch_id':(batch_id, batch_name), 'term_id': (term_id, term_name), 'primary_class_id': (primary_class_id, primary_class_name)}
                }

                pdf = request.env.ref('reports_nust_ext.action_report_grade_sheet').sudo().render_qweb_pdf([faculty_staff.id], datas)[0]
                pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
                return request.make_response(pdf, headers=pdfhttpheaders)
            else:
                return request.redirect('/')
            #return self.ref('reports_nust_ext.action_report_grade_sheet').report_action(self, data=datas,config=False)
        except Exception as e:
            print(e)
            data = {
                # 'student_id': student.id,
                'name': 'Grade Report',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_web.portal_error', values)

    @http.route(['/faculty/final/marksheet/report/download/'], method=['POST'], csrf=False, type='http', auth="user",
                website=True)
    def fac_final_marksheet_report_download(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            report_type = "pdf"
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            # dmc = http.request.env['odoocms.student'].sudo().search([('id', '=', student.id)])
            if faculty_staff:
                batch_id = int(kw.get('grade_class_batch_id'))
                batch_name = kw.get('grade_class_batch_name')
                term_id = int(kw.get('grade_class_term_id'))
                term_name = kw.get('grade_class_term_name')
                primary_class_id = int(kw.get('grade_class_primary_class_id'))
                primary_class_name = kw.get('grade_class_primary_class_name')
                institute_id = int(kw.get('grade_class_institute_id'))
                institute_name = kw.get('grade_class_institute_name')
                t_class_id = request.env['fin.marks.sheet.report.xls'].sudo().search([
                    ('primary_class_id', '=', primary_class_id), ('batch_id', '=', batch_id),
                    ('institute_id', '=', institute_id), ('term_id', '=', term_id)
                ])
                # {'id': 5, 'batch_id': (2907, 'PNEC/GL-2015B(MECH)'), 'term_id': (5, 'Fall 2020'),
                #  'primary_class_id': (60985, 'ME499-PNEC/GL-2015B(MECH)-0268-1162-Final Year Project')
                data = {
                    'institute_id': institute_id,
                    'batch_id': batch_id,
                    'term_id': term_id,
                    'primary_class_id': primary_class_id,
                    # 'institute_id': 26,
                    # 'batch_id': 3587,
                    # 'term_id': 5,
                    # 'primary_class_id': 62456,
                }
                # datas = {
                #
                #     'ids': [],
                #     'form': {'id': faculty_staff.id, 'batch_id': (batch_id, batch_name),
                #              'term_id': (term_id, term_name),
                #              'primary_class_id': (primary_class_id, primary_class_name)}
                # }

                p_class_id = request.env['fin.marks.sheet.report.xls'].sudo().create(data)

                if not p_class_id:
                    values = {
                        'header': 'Error!',
                        'message': 'Nothing Found!',
                    }
                    return 'Error'

                if p_class_id:
                    file_data = p_class_id.make_excel(portal=True)

                    filename = (primary_class_name or 'report') + '.xls'

                    return http.send_file(file_data, filename=filename, as_attachment=True, cache_timeout=20)
        except Exception as e:
            print(e)
            data = {
                # 'student_id': student.id,
                'name': 'Final Mark Sheet Report',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_web.portal_error', values)

    @http.route(['/faculty/clo/attainment/report/download/'], method=['POST'], csrf=False, type='http', auth="user",
                website=True)
    def fac_clo_attainment_report_download(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            report_type = "pdf"
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            # dmc = http.request.env['odoocms.student'].sudo().search([('id', '=', student.id)])
            if faculty_staff:
                primary_class_id = int(kw.get('grade_class_primary_class_id'))
                primary_class_name = kw.get('grade_class_primary_class_name')
                primary_class=request.env['odoocms.class.primary'].sudo().search([('id','=',primary_class_id)])
                data = {
                    'primary_class_ids': primary_class,
                }
                p_class_id = request.env['obe.clo.attainment.detail.new'].sudo().create(data)
                if not p_class_id:
                    values = {
                        'header': 'Error!',
                        'message': 'Nothing Found!',
                    }
                    return 'Error'

                if p_class_id:
                    file_data = p_class_id.make_excel(portal=True)

                    filename = (primary_class_name or 'report') + '.xls'

                    return http.send_file(file_data, filename=filename, as_attachment=True, cache_timeout=20)
        except Exception as e:
            print(e)
            data = {
                # 'student_id': student.id,
                'name': 'CLO Attainment Report',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_web.portal_error', values)

    @http.route(['/faculty/plo/attainment/report/download/'], method=['POST'], csrf=False, type='http', auth="user",
                website=True)
    def fac_plo_attainment_report_download(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            report_type = "pdf"
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            # dmc = http.request.env['odoocms.student'].sudo().search([('id', '=', student.id)])
            if faculty_staff:
                primary_class_id = int(kw.get('grade_class_primary_class_id'))
                primary_class_name = kw.get('grade_class_primary_class_name')
                primary_class = request.env['odoocms.class.primary'].sudo().search([('id', '=', primary_class_id)])
                data = {
                    'primary_class_ids': primary_class,
                }
                p_class_id = request.env['obe.plo.attainment.detail.new'].sudo().create(data)
                if not p_class_id:
                    values = {
                        'header': 'Error!',
                        'message': 'Nothing Found!',
                    }
                    return 'Error'

                if p_class_id:
                    file_data = p_class_id.make_excel(portal=True)

                    filename = (primary_class_name or 'report') + '.xls'

                    return http.send_file(file_data, filename=filename, as_attachment=True, cache_timeout=20)
        except Exception as e:
            print(e)
            data = {
                # 'student_id': student.id,
                'name': 'PLO Attainment Report',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_web.portal_error', values)
    # def fac_final_grade_report_download(self, id=0, **kw):
    #     report_type = "pdf"
    #     # id = int(kw.get('survey_id'))
    #     # fac = int(kw.get('faculty_staff_id'))
    #     values, success, faculty_staff = main.prepare_portal_values(request)
    #     if not success:
    #         return request.render("odoocms_student_portal.student_error", values)
    #     report = http.request.env['odoocms.class.primary'].sudo().search(
    #         [('id', '=', id)])
    #     report = http.request.env['grade.sheet.report.wizard'].sudo().search(
    #         [('id', '=', id)])
    #
    #
    #     return self._show_report(model=report, report_type=report_type, report_ref='reports_nust_ext.action_report_grade_sheet', download="download")

