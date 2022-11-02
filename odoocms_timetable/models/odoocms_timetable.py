from odoo import models, fields, api, _
from . import aarsol_unitime
import pdb
from odoo.exceptions import ValidationError, UserError


class OdooCMSTimeTableSchedule(models.Model):
	_name = 'odoocms.timetable.schedule'
	_description = 'Timetable Schedule'
	_order = 'period_id'
	
	period_id = fields.Many2one('odoocms.time.pattern', string="Period")
	time_from = fields.Float(string='From', required=True, index=True, help="Start and End time of Period.")
	time_to = fields.Float(string='To', required=True)
	total_time = fields.Float(compute='calculate_time', string='Total Time')
	class_id = fields.Many2one('odoocms.class', string='Class', required=True)
	
	primary_class_id = fields.Many2one('odoocms.class.primary', 'Primary Class', related='class_id.primary_class_id', store=True)
	term_id = fields.Many2one('odoocms.academic.term', string='Term', related='class_id.term_id', store=True)
	section_id = fields.Many2one('odoocms.batch.section', related='primary_class_id.section_id', store=True)
	batch_id = fields.Many2one('odoocms.batch', related='section_id.batch_id', store=True)
	faculty_id = fields.Many2one('odoocms.faculty.staff', string='Faculty', related='class_id.faculty_staff_id', store=True)
	
	week_day_ids = fields.Many2many('odoocms.week.day', string='Week Days')
	building_id = fields.Many2one('odoocms.building', 'Building')
	room_id = fields.Many2one('odoocms.room', 'Room', required=True)
	active = fields.Boolean('Active', default=True)
	
	@api.constrains('room_id', 'term_id','week_day_ids','time_from','time_to')
	def _check_room(self):
		for rec in self:
			if rec.term_id and rec.room_id and rec.week_day_ids:
				for weekday in rec.week_day_ids:
					class_ids = self.env['odoocms.timetable.schedule'].search([
						('term_id', '=', rec.term_id.id),
						('room_id', '=', rec.room_id.id),
						('time_from', '<', rec.time_to), ('time_to', '>', rec.time_from),
						('id', '!=', rec.id)]).filtered(lambda l: weekday in (l.week_day_ids))

					class_ids2 = self.env['odoocms.timetable.schedule'].search([
						('term_id', '=', rec.term_id.id),
						('room_id', '=', rec.room_id.id),
						('time_from', '=', rec.time_from), ('time_to', '=', rec.time_to),
						('id', '!=', rec.id)]).filtered(lambda l: weekday in (l.week_day_ids))
					if class_ids:
						raise UserError(_("Their is another class (%s) in same time for Room %s" % (class_ids[0].class_id.name, rec.room_id.name,)))
					elif class_ids2:
						raise UserError(_("Their is another class (%s) in same time for Room %s" % (class_ids2[0].class_id.name, rec.room_id.name,)))
					
	@api.constrains('faculty_id', 'term_id','week_day_ids','time_from','time_to')
	def _check_faculty(self):
		for rec in self:
			if rec.term_id and rec.faculty_id and rec.week_day_ids:
				for weekday in rec.week_day_ids:
					class_ids = self.env['odoocms.timetable.schedule'].search([
						('term_id', '=', rec.term_id.id),
						('faculty_id', '=', rec.faculty_id.id),
						('time_from', '<', rec.time_to), ('time_to', '>', rec.time_from),
						('id', '!=', rec.id)]).filtered(lambda l: weekday in (l.week_day_ids))
					
					class_ids2 = self.env['odoocms.timetable.schedule'].search([
						('term_id', '=', rec.term_id.id),
						('faculty_id', '=', rec.faculty_id.id),
						('time_from', '=', rec.time_from), ('time_to', '=', rec.time_to),
						('id', '!=', rec.id)]).filtered(lambda l: weekday in (l.week_day_ids))
					if class_ids:
						raise UserError(_("Their is another class (%s) in same time for Faculty Member %s" % (class_ids[0].class_id.name, rec.faculty_id.name)))
					elif class_ids2:
						raise UserError(_("Their is another class (%s) in same time for Faculty Member %s" % (class_ids2[0].class_id.name, rec.faculty_id.name)))
					
	@api.constrains('time_from', 'time_to')
	def check_time(self):
		for rec in self:
			if rec.time_from and rec.time_to and rec.time_from >= rec.time_to:
				raise ValidationError(_(
					"Time from must be less than Time to!"))
			
	@api.depends('time_from', 'time_to')
	def calculate_time(self):
		for rec in self:
			time_from = str(rec.time_from).replace(' ','').split('.')
			time_to = str(rec.time_to).replace(' ','').split('.')
			
			first_hrs = time_to[0]
			first_minutes = '.' + time_to[1]
			second_hrs = time_from[0]
			second_minutes = '.' + time_from[1]
			total_hrs = float(first_hrs) - float(second_hrs)
			total_minutes = float(first_minutes) - float(second_minutes)
			rec.total_time = total_hrs + (total_minutes)
	
	def name_get(self):
		res = []
		for record in self:
			days = [day.code for day in record.week_day_ids]
			name = record.class_id.code + ' - ' + ','.join(days) + ' - ' + str(record.time_from)
			res.append((record.id, name))
		return res
	
	@api.model
	def get_timetable(self, student=False, faculty=False, term_id=False):
		schedule_lines = {}
		for day in self.env['odoocms.week.day'].search([], order='number'):
			schedule_lines[day.number] = []
		
		if faculty:
			schedules = self.sudo().search([('faculty_id', '=', faculty.id),( 'term_id', '=',  term_id.id )], order='time_from')
			
			for schedule in schedules:
				for week_day in schedule.week_day_ids:
					line = {
						'time_from': "%02d:%02d" % (divmod(schedule.time_from * 60, 60)),
						'time_to': "%02d:%02d" % (divmod(schedule.time_to * 60, 60)),
						'subject_code': schedule.class_id.primary_class_id.code,
						'component': schedule.class_id.component,
						'subject_name': schedule.class_id.name,
						'faculty': schedule.faculty_id.name,
						'room': schedule.room_id.name,
						'day_number': week_day.number,
						'day_code': week_day.code,
					}
					schedule_lines[week_day.number].append(line)
		
		if student:
			student_rec = self.env['odoocms.student'].search([('id', '=', student.id)])
			config_term = self.env['ir.config_parameter'].sudo().get_param('odoocms.current_term')
			if config_term:
				new_semester = self.env['odoocms.academic.term'].sudo().browse(int(config_term))
			else:
				new_semester = student_rec.term_id
			
			class_ids = student_rec.enrolled_course_ids.mapped('component_ids').mapped('class_id').filtered(
				lambda l: l.term_id.id == new_semester.id).ids
			schedules = self.sudo().search([('class_id', 'in', class_ids)], order='time_from')
			
			for schedule in schedules:
				for week_day in schedule.week_day_ids:
					line = {
						'time_from': "%02d:%02d" % (divmod(schedule.time_from * 60, 60)),
						'time_to': "%02d:%02d" % (divmod(schedule.time_to * 60, 60)),
						'subject_code': schedule.class_id.primary_class_id.code,
						'component': schedule.class_id.component,
						'subject_name': schedule.class_id.name,
						'faculty': schedule.faculty_id.name,
						'room': schedule.room_id.name,
						'day_code': week_day.code,
					}
					schedule_lines[week_day.number].append(line)
		return schedule_lines
	
	@api.model
	def get_timetable2(self, student=False, faculty=False):  # this is for sohaib, later on i will combine both
		schedule_lines = {}
		for key, value in self._fields['week_day'].selection:
			schedule_lines[value] = []
		
		if faculty:
			class_ids = self.env['odoocms.class'].search([('faculty_staff_id', '=', faculty.id)])
			timeschedules = self.sudo().search([('class_id', 'in', class_ids.mapped('id'))], order='week_day,time_from')
			
			for schedule in timeschedules:
				line = {
					'time_from': str(schedule.time_from),
					'time_to': str(schedule.time_to),
					'subject': schedule.class_id.study_scheme_line_id.subject_id.name,
					'faculty': schedule.faculty_id.name,
					'room': schedule.room_id.name,
				}
				week_day = dict(schedule._fields['week_day'].selection).get(schedule.week_day)
				schedule_lines[week_day].append(line)
		
		if student and self.env['odoocms.student'].search([('id', '=', student)]):
			
			student = self.env['odoocms.student'].search([('id', '=', student)])
			timeschedules = self.sudo().search([('class_id', 'in', student.subject_ids.mapped('class_id').ids)],
			                                   order='week_day,time_from')
			
			for schedule in timeschedules:
				line = {
					'time_from': str(schedule.time_from),
					'time_to': str(schedule.time_to),
					'subject': schedule.class_id.study_scheme_line_id.subject_id.name,
					'faculty': schedule.faculty_id.name,
					'room': schedule.room_id.name,
				}
				week_day = dict(schedule._fields['week_day'].selection).get(schedule.week_day)
				schedule_lines[week_day].append(line)
		
		return schedule_lines


