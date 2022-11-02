# -*- coding: utf-8 -*-
# from odoo import http


# class ItemsInventoryReport(http.Controller):
#     @http.route('/items_inventory_report/items_inventory_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/items_inventory_report/items_inventory_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('items_inventory_report.listing', {
#             'root': '/items_inventory_report/items_inventory_report',
#             'objects': http.request.env['items_inventory_report.items_inventory_report'].search([]),
#         })

#     @http.route('/items_inventory_report/items_inventory_report/objects/<model("items_inventory_report.items_inventory_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('items_inventory_report.object', {
#             'object': obj
#         })
