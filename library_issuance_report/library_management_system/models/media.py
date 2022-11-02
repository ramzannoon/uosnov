# -*- coding: utf-8 -*-

from odoo import models, fields, _


class OpMedia(models.Model):
    _name = "op.media"
    _description = "Media Details"
    _order = "name"

    name = fields.Char('Title', size=128, required=True)
    isbn = fields.Char('ISBN Code', size=64)
    tags = fields.Many2many('op.tag', string='Tag(s)')
    author_ids = fields.Many2many(
        'op.author', string='Author(s)')
    edition = fields.Char('Edition')
    description = fields.Text('Description')
    issuance_state = fields.Selection([
        ('approved', 'Approved'),
        ('not_approved', 'Not Approved')
    ], string='Issuance State', default='approved')
    publisher_ids = fields.Many2many(
        'op.publisher', string='Publisher(s)')
    course_ids = fields.Many2many('odoocms.course', string='Course')
    movement_line = fields.One2many('op.media.movement', 'media_id',
                                    'Movements')
    # subject_ids = fields.Many2many(
    #     'op.subject', string='Subjects')
    internal_code = fields.Char('Internal Code', size=64)
    queue_ids = fields.One2many('op.media.queue', 'media_id', 'Media Queue')
    unit_ids = fields.One2many('op.media.unit', 'media_id', 'Units')
    media_type_id = fields.Many2one('op.media.type', 'Reference Type')
    active = fields.Boolean(default=True)

    barcode = fields.Char(string="Barcode")
    item_call_number = fields.Char(string="Item Call Number")
    location = fields.Char(string="Location")
    book_seller = fields.Char(string="Book Seller ID")
    book_issuance = fields.Selection([("issuable", "Issuable"),
                                      ("not_issuable", "Not Issuable")], string="Issuance")

    _sql_constraints = [
        ('unique_name_isbn',
         'unique(isbn)',
         'ISBN code must be unique per media!'),
        ('unique_name_internal_code',
         'unique(internal_code)',
         'Internal Code must be unique per media!'),
    ]

    def action_view_onhand_lib(self):
        view_id = self.env.ref('library_management_system.view_stock_library_tree')
        return {
            'name': _('Stock Available'),
            'view_type': 'tree',
            'view_mode': 'list',
            'res_model': 'stock.library',
            'view_id': view_id.id,
            'type': 'ir.actions.act_window',
            'domain': [('media_id', '=', self.id)],
        }
