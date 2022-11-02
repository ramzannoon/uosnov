# -*- coding: utf-8 -*-
# from odoo import http


# class CmsNotifications(http.Controller):
#     @http.route('/cms_notifications/cms_notifications/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cms_notifications/cms_notifications/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cms_notifications.listing', {
#             'root': '/cms_notifications/cms_notifications',
#             'objects': http.request.env['cms_notifications.cms_notifications'].search([]),
#         })

#     @http.route('/cms_notifications/cms_notifications/objects/<model("cms_notifications.cms_notifications"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cms_notifications.object', {
#             'object': obj
#         })
