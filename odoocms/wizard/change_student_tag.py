# -*- coding: utf-8 -*-
import pdb
from odoo import api, fields, models,_
from datetime import date
from odoo.exceptions import UserError, ValidationError


class OdooCMSChangeStudenttag(models.Model):
	_name ='odoocms.student.tag.change'
	_description = 'Change Student Tag'
	
	def _get_tags_domain(self):
		tags =self.env['odoocms.student.tag'].search([])
		available_tags = self.env['odoocms.student.tag']
		
		for tag in tags:
			if not tag.group_ids and not tag.category_id:
				available_tags += tag
			elif not tag.group_ids and tag.category_id and not tag.category_id.group_ids:
				available_tags += tag
			elif tag.group_ids:
				has_group = self.env.user.has_group
				serving_tags = tag.get_serving_groups()
				if any([has_group(g) for g in serving_tags]):
					available_tags += tag
			elif not tag.group_ids and tag.category_id.group_ids:
				has_group = self.env.user.has_group
				if any([has_group(g) for g in tag.category_id.get_serving_groups()]):
					available_tags += tag
		domain = [('id', 'in', available_tags.ids)]
		return domain
	
	@api.model
	def _get_students(self):
		if self.env.context.get('active_model', False) == 'odoocms.student' and self.env.context.get('active_ids', False):
			return self.env.context['active_ids']
			
	student_ids = fields.Many2many('odoocms.student', 'tag_change_student_rel','tag_change_id','student_id',string='Students',
	    default=_get_students, help="""Only selected students will be Processed.""")   #,

	action = fields.Selection([('add','Add'),('remove','Remove')])
	tag_id = fields.Many2one('odoocms.student.tag','Tag', domain=_get_tags_domain)  #lambda self: self._get_tags_domain()
	
	#rule_id = fields.Many2one('odoocms.student.change.state.rule', string = "Reason",)
	date_effective = fields.Date('Date Effective',default=date.today())
	description = fields.Text('Description')
	
	def change_student_tag(self):
		for student in self.student_ids:
			if self.action == 'add':
				tags = student.tag_ids + self.tag_id
			elif self.action == 'remove':
				tags = student.tag_ids - self.tag_id
				
			student.with_context({
					'date_effective':self.date_effective,
					'description': self.description,
					'method': 'Tags Form',
				}).write({
				'tag_ids': [[6, 0, tags.ids]]
			})
			
		return {'type': 'ir.actions.act_window_close'}



