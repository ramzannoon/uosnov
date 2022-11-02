from odoo import _, api, fields, models


class GenericRequest(models.Model):
    _name = "genericc.req"
    _description = "Generic Requests"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    generic_name = fields.Many2one('emp.general.request', string="Name ", required=True,)
    description = fields.Char('Description')
    date = fields.Date('Date')