# -*- coding: utf-8 -*-
# from odoo import http


# class IacMoodleConnector(http.Controller):
#     @http.route('/iac_moodle_connector/iac_moodle_connector/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/iac_moodle_connector/iac_moodle_connector/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('iac_moodle_connector.listing', {
#             'root': '/iac_moodle_connector/iac_moodle_connector',
#             'objects': http.request.env['iac_moodle_connector.iac_moodle_connector'].search([]),
#         })

#     @http.route('/iac_moodle_connector/iac_moodle_connector/objects/<model("iac_moodle_connector.iac_moodle_connector"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('iac_moodle_connector.object', {
#             'object': obj
#         })
