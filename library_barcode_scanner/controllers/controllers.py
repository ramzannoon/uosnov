# -*- coding: utf-8 -*-
# from odoo import http


# class LibraryBarcodeScanner(http.Controller):
#     @http.route('/library_barcode_scanner/library_barcode_scanner/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/library_barcode_scanner/library_barcode_scanner/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('library_barcode_scanner.listing', {
#             'root': '/library_barcode_scanner/library_barcode_scanner',
#             'objects': http.request.env['library_barcode_scanner.library_barcode_scanner'].search([]),
#         })

#     @http.route('/library_barcode_scanner/library_barcode_scanner/objects/<model("library_barcode_scanner.library_barcode_scanner"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('library_barcode_scanner.object', {
#             'object': obj
#         })
