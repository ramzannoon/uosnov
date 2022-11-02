# -*- coding: utf-8 -*-
# from odoo import http
#
#
# class Poll(http.Controller):
#     @http.route('/poll/poll/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/poll/poll/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('poll.listing', {
#             'root': '/poll/poll',
#             'objects': http.request.env['poll.poll'].search([]),
#         })

#     @http.route('/poll/poll/objects/<model("poll.poll"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('poll.object', {
#             'object': obj
#         })
