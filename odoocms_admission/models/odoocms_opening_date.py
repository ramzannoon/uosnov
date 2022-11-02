
from odoo import fields, models, api


class OdoocmsOpeningDate(models.Model):
    _name = 'odoocms.opening.date'
    _description = 'Degree'
    _rec_name = "opening_date"

    opening_date = fields.Date(string='Date', required=True)
