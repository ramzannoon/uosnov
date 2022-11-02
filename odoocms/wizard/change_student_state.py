# -*- coding: utf-8 -*-
import pdb
from odoo import api, fields, models,_
from datetime import date
from odoo.exceptions import UserError, ValidationError


class OdooCMSChangeStudentState(models.Model):
	_name ='odoocms.student.state.change'
	_description = 'Change Student State'
				
	@api.model
	def _get_students(self):
		if self.env.context.get('active_model', False) == 'odoocms.student' and self.env.context.get('active_ids', False):
			return self.env.context['active_ids']
			
	student_ids = fields.Many2many('odoocms.student', 'state_change_student_rel','state_change_id','student_id',
	    string='Students', default=_get_students, help="""Only selected students will be Processed.""")

	state = fields.Selection(lambda self: self.env['odoocms.selections'].get_selection_field('Student States'), tracking=True)
	
	rule_id = fields.Many2one('odoocms.student.change.state.rule', string = "Reason",)
	date_effective = fields.Date('Date Effective',default=date.today())
	description = fields.Text('Description')
	
	def change_student_state(self):
		for student in self.student_ids:
			if not student.batch_id:
				raise UserError('Please Assign Batch to %s-%s' % (student.code, student.name))
			if not student.section_id:
				if student.batch_id and len(student.batch_id.section_ids) == 1:
					student.section_id = student.batch_id.section_ids[0].id
				else:
					raise UserError('Please Assign Section to %s-%s' % (student.code, student.name))
			
			if self.state == 'enroll':
				if not student.term_id:
					student.term_id = student.batch_id.term_id.id
				if not student.semester_id:
					student.semester_id = student.batch_id.semester_id.id
			
			student.with_context({
					'date_effective':self.date_effective,
					'description': self.description,
					'method': 'State Wizard',
				}).write({
				'state': self.state,
			})
			
			# if (student.state == 'enroll' and (self.state in ('draft','suspend', 'cancel'))):
			# 	student.update({'state': self.state})
			# elif (student.state in ('draft','suspend', 'cancel') and self.state == 'enroll'):
			# 	student.update({'state': 'enroll'})

		return {'type': 'ir.actions.act_window_close'}



