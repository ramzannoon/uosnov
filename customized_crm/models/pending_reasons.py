# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _


class PendingReasons(models.Model):
    _name = "pending.reasons"
    _description = "Pending Reasons"

    name = fields.Char(string='Reason')
