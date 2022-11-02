import pdb
from datetime import date
from odoo import api, fields, models,_


class OdooCMSStudentCommentWiz(models.TransientModel):
	_name ='odoocms.student.comment.wiz'
	_description = 'Add Comments for Students'
				
	@api.model	
	def _get_students(self):
		if self.env.context.get('active_model', False) == 'odoocms.student' and self.env.context.get('active_ids', False):
			return self.env.context['active_ids']
			
	student_ids = fields.Many2many('odoocms.student', string='Students',
		help="""Only selected students will be Processed.""",default=_get_students)
	comment = fields.Html(string="Comment", required=True)
	date = fields.Date('Comment Date', default=date.today(), readonly=1)
	notfication_date = fields.Date('Notification Date', default=date.today)
	message_ref = fields.Char(string="Reference Number", required=True)
	cms_ref = fields.Char(string="CMS Reference Number", required=True)

	def add_comments(self):
		name = ""
		if self.env.user and self.env.user.partner_id and  self.env.user.partner_id.name:
			name = self.env.user.partner_id.name
		student_comments = self.env['odoocms.student.comment']

		data = {
			'comment': self.comment,
			'message_ref': self.message_ref,
			'notfication_date': self.notfication_date,
			'cms_ref': self.cms_ref,
		}

		for student in self.student_ids:
			data['student_id'] = student.id
			student_comments += self.env['odoocms.student.comment'].create(data)

		student_comments_list = student_comments.mapped('id')
		return {
			'domain': [('id', 'in', student_comments_list)],
			'name': _('Student Comments'),
			'view_mode': 'tree,form',
			'res_model': 'odoocms.student.comment',
			'view_id': False,
			# 'context': {'default_class_id': self.id},
			'type': 'ir.actions.act_window'
		}



