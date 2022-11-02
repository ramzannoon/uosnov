# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductProduct(models.Model):
    # private attributes
    _inherit = 'product.product'

    # field deceleration
    brand_id = fields.Many2one('brand.brand', string="Brand")
