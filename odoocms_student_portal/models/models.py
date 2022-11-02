# -*- coding: utf-8 -*-

from odoo import models, fields, api


class odoocms_student_portal(models.Model):
	_name = 'odoocms.student.portal.menu'
	_description = 'Student Portal Menu'
	
	name = fields.Char('Name', required=True)
	code = fields.Char('Code', required=True)
	title = fields.Char('Title', required=True)
	href = fields.Char('hRef')
	menu_icon = fields.Text('Menu Icon')
	css_class = fields.Char('CSS Class')
	
	parent_id = fields.Many2one('odoocms.student.portal.menu', 'Parent Menu')
	child_ids = fields.One2many('odoocms.student.portal.menu', 'parent_id', 'Child Menus')
	role = fields.Selection([
		('G','Undergraduate'),('PG','Graduate'),('PHD','Doctoral'),('DP','Diploma'),('All','All')], default='All')
	enable_internal = fields.Boolean('Enable (Internal)', default=True)
	enable_external = fields.Boolean('Enable (External)', default=False)
	visible_internal = fields.Boolean('Visible (Internal)', default=True)
	visible_external = fields.Boolean('Visible (External)', default=False)
	sequence = fields.Integer('Sequence')


# class ResConfigSettingsFac(models.TransientModel):
# 	_inherit = 'res.config.settings'
#
# 	student_portal_block = fields.Char(string="Block Student Portal", config_parameter='odoocms.block_portal', default='False')
