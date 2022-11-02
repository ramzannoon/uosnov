# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    # private attributes
    _inherit = 'product.template'

    # field deceleration
    brand_id = fields.Many2one('brand.brand', string='Brand')
