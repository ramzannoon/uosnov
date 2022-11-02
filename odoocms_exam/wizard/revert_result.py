import pdb
import time
from datetime import datetime, date, timedelta
from odoo import api, fields, models,_
from dateutil.relativedelta import relativedelta
from odoo.osv import expression
date_format ='%Y-%m-%d'
from odoo.exceptions import UserError


class OdooCMSRevertResult(models.TransientModel):
	_name ='odoocms.revert.result'
	_description = 'Revert Result'

	grade_class_ids = fields.Many2many('odoocms.class.grade', string='Grade Classes')
	
	def revert_result(self):
		for grade_class in self.grade_class_ids:
			grade_class.revisit_result()
		
		return {'type': 'ir.actions.act_window_close'}



