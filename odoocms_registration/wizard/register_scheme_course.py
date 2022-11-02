import pdb
import time
from datetime import date, datetime
from odoo import api, fields, models,_
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


# class OdooCMSRegisterSchemeCourse(models.TransientModel):
# 	_name ='odoocms.register.scheme.course'
# 	_description = 'Register Scheme Course'
#
# 	@api.model
# 	def _get_students(self):
# 		if self.env.context.get('active_model', False) == 'odoocms.student' and self.env.context.get('active_ids', False):
# 			return self.env.context['active_ids']
#
# 	student_ids = fields.Many2many('odoocms.student', string='Students',
# 		help="""Only selected students will be Processed.""",default=_get_students)
#
# 	term_id = fields.Many2one('odoocms.academic.term','Academic Term')
# 	st_course_reg_tag = fields.Char(string='Registration Tag',
# 	    default=lambda self:self.env['ir.sequence'].next_by_code('odoocms.student.course.tag'),copy=False, readonly=True)
#
# 	def get_planning_date(self,student_id, p_type):
# 		new_semester = self.academic_semester_id
# 		planning_line = False
# 		if new_semester.planning_ids:
# 			planning_line = new_semester.planning_ids.filtered(
# 				lambda l: l.type == p_type and len(l.campus_ids) == 0 and len(
# 					l.department_ids) == 0 and len(l.semester_ids) == 0)
# 			if not planning_line:
# 				planning_line = new_semester.planning_ids.filtered(
# 					lambda l: l.type == p_type and student_id.campus_id in (l.campus_ids) and len(
# 						l.department_ids) == 0 and len(l.semester_ids) == 0)
# 				if not planning_line:
# 					planning_line = new_semester.planning_ids.filtered(lambda l: l.type == p_type and len(
# 						l.campus_ids) == 0 and student_id.batch_id.department_id in (
# 																					 l.department_ids) and len(
# 						l.semester_ids) == 0)
# 					if not planning_line:
# 						planning_line = new_semester.planning_ids.filtered(
# 							lambda l: l.type == p_type and len(l.campus_ids) == 0 and len(
# 								l.department_ids) == 0 and student_id.semester_id in (l.semester_ids))
# 						if not planning_line:
# 							planning_line = new_semester.planning_ids.filtered(
# 								lambda l: l.type == p_type and len(
# 									l.campus_ids) == 0 and student_id.batch_id.department_id in (
# 											  l.department_ids) and student_id.semester_id in (
# 											  l.semester_ids))
# 							if not planning_line:
# 								planning_line = new_semester.planning_ids.filtered(
# 									lambda l: l.type == p_type and student_id.campus_id in (
# 										l.campus_ids) and len(
# 										l.department_ids) == 0 and student_id.semester_id in (
# 												  l.semester_ids))
# 								if not planning_line:
# 									planning_line = new_semester.planning_ids.filtered(
# 										lambda l: l.type == p_type and student_id.campus_id in (
# 											l.campus_ids) and student_id.batch_id.department_id in (
# 													  l.department_ids) and student_id.semester_id in (
# 													  l.semester_ids))
# 									if not planning_line:
# 										planning_line = new_semester.planning_ids.filtered(
# 											lambda l: l.type == p_type and student_id.campus_id in (
# 												l.campus_ids) and student_id.batch_id.department_id in (
# 														  l.department_ids) and len(l.semester_ids) == 0)
# 		return planning_line
#
# 	def register_scheme(self):
# 		registration = self.env['odoocms.student.course']
# 		not_reg_students = self.env['odoocms.student']
# 		for student in self.student_ids:
# 			if not student.study_scheme_id:
# 				not_reg_students += student
# 				student.message_post(body=('Study Scheme not Assigned'))
# 				# continue
# 				raise UserError('Study Scheme not Assigned.')
#
# 			# planning_line = self.get_planning_date(student,'enrollment')
# 			# if not planning_line or len(planning_line) == 0:
# 			# 	student.message_post(body=('Course Enrollment Date is not configured yet.'))
# 			# 	not_reg_students += student
# 			# 	# continue
# 			# 	raise UserError('Course Enrollment Date is not configured yet.')
# 			#
# 			# elif date.today() > planning_line.date_end:
# 			# 	student.message_post(body=('Course Enrollment Date is Over.'))
# 			# 	not_reg_students += student
# 			# 	# continue
# 			# 	raise UserError('Course Enrollment Date is Over.')
# 			#
# 			# else:
# 			reg = student.register_scheme_courses(self.term_id, self.st_course_reg_tag)
# 			if reg:
# 				registration += reg
#
# 		if registration:
# 			reg_list = registration.mapped('id')
# 			return {
# 				'domain': [('id', 'in', reg_list)],
# 				'name': _('Student Registration'),
# 				'view_type': 'form',
# 				'view_mode': 'tree,form',
# 				'res_model': 'odoocms.student.course',
# 				'view_id': False,
# 				# 'context': {'default_class_id': self.id},
# 				'type': 'ir.actions.act_window'
# 			}
# 		# elif not_reg_students:
# 		# 	reg_list = not_reg_students.mapped('id')
# 		# 	return {
# 		# 		'domain': [('id', 'in', reg_list)],
# 		# 		'name': _('Students'),
# 		# 		'view_type': 'form',
# 		# 		'view_mode': 'tree,form',
# 		# 		'res_model': 'odoocms.student',
# 		# 		'view_id': False,
# 		# 		# 'context': {'default_class_id': self.id},
# 		# 		'type': 'ir.actions.act_window'
# 		# 	}
# 		return 1
#
#
#
