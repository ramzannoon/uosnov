# -*- coding: utf-8 -*-

from odoo import api, fields, models ,_

class ProductProduct(models.Model):
    _inherit = 'product.product'

    purchase_line_ids = fields.One2many('purchase.order.line', 'product_id', 'Purchase Lines')

