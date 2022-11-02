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
             
             #class_ids = request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id)])

             values.update({
                 #'class_ids' : class_ids,
                 'active_menu': 'profile',
             })
             return http.request.render('odoocms_faculty_portal.faculty_portal_profile_page',values)
         except Exception as e:
             values = {
                 'error_message': e or False
             }
             return http.request.render('odoocms_web.portal_error', values)

