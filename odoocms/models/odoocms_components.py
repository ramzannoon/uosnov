
from odoo import fields, models, api, _


class OdooCMSComponents(models.Model):
    _name = 'odoocms.components'
    _description = 'Components'

    name = fields.Char(string='Name')
