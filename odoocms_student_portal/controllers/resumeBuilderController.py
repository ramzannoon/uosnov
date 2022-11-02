# import json
# from datetime import date
# from odoo import http
# from . import main
# import pdb
# from odoo.exceptions import UserError
# from odoo.http import content_disposition, Controller, request, route
# from odoo.tools.translate import _
#
#
# class StudentResumeBuilderPortal(http.Controller):
#     @http.route(['/student/resume/builder'], type='http', auth="user", website=True)
#     def student_resume_builder(self, **kw):
#         try:
#
#             values, success, student = main.prepare_portal_values(request)
#             if not success:
#                 return request.render("odoocms_student_portal.student_error", values)
#             countries =  http.request.env['res.country'].sudo().search([])
#             resume = request.env['odoocms.student.resume'].sudo().search([('student_id', "=", student.id)])
#
#             values.update({
#                 'active_menu': 'resume',
#                 'countries': countries,
#                 'resume': resume
#             })
#             return http.request.render('odoocms_student_portal.student_resume_builder', values)
#         except Exception as e:
#             data = {
#                 # 'student_id': student.id,
#                 'name': 'resume',
#                 'description': e or False,
#                 'state': 'submit',
#             }
#             request.env['odoocms.error.reporting'].sudo().create(data)
#             values = {
#                 'error_message': e or False
#             }
#             return http.request.render('odoocms_student_portal.student_error', values)
#
#     @http.route(['/student/resume/builder/profile'], type='http',  method=['POST'], auth="user", website=True, csrf=False )
#     def student_resume_builder_profile(self, **kw):
#         try:
#             values, success, student = main.prepare_portal_values(request)
#             if not success:
#                 return request.render("odoocms_student_portal.student_error", values)
#             email = kw.get('email')
#             phone = kw.get('mobile')
#             house = kw.get('house')
#             street = kw.get('street')
#             city = kw.get('city')
#             #country = kw.get('country')
#             dob = kw.get('dob')
#            # 923364533765
#
#             data = {
#                 'email': email,
#                 'per_street': house,
#                 'per_street2': street,
#                 'per_city': city,
#                 'mobile': str(phone)
#             }
#             student.write(data)
#
#
#             data = {
#                 'status_is': "",
#                 'message': '',
#                 'color': '#FF0000'
#             }
#
#             data = json.dumps(data)
#             return data
#         except Exception as e:
#             data = {
#                 # 'student_id': student.id,
#                 'name': 'login Credentials Save',
#                 'description': e or False,
#                 'state': 'submit',
#             }
#             request.env['odoocms.error.reporting'].sudo().create(data)
#             data = {
#                 'status_is': "Error",
#                 'message': e.args[0],
#                 'color': '#FF0000'
#             }
#             data = json.dumps(data)
#             return data
#
#     @http.route(['/student/resume/builder/objective'], type='http', method=['POST'], auth="user", website=True, csrf=False)
#     def student_resume_builder_objective(self, **kw):
#         try:
#             values, success, student = main.prepare_portal_values(request)
#             if not success:
#                 return request.render("odoocms_student_portal.student_error", values)
#             objective = kw.get('objective')
#
#
#
#             data = {
#                 'student_id' : student.id,
#                 'objective': objective,
#             }
#             resume = request.env['odoocms.student.resume'].sudo().search([('student_id' ,"=",student.id )])
#             if resume:
#                 resume.sudo().write(data)
#             if not resume:
#                 request.env['odoocms.student.resume'].sudo().create(data)
#
#             data = {
#                 'status_is': "",
#                 'message': 'Objective ',
#                 'color': '#FF0000'
#             }
#
#             data = json.dumps(data)
#             return data
#         except Exception as e:
#             data = {
#                 # 'student_id': student.id,
#                 'name': 'login Credentials Save',
#                 'description': e or False,
#                 'state': 'submit',
#             }
#             request.env['odoocms.error.reporting'].sudo().create(data)
#             data = {
#                 'status_is': "Error",
#                 'message': e.args[0],
#                 'color': '#FF0000'
#             }
#             data = json.dumps(data)
#             return data
#
#     @http.route(['/student/resume/builder/profExp/add'], type='http', method=['POST'], auth="user", website=True, csrf=False)
#     def student_resume_builder_prof_add(self, **kw):
#         try:
#             values, success, student = main.prepare_portal_values(request)
#             if not success:
#                 return request.render("odoocms_student_portal.student_error", values)
#
#             nameOrganization = kw.get('name_org')
#             highlight = kw.get('highlight')
#             exp_from = kw.get('exp_from')
#             exp_to = kw.get('exp_to')
#             resume = request.env['odoocms.student.resume'].sudo().search([('student_id', "=", student.id)])
#             data = {
#                 'name': nameOrganization,
#                 'description': highlight,
#                 'from_date': exp_from,
#                 'to_date': exp_to,
#                 'experience_id': resume.id
#             }
#             resume.experience_ids.sudo().create(data)
#
#
#
#
#             data = {
#                 'status_is': "",
#                 'message': '',
#                 'color': '#FF0000'
#             }
#
#             data = json.dumps(data)
#             return data
#         except Exception as e:
#             data = {
#                 # 'student_id': student.id,
#                 'name': 'login Credentials Save',
#                 'description': e or False,
#                 'state': 'submit',
#             }
#             request.env['odoocms.error.reporting'].sudo().create(data)
#             data = {
#                 'status_is': "Error",
#                 'message': e.args[0],
#                 'color': '#FF0000'
#             }
#             data = json.dumps(data)
#             return data
#
#     @http.route(['/student/resume/builder/profExp/edit'], type='http', method=['POST'], auth="user", website=True, csrf=False)
#     def student_resume_builder_prof_edit(self, **kw):
#         try:
#             values, success, student = main.prepare_portal_values(request)
#             if not success:
#                 return request.render("odoocms_student_portal.student_error", values)
#
#             nameOrganization = kw.get('name_org')
#             highlight = kw.get('highlight')
#             exp_from = kw.get('exp_from')
#             exp_to = kw.get('exp_to')
#             resume = request.env['odoocms.student.resume'].sudo().search([('student_id', "=", student.id)])
#             data = {
#                 'name': nameOrganization,
#                 'description': highlight,
#                 'from_date': exp_from,
#                 'to_date': exp_to,
#                 'experience_id': resume.id
#             }
#             resume.experience_ids.sudo().create(data)
#
#             data = {
#                 'status_is': "",
#                 'message': '',
#                 'color': '#FF0000'
#             }
#
#             data = json.dumps(data)
#             return data
#         except Exception as e:
#             data = {
#                 # 'student_id': student.id,
#                 'name': 'login Credentials Save',
#                 'description': e or False,
#                 'state': 'submit',
#             }
#             request.env['odoocms.error.reporting'].sudo().create(data)
#             data = {
#                 'status_is': "Error",
#                 'message': e.args[0],
#                 'color': '#FF0000'
#             }
#             data = json.dumps(data)
#             return data
#
