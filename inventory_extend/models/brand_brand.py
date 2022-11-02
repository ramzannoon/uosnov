# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class BrandBrand(models.Model):
    _name = 'brand.brand'
    _rec_name = 'name'
    _description = 'Brand'

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name", required=True)
