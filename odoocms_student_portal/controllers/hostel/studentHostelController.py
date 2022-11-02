from datetime import date
from odoo import http
from .. import main
import pdb
from odoo.exceptions import UserError
from odoo.http import content_disposition, Controller, request, route
import re
from odoo.tools.translate import _


class StudentClearance(http.Controller):
    @http.route(['/student/hostel/application'], type='http', auth="user", website=True)
    def student_hostel_app(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)

            hostel_app = http.request.env['odoocms.hostel.admission.application'].sudo().search([('student_id','=',student.id)])

            values.update({
                'active_menu': 'notifications',
                'hostel_app':hostel_app
            })
            return http.request.render('odoocms_student_portal.student_hostel_application', values)
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Hostel',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/hostel/application/save'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def student_hostel_app_save(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)

            nust_reg_date = kw.get('nust_reg_date')
            merit_no = (kw.get('merit_no'))
            orphan = (kw.get('orphan'))
            shaheed = (kw.get('shaheed'))
            house = kw.get('house')
            street = kw.get('street')
            city = kw.get('city')
            zip = (kw.get('zip'))
            father_name = (kw.get('f_name'))
            father_cnic = (kw.get('f_cnic'))
            father_occupation = (kw.get('f_occupation'))
            father_office_address = (kw.get('f_office_address'))
            father_phone = (kw.get('f_phone'))
            father_mobile = (kw.get('f_mobile'))
            father_email = (kw.get('f_email'))
            mother_mobile = (kw.get('m_mobile'))
            spouse_name = (kw.get('s_name'))
            spouse_cnic = (kw.get('s_cnic'))
            spouse_mobile = kw.get('s_mobile')
            no_of_children = (kw.get('no_of_children'))
            blood_group = (kw.get('blood_group'))
            medical_history = (kw.get('medical_history'))
            medicine = (kw.get('medicine'))
            medical_description = (kw.get('medical_description'))
            disability = (kw.get('disability'))
            data = {
                'student_id': student.id,
                #'nust_registration_date': nust_reg_date,
                'merit_no': merit_no,
                'temp_street': house,
                'temp_street2':street,
                'temp_city': city,
                'temp_zip': zip,
                'father_name':father_name,
                'occupation': father_occupation or False,
                'father_cnic': father_cnic ,
                'father_residence_phone':father_phone or False,
                'father_mobile': father_mobile or False,
                'father_email':father_email or False,
                'mother_mobile': mother_mobile or False,
                'spouse_name': spouse_name or False,
                'spouse_cnic': spouse_cnic or False,
                'spouse_mobile': spouse_mobile or False,
                'child_no':no_of_children or False,
                'blood_group':blood_group,
                'regularly_taken_medicine': medicine or False,
                'disease_detail': medical_description or False,
                'disability':bool(disability) or False,
                'orphan': bool(orphan) or False,
                'shaheed': bool(shaheed) or False,
                'any_medical_history': bool(medical_history) or False,
                'state': 'draft',
            }
            request.env['odoocms.hostel.admission.application'].sudo().create(data)
            return request.redirect('/student/hostel/application')
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Hostel Save',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/hostel/application/cancel'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def student_hostel_app_cancel(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            
            application = request.env['odoocms.hostel.admission.application'].sudo().search([('student_id','=',student.id)])
            application.sudo().unlink()
            return request.redirect('/student/hostel/application')
        except Exception as e:
            data = {
                # 'student_id': student.id,
                'name': 'Hostel Cancel',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)




