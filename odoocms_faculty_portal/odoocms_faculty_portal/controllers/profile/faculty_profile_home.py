import base64
import json

from odoo import http
from odoo.http import request
import pdb
from .. import main


class FacultyProfile(http.Controller):
    @http.route(['/faculty/profile'], type='http', auth="user", website=True)
    def profileHome(self, **kw):
         try:
             values, success, faculty_staff = main.prepare_portal_values(request)
             if not success:
                 return request.render("odoocms_web.portal_error", values)
             employed_from = request.env['odoocms.hr.emp.rec.master'].sudo().search([('faculty_staff_id', '=', faculty_staff.id),('hr_emp_action_type','=','NEJ')], order='hr_emp_eff_dt desc', limit=1)
             values.update({
                 #'class_ids' : class_ids,
                 'active_menu': 'profile',
                 'employed_from': employed_from
             })
             return http.request.render('odoocms_faculty_portal.faculty_portal_profile_page',values)
         except Exception as e:
             values = {
                 'error_message': e or False
             }
             return http.request.render('odoocms_web.portal_error', values)

    @http.route(['/faculty/profile/update/save'], type='http', method=['POST'], auth="user", website=True, csrf=False)
    def profileHomeUpdateSave(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:

                return request.render("odoocms_faculty_portal.faculty_error", values)

            personal_data = {
                'confirmation': True if kw.get('consent') == 'on' else False,
                'mobile_phone': kw.get('mobile_phone'),
                'work_email': kw.get('work_email'),
                'twitter_fms': kw.get('twitter_fms'),
                'skype_fms': kw.get('skype_fms'),
                'linkedin_fms': kw.get('linkedin_fms'),
                'facebook_fms': kw.get('facebook_fms'),
                'google_fms': kw.get('google_fms'),
                'blood_group': kw.get('blood_group'),
                'cnic_no_fms': kw.get('cnic_no_fms'),
                'domocile_fms': kw.get('domocile_fms'),
                'nust_campus_fms': kw.get('nust_campus_fms'),
                'father_name': kw.get('father_name'),
                'father_cnic': kw.get('father_cnic'),
                'father_address': kw.get('father_address'),
                'date_of_birth': kw.get('date_of_birth'),
                'gender': kw.get('gender'),
                'religion': kw.get('religion'),
                'sect_fms': kw.get('sect_fms'),
                'father_profession': kw.get('father_profession'),
                'father_status': kw.get('father_status'),
            }

            faculty_staff.sudo().write(personal_data)

            data = {
                'status_is': 'Success',
            }
            data = json.dumps(data)
            return data

        except Exception as e:
            data = {
                'status_is': 'Error',
                'error_message': e.args[0] or False
            }
            data = json.dumps(data)
            return data

