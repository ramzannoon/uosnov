# -*- coding: utf-8 -*-

from odoo import models, fields, api


class odoocms_faculty_portal(models.Model):
	_name = 'odoocms.faculty.portal.menu'
	_description = 'Faculty Portal Menu'
	
	name = fields.Char('Name',required=True)
	code = fields.Char('Code',required=True)
	title = fields.Char('Title',required=True)
	href = fields.Char('hRef')
	menu_icon = fields.Text('Menu Icon')
	css_class = fields.Char('CSS Class')
	
	parent_id = fields.Many2one('odoocms.faculty.portal.menu','Parent Menu')
	child_ids = fields.One2many('odoocms.faculty.portal.menu','parent_id','Child Menus')
	
	enable_internal = fields.Boolean('Enable (Internal)',default=True)
	enable_external = fields.Boolean('Enable (External)',default=False)
	
	visible_internal = fields.Boolean('Visible (Internal)', default=True)
	visible_external = fields.Boolean('Visible (External)', default=False)
	sequence = fields.Integer('Sequence')



class ResConfigSettingsFac(models.TransientModel):
	_inherit = 'res.config.settings'
    
    
	grading_visible = fields.Char(string = "Grading visible", config_parameter='odoocms.grading_visible', default='True')
	attendance_visible = fields.Char(string = "Attendance visible", config_parameter='odoocms.attendance_visible', default='True')
