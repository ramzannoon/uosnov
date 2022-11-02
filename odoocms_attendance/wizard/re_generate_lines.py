import pdb
import time
from datetime import datetime, date, timedelta
from odoo import api, fields, models,_
from dateutil.relativedelta import relativedelta
from odoo.osv import expression
date_format ='%Y-%m-%d'
from odoo.exceptions import UserError


class OdooCMSReGenerateLines(models.TransientModel):
	_name ='odoocms.regenerate.attendance'
	_description = 'Re Generate Attendance Lines'

	term_id = fields.Many2one('odoocms.academic.term','Academic Term')
	level = fields.Selection([
		('institute', 'Institute'),
		('department', 'Department'),
		('program', 'Program'),
		('career', 'Career'),
		('batch', 'Batch'),
		('class', 'Class')], string='Level', default='batch')
	
	batch_ids = fields.Many2many('odoocms.batch', string='Batches')
	career_ids = fields.Many2many('odoocms.career', string='Career')
	program_ids = fields.Many2many('odoocms.program', string='Programs')
	department_ids = fields.Many2many('odoocms.department', string='Departments')
	institute_ids = fields.Many2many('odoocms.institute', string='Schools')
	class_ids = fields.Many2many('odoocms.class', string='Classes')

	def regenerate_lines(self):
		domain = [
			(1, '=', 1),
		]
		att_classes = self.env['odoocms.class.attendance'].sudo()
		if self.level == 'class' and self.class_ids:
			domain = expression.AND([domain, [('id', 'in', self.class_ids.ids)]])
			class_ids = self.env['odoocms.class'].search(domain)
			att_classes = self.env['odoocms.class.attendance'].search([
				('class_id','in',class_ids.ids),
				('state','!=','lock')
			])
			att_classes.write({
				'to_be': True,
			})
		else:
			if self.level == 'batch' and self.batch_ids:
				domain = expression.AND([domain, [('id', 'in', self.batch_ids.ids)]])
			elif self.level == 'program' and self.program_ids:
				domain = expression.AND([domain, [('program_id', 'in', self.program_ids.ids)]])
			elif self.level == 'department' and self.department_ids:
				domain = expression.AND([domain, [('department_id', 'in', self.department_ids.ids)]])
			elif self.level == 'institute' and self.institute_ids:
				domain = expression.AND([domain, [('institute_id', 'in', self.institute_ids.ids)]])
			elif self.level == 'career' and self.career_ids:
				domain = expression.AND([domain, [('career_id', 'in', self.career_ids.ids)]])
			
			batches = self.env['odoocms.batch'].search(domain)
			att_classes = self.env['odoocms.class.attendance'].search([
				('batch_id', 'in', batches.ids),
				('state', '!=', 'lock')
			])
			att_classes.write({
				'to_be': True,
			})

		if att_classes:
			class_list = att_classes.mapped('id')
			return {
				'domain': [('id', 'in', class_list)],
				'name': _('Scheduled Classes'),
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'odoocms.class.attendance',
				'view_id': False,
				'type': 'ir.actions.act_window'
			}
		else:
			return {'type': 'ir.actions.act_window_close'}



