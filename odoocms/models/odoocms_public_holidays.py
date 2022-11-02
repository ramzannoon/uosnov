from datetime import date
from odoo.tools.translate import _
from odoo import models, fields, api


class hr_holidays(models.Model):
	_name = 'odoocms.holidays.public'
	_description = 'Public Holidays'
	_order = "date, name desc"
	
	name = fields.Char('Name', required=True)
	date = fields.Date('Date', required=True)
	term_id = fields.Many2one('odoocms.academic.term','Academic Term')
	variable = fields.Boolean('Date may change')


class OdooCMSAcademicTerm(models.Model):
	_inherit = 'odoocms.academic.term'

	pubilc_holidays_ids = fields.One2many('odoocms.holidays.public', 'term_id', string='Public Holidays')