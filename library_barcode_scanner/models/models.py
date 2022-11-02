# -*- coding: utf-8 -*-

from odoo import models, fields, api


class LibraryBookScannerWizard(models.TransientModel):
   _name = 'library.barcode.scanner.wizard'

   barcode_scan = fields.Char(string='Book Barcode', help="Here you can provide the barcode for the book")


   def search_book_in_library(self):
      book_rec = self.env['op.media']
      if self.barcode_scan:
         book = book_rec.search([('barcode', '=', self.barcode_scan)])
         self.ensure_one()
         return {
            'name': 'book',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'op.media',
            'res_id': book.id,
            'target': 'current',
         }

