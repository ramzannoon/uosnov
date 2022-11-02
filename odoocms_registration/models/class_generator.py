# -*- coding: utf-8 -*-
import pdb
from odoo import api, fields, models,_

import logging

_logger = logging.getLogger(__name__)


class OdooCMSClassGenerator(models.Model):
	_name = 'odoocms.class.generator'
	_description = 'Class Generator'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name = fields.Char(string='Reference', required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
	term_id = fields.Many2one('odoocms.academic.term','Academic Term')
	institute_id = fields.Many2one('odoocms.institute','School')
	department_id = fields.Many2one('odoocms.department','Department')
	program_id = fields.Many2one('odoocms.program','Program')
	batch_ids = fields.Many2many('odoocms.batch', string='Batches')
	course_id = fields.Many2one('odoocms.course','Course')
	can_generate = fields.Boolean(compute='_can_generate',store=True)
	state = fields.Selection([('draft','Draft'),('done','Done'),('cancel','Cancel')],'Status',default='draft')
	type = fields.Selection([('compulsory','Compulsory'),('elective','Elective')],'Courses Type',default='compulsory')
	class_type = fields.Selection([('regular','Regular'),('special','Special/Summer')],'Class Type',default='regular')
	line_ids = fields.One2many('odoocms.class.generator.line', 'generator_id', 'Lines')
	primary_class_ids = fields.One2many('odoocms.class.primary','generator_id','Primary Classes')
	
	@api.model
	def create(self, vals):
		if vals.get('name', _('New')) == _('New'):
			vals['name'] = self.env['ir.sequence'].next_by_code('odoocms.class.generator') or _('New')
		result = super().create(vals)
		return result
	
	@api.depends('line_ids')
	def _can_generate(self):
		if self.line_ids:
			self.can_generate = True
		else:
			self.can_generate = False
	
	def add_course(self):
		batch = len(self.batch_ids)>0 and self.batch_ids[0].id or False
		if self.course_id:
			data = {
				'name': self.course_id.name,
				'code': self.course_id.code,
				'batch_id': batch,
				'program_id': self.program_id and self.program_id.id or False,
				'department_id': self.department_id.id,
				'institute_id': self.institute_id.id,
				'course_id': self.course_id.id,
				'count': len(self.batch_ids)>0 and len(self.batch_ids[0].section_ids) or 1,
				'type': self.type,
				'class_type': self.class_type,
			}
			self.line_ids = [(0,0,data)]
			self.course_id = False
		
	def fetch_scheme(self):
		#classes = [[5]]
		classes = []
		for batch in self.batch_ids:
			# term_scheme = self.env['odoocms.term.scheme'].search(
			# 	[('session_id', '=', batch.session_id.id), ('term_id', '=', batch.term_id.id)])
			# if not term_scheme:
			# 	raise ValidationError('Term Scheme is not defined for %s and %s' % (batch.session_id.name, batch.term_id.name,))
			
			if self.type == 'compulsory':
				scheme_lines = batch.study_scheme_id.line_ids.filtered(
					lambda l: l.term_id.id == self.term_id.id and l.course_type == self.type)
			else:
				scheme_lines = batch.study_scheme_id.line_ids.filtered(
					lambda l: l.course_type == self.type)
				
			for scheme_line in scheme_lines:
				exists = self.line_ids.filtered(lambda l: l.code == scheme_line.course_id.code and l.batch_id.id == batch.id and l.department_id.id == self.department_id.id)
				if not exists:
					data = {
						'name': scheme_line.course_id.name,
						'code': scheme_line.course_id.code,
						'batch_id': batch.id,
						'program_id': self.program_id and self.program_id.id or False,
						'department_id': self.department_id.id,
						'institute_id': self.department_id.institute_id.id,
						'career_id': batch.career_id.id,
						'course_id': scheme_line.course_id.id,
						'scheme_line_id': scheme_line.id,
						'count': len(batch.section_ids),
						'type': self.type,
						'class_type': self.class_type,
					}
					classes.append((0, 0, data))
		
		if len(classes) > 0:
			self.line_ids = classes
	
	def add_classes(self, term_id, class_code, class_name, line, section=False, batch_term=False):
		# Their is Primary Class for each Section x Course
		primary_class_id = self.env['odoocms.class.primary'].search([('code', '=', class_code),])
		SL = line.scheme_line_id
		if not primary_class_id:
			class_ids = []
			grade_class_id = self.env['odoocms.class.grade'].search([('code', '=', class_code),])
			if not grade_class_id:
				grade_method = False
				if SL:
					grade_method = SL.grade_method_id and SL.grade_method_id.id or False
				if line.batch_id:
					grade_method = line.batch_id.program_id.grade_method_id and line.batch_id.program_id.grade_method_id.id
					
				grade_class_data = {
					'name': class_name,
					'code': class_code,
					'batch_id': line.batch_id and line.batch_id.id or False,
					'career_id': line.career_id and line.career_id.id or False,
					'program_id': line.program_id and line.program_id.id or False,
					'department_id': line.department_id and line.department_id.id or False,
					'term_id': term_id.id,
					'study_scheme_id': line.batch_id.study_scheme_id.id,
					'study_scheme_line_id': SL and SL.id or False,
					'grade_method_id': grade_method,
					'batch_term_id': batch_term and batch_term.id or False,
				}
				_logger.info('Generating Grading Class: %s' % (grade_class_data['code']))
				grade_class_id = self.env['odoocms.class.grade'].create(grade_class_data)
			
			credits = 0
			components = SL and SL.component_lines or line.course_id.component_lines
			for component in components:
				class_data = {
					'name': class_name,
					'code': class_code + '-' + component.component_id.name,
					'component_id': component.component_id.id,
					'weightage': component.weightage,
					'contact_hours': component.contact_hours,
					'section_id': section and section.id or False,
				}
				if line.batch_id:
					class_data = line.batch_id.component_hook(class_data, SL)
				credits += component.weightage
				class_ids.append((0, 0, class_data))
			data = {
				'name': class_name,
				'code': class_code,
				'class_type': line.class_type,
				'session_id': line.batch_id.session_id.id,
				'batch_id': line.batch_id and line.batch_id.id or False,
				'section_id': section and section.id or False,
				'term_id': term_id.id,
				'program_id': line.program_id and line.program_id.id or False,
				'department_id': line.department_id and line.department_id.id or False,
				'study_scheme_id': line.batch_id and line.batch_id.study_scheme_id.id or False,
				'study_scheme_line_id': SL and SL.id or False,
				'course_id': line.course_id.id,
				'career_id': line.career_id.id,
				'strength': section and section.strength or 45,
				'class_ids': class_ids,
				'grade_class_id': grade_class_id.id,
				'credits': credits,
				'major_course': SL and SL.major_course or False,
				'self_enrollment': SL and SL.self_enrollment or False,
				'generator_id': self.id,
				'course_code': SL and SL.course_code and SL.course_code or line.course_id.code,
				'course_name': SL and SL.course_name and SL.course_name or line.course_id.name,
			}
			primary_class_id = self.env['odoocms.class.primary'].create(data)
		return primary_class_id
			
	def action_generate(self):
		primary_class_ids = self.env['odoocms.class.primary']
		for line in self.line_ids:
			batch = line.batch_id
			if batch:
				batch_term = self.env['odoocms.batch.term'].search(
					[('batch_id', '=', batch.id), ('term_id', '=', self.term_id.id)])
				if not batch_term:
					batch_term_data = {
						'name': batch.code + '-' + self.term_id.code,
						'code': batch.code + '-' + self.term_id.code,
						'batch_id': batch.id,
						'term_id': self.term_id.id,
						'semester_id': batch.semester_id.id,
					}
					batch_term_data = batch.batch_term_hook(batch_term_data)
					batch_term = self.env['odoocms.batch.term'].create(batch_term_data)
				
				SL = line.scheme_line_id
				cnt = 1
				for section in batch.section_ids:
					if cnt > line.count:
						break
					cnt = cnt + 1
					class_code = (SL and SL.course_code and SL.course_code or line.course_id.code) \
						+ '-' + self.term_id.short_code + '-' + section.code
					class_name = SL and SL.course_name and SL.course_name or line.course_id.name
					
					primary_class_ids += self.add_classes(self.term_id, class_code, class_name, line, section=section, batch_term=batch_term)
						
			else:
				SL = line.scheme_line_id
				for x in range(1, line.count+1):
					class_code = (SL and SL.course_code and SL.course_code or line.course_id.code) \
						+ '-' + self.term_id.short_code + '-' + self.institute_id.code + '-' + chr(64+x)
					class_name = SL and SL.course_name and SL.course_name or line.course_id.name
					
					primary_class_ids += self.sudo().add_classes(self.term_id, class_code, class_name, line)
		
		self.state = 'done'
		if primary_class_ids:
			class_list = primary_class_ids.mapped('id')
			return {
				'domain': [('id', 'in', class_list)],
				'name': _('Classes'),
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'odoocms.class.primary',
				'view_id': False,
				'type': 'ir.actions.act_window'
			}
		
	def action_reject(self):
		self.state = 'cancel'
		
	def action_reset_draft(self):
		self.state = 'draft'


class OdooCMSClassGeneratorLine(models.Model):
	_name = 'odoocms.class.generator.line'
	_description = 'Class Generator Lines'
	
	generator_id = fields.Many2one('odoocms.class.generator')
	batch_id = fields.Many2one('odoocms.batch','Batch')
	program_id = fields.Many2one('odoocms.program','Program')
	department_id = fields.Many2one('odoocms.department','Department')
	institute_id = fields.Many2one('odoocms.institute','School')
	career_id = fields.Many2one('odoocms.career','Academic Level')
	name = fields.Char('Name')
	code = fields.Char('Code')
	scheme_line_id = fields.Many2one('odoocms.study.scheme.line','Scheme Line')
	course_id = fields.Many2one('odoocms.course','Catalogue Course')
	count = fields.Integer('Class Count')
	type = fields.Selection([('compulsory', 'Compulsory'), ('elective', 'Elective')], 'Courses Type', default='compulsory')
	class_type = fields.Selection([('regular', 'Regular'), ('special', 'Special/Summer')], 'Class Type', default='regular')

