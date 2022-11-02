import base64
import json

from odoo import http
from odoo.http import request
import pdb
from . import main


class FacultyProfile(http.Controller):
    @http.route(['/faculty/profile'], type='http', auth="user", website=True)
    def profileHome(self, **kw):
         try:
             values, success, faculty_staff = main.prepare_portal_values(request)
             if not success:
                 return request.render("odoocms_faculty_portal.faculty_error", values)
             
             class_ids = request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id)])
           
             values.update({
                 'class_ids' : class_ids,
                 'active_menu': 'profile',
             })
             return http.request.render('odoocms_faculty_portal.faculty_portal_profile_page',values)
         except Exception as e:
             values = {
                 'error_message': e or False
             }
             return http.request.render('odoocms_faculty_portal.faculty_error', values)

    @http.route('/faculty/picture/upload', type='http', auth="user", methods=['POST'], website=True, csrf=False)
    def image_handle_faculty_upload(self, **post):
        try:
            post_file = []  # List of file to add to ir_attachment once we have the ID
            post_description = []  # Info to add after the message
            values = {}

            for field_name, field_value in post.items():
               if hasattr(field_value, 'filename'):
                    post_file.append(field_value)

            Forum = request.registry['forum.forum']
            for field_value in post_file:
                attachment_value = {
                    'name': field_value.filename,
                    'res_name': field_value.filename,
                    'res_model': 'forum.forum',
                    'res_id': Forum.id,
                    'datas': base64.encodebyte(field_value.read()),
                    'datas_fname': field_value.filename,
                }
                request.registry['ir.attachment'].sudo().create(request.cr, attachment_value, context=request.context)
            return http.route('/faculty/profile')
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)

    @http.route(['/faculty/profile/update'], type='http', method=['POST'], auth="user", website=True, csrf=False)
    def profileHomeUpdate(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)

            personal_data = {
                'mobile_phone': kw.get('f_phone'),
                'work_email': kw.get('f_work_email'),
                'twitter_fms': kw.get('f_twitter_fms'),
                'skype_fms': kw.get('f_skype_fms'),
                'linkedin_fms': kw.get('f_linkedIn'),
                'facebook_fms': kw.get('f_facebook_fms'),
                'google_fms': kw.get('f_google_fms'),
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
                'status_is':'Error',
                'error_message': e.args[0] or False
                }
            data = json.dumps(data)
            return data

    @http.route(['/faculty/profile/passport'], type='http', auth="user", website=True)
    def profilePassport(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
            class_ids = request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id)])
            
            values.update({
                'class_ids': class_ids,
                'active_menu': 'profile',
            })
            return http.request.render('odoocms_faculty_portal.faculty_portal_passport', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)

    @http.route(['/faculty/profile/scholar'], type='http', auth="user", website=True)
    def profileScholar(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
            class_ids = request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id)])
            
            values.update({
                'class_ids': class_ids,
                'active_menu': 'profile',
            })
            return http.request.render('odoocms_faculty_portal.faculty_portal_scholar', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)

    @http.route(['/faculty/profile/award'], type='http', auth="user", website=True)
    def profileAwards(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
            class_ids = request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id)])
            
            values.update({
                'class_ids': class_ids,
                'active_menu': 'profile',
            })
            return http.request.render('odoocms_faculty_portal.faculty_portal_award', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)

    @http.route(['/faculty/profile/nok'], type='http', auth="user", website=True)
    def profileNok(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
            class_ids = request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id)])
            
            values.update({
                'class_ids': class_ids,
                'active_menu': 'profile',
            })
            return http.request.render('odoocms_faculty_portal.faculty_portal_nok', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)

    @http.route(['/faculty/profile/training'], type='http', auth="user", website=True)
    def profileTraining(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
            class_ids = request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id)])
            
            values.update({
                'class_ids': class_ids,
                'active_menu': 'profile',
            })
            return http.request.render('odoocms_faculty_portal.faculty_portal_training', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)

    @http.route(['/faculty/profile/collaboration'], type='http', auth="user", website=True)
    def profileCollaboration(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
            class_ids = request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id)])
            
            values.update({
                'class_ids': class_ids,
                'active_menu': 'profile',
            })
            return http.request.render('odoocms_faculty_portal.faculty_portal_collaboration', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)

    @http.route(['/faculty/profile/experience'], type='http', auth="user", website=True)
    def profileExperience(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
            class_ids = request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id)])
            
            values.update({
                'class_ids': class_ids,
                'active_menu': 'profile',
            })
            return http.request.render('odoocms_faculty_portal.faculty_portal_experience', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)

    @http.route(['/faculty/profile/project'], type='http', auth="user", website=True)
    def profileProject(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
            class_ids = request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id)])
            
            values.update({
                'class_ids': class_ids,
                'active_menu': 'profile',
            })
            return http.request.render('odoocms_faculty_portal.faculty_portal_project', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)

    @http.route(['/faculty/profile/family'], type='http', auth="user", website=True)
    def profileFamily(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
            class_ids = request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id)])
            
            values.update({
                'class_ids': class_ids,
                'active_menu': 'profile',
            })
            return http.request.render('odoocms_faculty_portal.faculty_portal_family', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)

    @http.route(['/faculty/profile/certification'], type='http', auth="user", website=True)
    def profileQualification(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
            class_ids = request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id)])
            
            values.update({
                'class_ids': class_ids,
                'active_menu': 'profile',
            })
            return http.request.render('odoocms_faculty_portal.faculty_portal_certification', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)

    @http.route(['/faculty/profile/courses/taught'], type='http', auth="user", website=True)
    def profileTaught(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
            class_ids = request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id)])
            
            values.update({
                'class_ids': class_ids,
                'active_menu': 'profile',
            })
            return http.request.render('odoocms_faculty_portal.faculty_portal_courses_taught', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)

    @http.route(['/faculty/profile/defence'], type='http', auth="user", website=True)
    def profileDefence(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
            class_ids = request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id)])
            
            values.update({
                'class_ids': class_ids,
                'active_menu': 'profile',
            })
            return http.request.render('odoocms_faculty_portal.faculty_portal_courses_defence', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)

    @http.route(['/faculty/profile/skill'], type='http', auth="user", website=True)
    def profileSkill(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
            class_ids = request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id)])
            
            values.update({
                'class_ids': class_ids,
                'active_menu': 'profile',
            })
            return http.request.render('odoocms_faculty_portal.faculty_portal_courses_skill', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)

    @http.route(['/faculty/profile/prof/reg'], type='http', auth="user", website=True)
    def profilePReg(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
            class_ids = request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id)])
            
            values.update({
                'class_ids': class_ids,
                'active_menu': 'profile',
            })
            return http.request.render('odoocms_faculty_portal.faculty_portal_courses_p_reg', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)

    @http.route(['/faculty/profile/hec'], type='http', auth="user", website=True)
    def profileHec(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
            class_ids = request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id)])
            
            values.update({
                'class_ids': class_ids,
                'active_menu': 'profile',
            })
            return http.request.render('odoocms_faculty_portal.faculty_portal_courses_hec', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)

    @http.route(['/faculty/profile/acad'], type='http', auth="user", website=True)
    def profileAcad(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
            class_ids = request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id)])
            
            values.update({
                'class_ids': class_ids,
                'active_menu': 'profile',
            })
            return http.request.render('odoocms_faculty_portal.faculty_portal_courses_acad', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)