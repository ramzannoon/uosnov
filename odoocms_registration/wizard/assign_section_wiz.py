import pdb

from odoo import api, fields, models,_
import math


class OdooCMSAssignSectionWiz(models.TransientModel):
	_name ='odoocms.assign.section.wiz'
	_description = 'Assign Section Wizard'

	student_ids = fields.Many2many('odoocms.student', string='Students',
		help="""Only selected students will be Processed.""")
	
	batch_id = fields.Many2one('odoocms.batch','Batch')

	@api.onchange('batch_id')
	def onchange_batch_id(self):
		student_ids = self.env['odoocms.student'].search([('batch_id','=',self.batch_id.id)])
		if student_ids:
			self.student_ids = student_ids

	def assign_section(self):
		student_ids = self.student_ids.sorted(key=lambda r: r.cgpa, reverse=True)
		batch_section_ids = self.env['odoocms.batch.section'].search([('batch_id','=',self.batch_id.id)])

		# outer = 0
		# for sec in batch_section_ids:
		# 	inner = outer
		# 	for st in range(0, len(student_ids) / len(batch_section_ids)):
		# 		student_ids[inner].section_id = sec.id
		# 		inner += len(batch_section_ids)
		# 	outer += 1

		i = 0
		for st in range(0, math.ceil(len(student_ids)/len(batch_section_ids)) ):
			for sec in batch_section_ids:
				if (i<len(student_ids)):
					student_ids[i].section_id = sec.id
					i += 1

		if student_ids:
			reg_list = student_ids.mapped('id')
			return {
				'domain': [('id', 'in', reg_list)],
				'name': _('Student'),
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'odoocms.student',
				'view_id': False,
				# 'context': {'default_class_id': self.id},
				'type': 'ir.actions.act_window'
			}
		else:
			return {'type': 'ir.actions.act_window_close'}