class OdooCMSClassPrimary(models.Model):
	_inherit = 'odoocms.class.primary'
	
	timetable_ids = fields.One2many('odoocms.timetable.schedule', 'primary_class_id', 'Timetable')

	def unlink(self):
		for rec in self.sudo():
			if rec.registration_ids:
				raise ValidationError(_("Students are registered in the Primary Class, Class can not be deleted."))
			
			if rec.timetable_ids:
				raise ValidationError(_("Timetable scheduled for the Class, Class can not be deleted."))
			
			grade_class = rec.grade_class_id
			ctx = self.env.context.copy()
			ctx['active_test'] = False
			for component_class in rec.class_ids:
				dropped_components = self.env['odoocms.student.course.component'].sudo().with_context(ctx).search([
					('class_id', '=', component_class.id), ('active', '=', False)])
				dropped_components.unlink()
				component_class.unlink()
			
			dropped_courses = self.env['odoocms.student.course'].sudo().with_context(ctx).search([
				('primary_class_id', '=', rec.id), ('active', '=', False)])
			dropped_courses.unlink()
			
			cross_office_reg_request = self.env['odoocms.course.registration.cross.office'].sudo().with_context(ctx).search([
				('primary_class_id', '=', rec.id)])
			cross_office_reg_request.unlink()
			
			cross_reg_request = self.env['odoocms.course.registration.cross'].sudo().with_context(ctx).search([
				('primary_class_id', '=', rec.id)])
			cross_reg_request.unlink()
			
			reg_line_request = self.env['odoocms.course.registration.line'].sudo().with_context(ctx).search([
				('primary_class_id', '=', rec.id)])
			reg_line_request.unlink()
			
			
			super().unlink()
			grade_class.sudo().unlink()
			

class OdooCMSClass(models.Model):
	_inherit = 'odoocms.class'
	
	timetable_ids = fields.One2many('odoocms.timetable.schedule', 'class_id', 'Timetable')
		

class OdooCMSBatchSection(models.Model):
	_inherit = "odoocms.batch.section"
	
	timetable_ids = fields.One2many('odoocms.timetable.schedule', 'section_id', 'Timetable')


class OdooCMSBatch(models.Model):
	_inherit = "odoocms.batch"
	
	timetable_ids = fields.One2many('odoocms.timetable.schedule', 'batch_id', 'Timetable')


class OdooCMSFacultyStaff(models.Model):
	_inherit = 'odoocms.faculty.staff'
	
	timetable_ids = fields.One2many('odoocms.timetable.schedule', 'faculty_id', 'Timetable')

# access_odoocms_timetable_user,access.odoocms.timetable.user,odoocms_timetable.model_odoocms_timetable,odoocms.group_cms_user,1,1,1,0
# access_odoocms_timetable_manager,access.odoocms.timetable.manager,odoocms_timetable.model_odoocms_timetable,odoocms.group_cms_manager,1,1,1,1

