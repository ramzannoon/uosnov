from odoo import _, api, fields, models


class GeneralRequest(models.Model):
    _name = "emp.general.request"
    _description = "General Requests"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True,)



class Equipment(models.Model):
    _name = "emp.equipment"
    _description = "General Requests"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True,)