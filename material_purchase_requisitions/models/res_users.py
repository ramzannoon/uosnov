from odoo import api, fields, models, _


class Users(models.Model):
    _inherit = 'res.users'

    signature_image = fields.Binary(string='Signature Image', attachment=True, help="Provide the image of the Signature")
