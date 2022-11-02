import pdb
import time
from datetime import datetime, date, timedelta
from odoo import api, fields, models,_
from dateutil.relativedelta import relativedelta
from odoo.osv import expression
date_format ='%Y-%m-%d'
from odoo.exceptions import UserError


class OdooCMSReCalculateResult(models.TransientModel):
	_name ='odoocms.recalculate.result'
	_description = 'Re-Calculate Result'

	primary_class_ids = fields.Many2many('odoocms.class.primary', string='Primary Classes')
	student_course_ids = fields.Many2many('odoocms.student.course',string='Student Courses')
	
	def recalculate_result(self):
		if self.primary_class_ids:
			self.primary_class_ids.write({
				'to_be': True,
			})
		elif self.student_course_ids:
			self.student_course_ids.write({
				'to_be': True,
			})
			
		return {'type': 'ir.actions.act_window_close'}



