from odoo import api, fields, models, _

class ResPartner(models.Model):
	_inherit = 'res.partner'

	cnic = fields.Char( string='CNIC')


class ResCompany(models.Model):
	_inherit = "res.company"

	short_name = fields.Char('Short Name')