# -*- coding: utf-8 -*-
import pdb
import time
import datetime
from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError


class OdooCMSChangeStudentRegID(models.TransientModel):
	_name ='odoocms.student.reg.change'
	_description = 'Change Student Reg Number'
				
	@api.model	
	def _get_students(self):
		if self.env.context.get('active_model', False) == 'odoocms.student' and self.env.context.get('active_ids', False):
			return self.env.context['active_ids']
			
	student_ids = fields.Many2many('odoocms.student', string='Students',
		help="""Only selected students will be Processed.""",default=_get_students)

	def change_student_reg_no(self):
		for student in self.student_ids:
			if student.new_id_number in self.env['odoocms.student'].search([]).filtered(lambda s:s.id != student.id).mapped('id_number'):
				student.new_id_number = False
				raise UserError(_("Another Student having same(%s) Reg Number" % (student.id_number,)))
			else:
				student.id_number = student.new_id_number
				student.new_id_number = False
		return {'type': 'ir.actions.act_window_close'}



