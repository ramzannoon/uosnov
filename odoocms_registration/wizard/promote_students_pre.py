import pdb
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError, UserError


class OdooCMSRegisterSchemeCourse(models.TransientModel):
	_name ='odoocms.promote.student'
	_description = 'Promote Students'
				
	@api.model	
	def _get_students(self):
		if self.env.context.get('active_model', False) == 'odoocms.student' and self.env.context.get('active_ids', False):
			return self.env.context['active_ids']

	@api.model
	def _get_term(self):
		new_semester = False
		config_term = self.env['ir.config_parameter'].sudo().get_param('odoocms.current_term')
		if config_term:
			new_semester = self.env['odoocms.academic.term'].sudo().browse(int(config_term))
		return new_semester
			
	student_ids = fields.Many2many('odoocms.student', string='Students',
		help="""Only selected students will be Processed.""",default=_get_students)
	
	term_id = fields.Many2one('odoocms.academic.term','Academic Term',default=_get_term, readonly = True, required=True)
	# st_subiect_reg_tag = fields.Char(string='Registration Tag',default=lambda self:self.env['ir.sequence'].next_by_code('odoocms.student.subject.tag'),copy=False, readonly=True)

	def promote_students(self):
		if not self.term_id:
			raise ValidationError("Please Set Current Academic Term in Configuration")

		student_ids = self.env['odoocms.student']
		for student in self.student_ids:
			#Here need to implement the fee check

			if student.course_ids:
				raise ValidationError("Student is currently enrolled in some Courses. Result of some Courses is not done yet.")
			# If Student does not have any academic semester
			if not student.term_id:
				term_scheme = self.env['odoocms.term.scheme'].search([
					('session_id', '=', student.session_id.id),
					('term_id', '=', self.term_id.id)
				])
				if not term_scheme:
					raise ValidationError(
						"""Term Scheme not defined for Session: %s \n Term: %s \n Student: %s """ % (
							student.session_id.name, self.term_id.name, student.name))

				if term_scheme.semester_id.number > 1:
					raise ValidationError(
						"""Direct Registration is not possible for Semester: %s \n Term: %s \n Student: %s """ % (
							term_scheme.semester_id.name, self.term_id.name, student.name))
				student.term_id = term_scheme.term_id.id
				student.semester_id = term_scheme.semester_id.id
				student_ids += student

			# If Student Academic Semester and reistration semester are same
			elif student.term_id.id == self.term_id.id:
				term_scheme = self.env['odoocms.term.scheme'].search([
					('session_id', '=', student.session_id.id),
					('term_id', '=', self.term_id.id)
				])
				if not term_scheme:
					raise ValidationError(
						"""Term Scheme not defined for Session: %s \n Term: %s \n Student: %s """ % (
							student.session_id.name, self.term_id.name, student.name))
				if not student.semester_id:
					if term_scheme.semester_id.number > 1:
						raise ValidationError(
							"""Direct Registration is not possible for Semester: %s \n Term: %s \n Student: %s """ % (
								term_scheme.semester_id.name, self.term_id.name, student.name))
					student.semester_id = term_scheme.semester_id.id

			# If Student Academic Semester and reistration semester are not same
			elif student.term_id.id != self.term_id.id:
				term_scheme = self.env['odoocms.term.scheme'].search([
					('session_id', '=', student.session_id.id),
					('term_id', '=', self.term_id.id)
				])
				if not term_scheme:
					raise ValidationError(
						"""Term Scheme not defined for Session: %s \n Term: %s \n Student: %s """ % (
							student.session_id.name, self.term_id.name, student.name))

				if not student.semester_id:
					raise ValidationError(
						"""Direct Promotion is not possible for Semester: %s \n Term: %s \n Student: %s """ % (
							term_scheme.semester_id.name, self.term_id.name, student.name))

				current_semester_number = student.semester_id.number
				next_semester_number = current_semester_number + 1
				next_semester = self.env['odoocms.semester'].search([('number', '=', next_semester_number)])
				if not next_semester:
					return False

				next_term_scheme = self.env['odoocms.term.scheme'].search([
					('session_id', '=', student.session_id.id),
					('semester_id', '=', next_semester.id)
				])

				if term_scheme.semester_id.number != next_term_scheme.semester_id.number:
					raise ValidationError(
						"""Promotion is not possible: \nFrom Term: %s (%s) \nTo Term: %s (%s) \nStudent: %s """ % (
							student.term_id.name, student.semester_id.name,
							term_scheme.term_id.name, term_scheme.semester_id.name, student.name))

				student.term_id = self.term_id.id
				student.semester_id = next_semester.id
				student_ids += student

			# if semester_scheme.state != 'approve':
			# 	raise ValidationError("""Semester Scheme not Approved for Session: %s \n Term: %s \n Student: %s """ % (
			# 		student.academic_session_id.name, new_semester.name, student.name))
		
		if student_ids:
			reg_list = student_ids.mapped('id')
			return {
				'domain': [('id', 'in', reg_list)],
				'name': _('Promoted Students'),
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'odoocms.student',
				'view_id': False,
				# 'context': {'default_class_id': self.id},
				'type': 'ir.actions.act_window'
			}

		return 1



