# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _


class LeadType(models.Model):
    _name = "lead.type"
    _description = "Lead Type"

    name = fields.Char(string='Reason')
