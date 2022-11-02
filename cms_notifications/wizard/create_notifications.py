# -*- coding: utf-8 -*-

from odoo import api, fields, models

from datetime import datetime
from dateutil.relativedelta import relativedelta


class OdooCMSCreateStudentNotifications(models.TransientModel):
	
	_name ='odoocms.student.notifications'
	_description = 'Create Student Notifications'

	@api.model
	def _get_students(self):
		if self.env.context.get('active_model', False) == 'odoocms.student' and self.env.context.get('active_ids', False):
			return self.env.context['active_ids']

	@api.model
	def get_default_user(self):
		return self.env.user.id

	name = fields.Char('Title')
	description = fields.Html('Description')
	date = fields.Datetime('Date', default=datetime.now())
	expiry = fields.Date('Expiry Date', default=date.today() + relativedelta(days=7))
	image = fields.Binary('Image', attachment=True)
	uploaded_by = fields.Many2one('res.users', 'Uploaded By', default= get_default_user)
	priority = fields.Boolean('Visible Top', default=False)
	allow_preview = fields.Boolean('Allow Preview', default=True)
	student_ids = fields.Many2many('odoocms.student', string='Students',
		help="""Only selected students will be Processed.""", default=_get_students)

	def create_notifications(self):
		notification_vals = {}
		CMSNotifications = self.env['cms.notification']
		if self.name:
			notification_vals['name'] = self.name
		if self.description:
			notification_vals['description'] = self.description
		if self.date:
			notification_vals['date'] = self.date
		if self.expiry:
			notification_vals['expiry'] = self.expiry
		if self.image:
			notification_vals['image'] = self.image
		if self.uploaded_by:
			notification_vals['uploaded_by'] = self.uploaded_by.id
		if self.priority:
			notification_vals['priority'] = self.priority
		if self.allow_preview:
			notification_vals['allow_preview'] = self.allow_preview
		if self.student_ids:
			'''
				Iterating over each student to create notifications for respective student if there user exists
			'''
			User_ids = []
			for student in self.student_ids:
				if student.user_id:
					User_ids.append(student.user_id.id)
			notification_vals['recipient_ids'] = [(6, 0, User_ids)]
			CMSNotifications.create(notification_vals)
		return {'type': 'ir.actions.act_window_close'}


class OdooCMSCreateFacultyNotifications(models.TransientModel):
	
	_name ='odoocms.faculty.notifications'
	_description = 'Create Faculty Notifications'

	@api.model
	def _get_faculty(self):
		if self.env.context.get('active_model', False) == 'odoocms.faculty.staff' and self.env.context.get('active_ids', False):
			return self.env.context['active_ids']

	@api.model
	def get_default_user(self):
		return self.env.user.id

	name = fields.Char('Title')
	description = fields.Html('Description')
	date = fields.Datetime('Date', default=datetime.now())
	expiry = fields.Date('Expiry Date', default=date.today() + relativedelta(days=7))
	image = fields.Binary('Image', attachment=True)
	uploaded_by = fields.Many2one('res.users', 'Uploaded By', default= get_default_user)
	priority = fields.Boolean('Visible Top', default=False)
	allow_preview = fields.Boolean('Allow Preview', default=True)
	faculty_ids = fields.Many2many('odoocms.faculty.staff', string='Faculty Staff',
		help="""Only selected staff will be Processed.""",default=_get_faculty)

	def create_notifications(self):
		notification_vals = {}
		CMSNotifications = self.env['cms.notification']
		if self.name:
			notification_vals['name'] = self.name
		if self.description:
			notification_vals['description'] = self.description
		if self.date:
			notification_vals['date'] = self.date
		if self.expiry:
			notification_vals['expiry'] = self.expiry
		if self.image:
			notification_vals['image'] = self.image
		if self.uploaded_by:
			notification_vals['uploaded_by'] = self.uploaded_by.id
		if self.priority:
			notification_vals['priority'] = self.priority
		if self.allow_preview:
			notification_vals['allow_preview'] = self.allow_preview
		if self.faculty_ids:
			User_ids = []
			for faculty in self.faculty_ids:
				'''
				Notification Will be Created for those faculty whose user exists
				'''
				if faculty.user_id:
					User_ids.append(faculty.user_id.id)
			notification_vals['recipient_ids'] = [(6, 0, User_ids)]
			CMSNotifications.create(notification_vals)
		return {'type': 'ir.actions.act_window_close'}

