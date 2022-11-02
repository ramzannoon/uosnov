import pdb
from datetime import datetime, date
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class OdooCMSStudentTermDefer(models.Model):
	_name = "odoocms.student.term.defer"
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description = "Student Term Defer"
	_rec_name = 'student_id'
	
	READONLY_STATES = {
		'submit': [('readonly', True)],
		'approve': [('readonly', True)],
		'done': [('readonly', True)],
		'cancel': [('readonly', True)],
	}
	
	student_id = fields.Many2one('odoocms.student', string="Student",states=READONLY_STATES)
	program_id = fields.Many2one('odoocms.program' ,string='Academic Program',related='student_id.program_id',store=True)
	batch_id = fields.Many2one('odoocms.batch' ,string='Batch',related='student_id.batch_id',store=True)
	section_id = fields.Many2one('odoocms.batch.section',string='Class Section', related='student_id.section_id', store=True)
	semester_id = fields.Many2one('odoocms.semester', string='Current Semester', related='student_id.semester_id', store=True)
	career_id = fields.Many2one('odoocms.career',string='Academic Level',related='student_id.career_id', store=True)
	current_term_id = fields.Many2one('odoocms.academic.term', string='Current Term', related='student_id.term_id', store=True)
	term_seq = fields.Integer(related='current_term_id.number',store=True)
	
	term_id = fields.Many2one('odoocms.academic.term' ,string='Term to Defer',states=READONLY_STATES)
	reason = fields.Text(string='Reason',states=READONLY_STATES)
	bypass = fields.Boolean('ByPass Approval Process',states=READONLY_STATES)
	
	invoice_id = fields.Many2one('account.move', 'Invoice')
	invoice_status = fields.Selection(string='Invoice Status',related='invoice_id.state', tracking=True)
	
	can_defer = fields.Boolean('Can Defer', compute='_can_defer', tracking=True)
	state = fields.Selection([('draft' ,'Draft'), ('submit' ,'Submitted'), ('approve' ,'Approved'), ('done' ,'Done'), ('cancel' ,'Canceled')]
		,default='draft' ,string="Status" ,tracking=True)
	
	def _can_defer(self):
		can_defer = False
		if self.state == 'approve':
			if self.invoice_id and self.invoice_status == 'paid':
				can_defer = True
			else:
				# sm_defer_receipt_type = self.env['ir.config_parameter'].sudo().get_param('odoocms_registration.sm_defer_receipt_type')
				#
				# if not sm_defer_receipt_type:
				# 	raise UserError('Please configure the Term Defer Receipt Type in Global Settings')
				# sm_defer_receipt_type = self.env['odoocms.receipt.type'].search([('id','=',sm_defer_receipt_type)])
				# if not sm_defer_receipt_type.fee_head_ids:
				# 	raise UserError('Please configure heads with Receipt Type.')
				#
				# fee_structure = self.env['odoocms.fee.structure'].search([
				# 	('academic_session_id','=',self.student_id.academic_session_id.id),
				# 	('career_id','=',self.student_id.career_id.id)
				# ])
				#
				# fee_amount = 0
				# if fee_structure and fee_structure.line_ids and fee_structure.line_ids.filtered(lambda l: l.fee_head_id.id == sm_defer_receipt_type.fee_head_ids[0].id):
				# 	fee_amount = fee_structure.line_ids.filtered(lambda l: l.fee_head_id.id == sm_defer_receipt_type.fee_head_ids[0].id).fee_amount
				# if fee_amount <= 0:
				# 	can_defer = True
				can_defer = True
		self.can_defer = can_defer

	def action_invoice(self):
		sm_defer_receipt_type = self.env['ir.config_parameter'].sudo().get_param('odoocms_registration.sm_defer_receipt_type')
		if not sm_defer_receipt_type:
			raise UserError('Please configure the Term Defer Receipt Type in Global Settings')
		sm_defer_receipt_type = self.env['odoocms.receipt.type'].search([('id','=',sm_defer_receipt_type)])
		if not sm_defer_receipt_type.fee_head_ids:
			raise UserError('Please configure heads with Receipt Type.')

		fee_structure = self.env['odoocms.fee.structure'].search([
			('academic_session_id','=',self.student_id.academic_session_id.id),
			('career_id','=',self.student_id.career_id.id)
		])

		fee_amount = 0
		if fee_structure and fee_structure.line_ids and fee_structure.line_ids.filtered(lambda l: l.fee_head_id.id == sm_defer_receipt_type.fee_head_ids[0].id):
			fee_amount = fee_structure.line_ids.filtered(lambda l: l.fee_head_id.id == sm_defer_receipt_type.fee_head_ids[0].id).fee_amount
		# sm_defer_receipt_type.fee_head_ids[0].

		if fee_amount > 0:
			view_id = self.env.ref('odoocms_fee.view_odoocms_generate_invoice_form')
			return {
				'name': _('Term Defer Invoice'),
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'odoocms.generate.invoice',
				'view_id': view_id.id,
				'views': [(view_id.id, 'form')],
				'context': {
					'default_fixed_type': True,
					'default_receipt_type_ids': [(4, sm_defer_receipt_type.id, None)]},
				'target': 'new',
				'type': 'ir.actions.act_window'
			}
		return {'type': 'ir.actions.act_window_close'}

	def action_submit_portal(self):
		for rec in self:
			activity = self.env.ref('odoocms_registration.mail_act_term_defer')
			self.activity_schedule('odoocms_registration.mail_act_term_defer', user_id=activity._get_role_users(self.program_id))
			rec.state = 'submit'

	def action_submit(self):
		for rec in self:
			exist_recs = self.env['odoocms.student.term.defer'].search([('student_id','=',rec.student_id.id),('state','in',('submit','approve','done'))])
			if len(exist_recs) >= 2:
				raise UserError('Two Defered records already exist')
			
			if rec.bypass:
				rec.defer_term()
			else:
				activity = self.env.ref('odoocms_registration.mail_act_term_defer')
				self.activity_schedule('odoocms_registration.mail_act_term_defer', user_id=activity._get_role_users(self.program_id))
				rec.state = 'submit'

	def action_approve(self):
		for rec in self:
			rec.state = 'approve'

	def action_cancel(self):
		for rec in self:
			rec.state = 'cancel'

	def defer_term(self):
		deferred_tag = self.env['odoocms.student.tag'].search([('name', '=', 'Deferred')])
		if not deferred_tag:
			values = {
				'name': 'Deferred',
				'code': 'deferred',
			}
			deferred_tag = self.env['odoocms.student.tag'].create(values)
			
		for rec in self:
			student_course = self.env['odoocms.student.course'].search([
				('student_id','=',rec.student_id.id),
				('term_id','=', rec.term_id.id),
				('course_type','in',('compulsory','elective','additional','alternate','minor',))
			])
			if student_course:
				student_course.unlink()
			rec.state = 'done'
			
			tags = rec.student_id.tag_ids + deferred_tag
			rec.student_id.write({
				'tag_ids': [[6, 0, tags.ids]]
			})


class OdooCMSStudentTermResume(models.Model):
	_name = "odoocms.student.term.resume"
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description = "Student Term Resume"
	
	READONLY_STATES = {
		'submit': [('readonly', True)],
		'approve': [('readonly', True)],
		'done': [('readonly', True)],
		'cancel': [('readonly', True)],
	}

	student_id = fields.Many2one('odoocms.student', string="Student",states=READONLY_STATES)
	program_id = fields.Many2one(related='student_id.program_id',string='Academic Program')
	batch_id = fields.Many2one(related='student_id.batch_id',string='Class Batch')
	section_id = fields.Many2one(related='student_id.section_id',string='Class Section')
	term_id = fields.Many2one(related='student_id.term_id',string='Academic Term')
	semester_id  = fields.Many2one(related='student_id.semester_id',string='Current Semester')
	
	invoice_id = fields.Many2one('account.move', 'Invoice')
	invoice_status = fields.Selection(string='Invoice Status', related='invoice_id.state', tracking=True)
	can_approve = fields.Boolean('Can Approve', compute='_can_approve', tracking=True)
	
	state = fields.Selection([('draft', 'Draft'), ('submit' ,'Submitted'), ('approve', 'Approved'), ('done', 'Done'), ('cancel', 'Canceled')]
		, default='draft', string="Status", tracking=True)
	
	def _can_approve(self):
		can_approve = False
		if self.state == 'submit':
			# if self.invoice_id and self.invoice_status == 'paid':
			can_approve = True
		self.can_approve = can_approve

	# Later on Will do same as done for defer
	
	# def action_invoice(self):
	# 	sm_resume_receipt_type = self.env['ir.config_parameter'].sudo().get_param('odoocms_registration.sm_resume_receipt_type')
	# 	if not sm_resume_receipt_type:
	# 		raise UserError('Please configure the Term Un-Defer Receipt Type in Global Settings')
	#
	# 	view_id = self.env.ref('odoocms_fee.view_odoocms_generate_invoice_form')
	# 	return {
	# 		'name': _('Term Un-Defer Invoice'),
	# 		'view_type': 'form',
	# 		'view_mode': 'form',
	# 		'res_model': 'odoocms.generate.invoice',
	# 		'view_id': view_id.id,
	# 		'views': [(view_id.id, 'form')],
	# 		'context': {
	# 			'default_fixed_type': True,
	# 			'default_receipt_type_ids': [(4, eval(sm_resume_receipt_type), None)]},
	# 		'target': 'new',
	# 		'type': 'ir.actions.act_window'
	# 	}

	def action_invoice(self):
		sm_resume_receipt_type = self.env['ir.config_parameter'].sudo().get_param('odoocms_registration.sm_resume_receipt_type')
		if not sm_resume_receipt_type:
			return {'type': 'ir.actions.act_window_close'}
		sm_resume_receipt_type = self.env['odoocms.receipt.type'].search([('id','=',sm_resume_receipt_type)])

		if not sm_resume_receipt_type.fee_head_ids:
			raise UserError('Please configure heads with Receipt Type.')

		fee_structure = self.env['odoocms.fee.structure'].search([
			('academic_session_id','=',self.student_id.academic_session_id.id),
			('career_id','=',self.student_id.career_id.id)
		])

		fee_amount = 0
		if fee_structure and fee_structure.line_ids and fee_structure.line_ids.filtered(lambda l: l.fee_head_id.id == sm_resume_receipt_type.fee_head_ids[0].id):
			fee_amount = fee_structure.line_ids.filtered(lambda l: l.fee_head_id.id == sm_resume_receipt_type.fee_head_ids[0].id).fee_amount
		# sm_resume_receipt_type.fee_head_ids[0].

		if fee_amount > 0:
			view_id = self.env.ref('odoocms_fee.view_odoocms_generate_invoice_form')
			return {
				'name': _('Term Un-Defer Invoice'),
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'odoocms.generate.invoice',
				'view_id': view_id.id,
				'views': [(view_id.id, 'form')],
				'context': {
					'default_fixed_type': True,
					'default_receipt_type_ids': [(4, sm_resume_receipt_type.id, None)]},
				'target': 'new',
				'type': 'ir.actions.act_window'
			}
		return {'type': 'ir.actions.act_window_close'}

	def action_submit(self):
		for rec in self:
			rec.state = 'submit'

	def resume_term(self):
		for rec in self:
			rec.state = 'done'
			rec.student_id.state = 'enroll'


class OdooCMSWithDrawReason(models.Model):
	_name = "odoocms.drop.reason"
	_description = "Course Drop Reason"
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name = fields.Char(string='name')
	description = fields.Text(string='Description Text', required = True)


class OdooCMSStudentCourse(models.Model):
	_inherit = "odoocms.student.course"
	
	delete_id = fields.Many2one('odoocms.student.course.delete', 'Delete ID')
	
	def remove_attendance(self, component,date_effective):
		pass
	
	
class OdooCMSCourseDrop(models.Model):
	_name = "odoocms.student.course.drop"
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description = "Student Course Drop"
	_order = 'name desc'

	READONLY_STATES = {
		'submit': [('readonly', True)],
		'approve': [('readonly', True)],
		'done': [('readonly', True)],
		'cancel': [('readonly', True)],
	}

	name = fields.Char(string='Reference', required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
	student_id = fields.Many2one('odoocms.student', string="Student",tracking=True,states=READONLY_STATES)
	program_id = fields.Many2one(related='student_id.program_id',string='Academic Program',states=READONLY_STATES)
	batch_id = fields.Many2one(related='student_id.batch_id',string='Class Batch',states=READONLY_STATES)
	section_id = fields.Many2one(related='student_id.section_id',string='Class Section',states=READONLY_STATES)
	term_id = fields.Many2one(related='batch_id.term_id',string='Academic Term',states=READONLY_STATES)
	semester_id  = fields.Many2one(related='student_id.semester_id',string='Current Semester',states=READONLY_STATES)
	
	registration_id  = fields.Many2one('odoocms.student.course',string='Withdraw/Drop Course',tracking=True,states=READONLY_STATES)
	description = fields.Text(string='Description',states=READONLY_STATES)
	reason_id  = fields.Many2one('odoocms.drop.reason',string='Reason',states=READONLY_STATES)
	date_request = fields.Date('Request Date', default=date.today(), readonly=True)
	date_effective = fields.Date('Effective Date', default=date.today())
	date_approve = fields.Date(string='Approve Date', readonly=True)
	state = fields.Selection([
		('draft','Draft'),
		('submit','Submit'),
		('approve','Approved'),
		('cancel','Cancel')],default='draft',string="Status",tracking=True)
	
	override_min_limit = fields.Boolean('Override Minimum Limit?', default=False, states=READONLY_STATES, tracking=True)
	limit_error = fields.Boolean('Over Limit', default=False)
	limit_error_text = fields.Text(default='')
	
	@api.model
	def create(self, vals):
		if vals.get('name', _('New')) == _('New'):
			vals['name'] = self.env['ir.sequence'].next_by_code('odoocms.student.course.drop') or _('New')
			result = super().create(vals)
		return result
	
	def action_submit(self):
		for rec in self:
			rec._min_register_limit()
			if self.limit_error:
				return
			rec.state = 'submit'
	
	def action_approve(self):
		for rec in self:
			self._min_register_limit()
			if rec.limit_error:
				return
			if rec.state == 'submit':
				if rec.term_id and rec.batch_id and rec.batch_id.can_apply('drop_f', rec.term_id, rec.date_effective):
					rec.registration_id.write({
						'grade': 'F',
						'dropped': True,
						'state': 'done',
					})
				elif rec.term_id and rec.batch_id and rec.batch_id.can_apply('drop_w', rec.term_id, rec.date_effective):
					rec.registration_id.write({
						'grade': 'W',
						'dropped': True,
						'state': 'done',
						'include_in_cgpa': False,
					})
				elif rec.term_id and rec.batch_id and rec.batch_id.can_apply('enrollment', rec.term_id, rec.date_effective):
					rec.registration_id.write({
						'active': False,
						'dropped': True,
						'state': 'dropped',
						'dropped_date': datetime.now(),
					})
				else:
					raise UserError('Date Over for Course Drop!')
				
				for component in rec.registration_id.component_ids:
					rec.registration_id.remove_attendance(component, rec.date_effective)
					component.active = False
				
				rec.state ='approve'
			else:
				raise UserError('Request is not confirmed yet. Please Submit the request first!')

	def action_cancel(self):
		for rec in self:
			rec.state = 'cancel'
	
	def _min_register_limit(self):
		registered_courses = self.env['odoocms.student.course'].search([
			('student_id', '=', self.student_id.id), ('term_id', '=', self.term_id.id), ('grade', 'not in', ('W', 'F'))])
		
		min_credits = 0
		sum_credit = 0
		
		for course in registered_courses:
			sum_credit += course.primary_class_id.credits
			
		sum_credit -= self.registration_id.primary_class_id.credits
		
		# Allowed
		global_load = self.env['odoocms.student.registration.load'].search([
			('type', '=', self.term_id.type), ('default_global', '=', True)])
		if global_load:
			min_credits = global_load.min
		
		career_load = self.student_id.career_id.registration_load_ids.filtered(lambda l: l.type == self.term_id.type)
		if career_load:
			min_credits = career_load.min if career_load.min > 0 else min_credits
		
		batch_load = self.student_id.batch_id.registration_load_ids.filtered(lambda l: l.type == self.term_id.type)
		if batch_load:
			min_credits = batch_load.min if batch_load.min > 0 else min_credits
		
		program_load = self.student_id.program_id.registration_load_ids.filtered(lambda l: l.type == self.term_id.type)
		if program_load:
			min_credits = program_load.min if program_load.min > 0 else min_credits
		
		student_load = self.student_id.registration_load_ids.filtered(lambda l: l.type == self.term_id.type)
		if student_load:
			min_credits = student_load.min if student_load.min > 0 else min_credits
		
		if sum_credit < min_credits and not self.override_min_limit:
			self.limit_error = True
			self.limit_error_text = 'Registration of (%s) Credits is not possible. Minimum Allowed limit: (%s) CH' % (sum_credit, min_credits)
		
		else:
			self.limit_error = False
			self.limit_error_text = ''
			

	

class OdooCMSRequestStudentProfile(models.Model):
	_name = "odoocms.request.student.profile"
	_description = "Student Profile Change Request"
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_rec_name = 'student_id'

	READONLY_STATES = {
		'done': [('readonly', True)],
		'reject': [('readonly', True)],
	}

	student_id = fields.Many2one('odoocms.student', string="Student", states=READONLY_STATES)
	change_in = fields.Char(string='Change In', states=READONLY_STATES)
	old_info = fields.Char(string='Old Information', states=READONLY_STATES)
	new_info = fields.Char(string='New Information', states=READONLY_STATES)
	image_newspaper = fields.Binary(string='NewsPaper Image', attachment=True, states=READONLY_STATES)
	image_cnic = fields.Binary(string='CNIC Image', attachment=True, states=READONLY_STATES)
	state = fields.Selection([('draft','Draft'),('reject','Rejected'),('done','Done')], default ='draft', string='State')

	def action_approve(self):
		if self.state == 'draft':
			self.student_id[self.change_in] = self.new_info
			self.state = 'done'

	def action_reject(self):
		if self.state == 'draft':
			self.state = 'reject'


class OdooCMSCourseDelete(models.Model):
	_name = "odoocms.student.course.delete"
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description = "Delete Students Course"


	name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
					   states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
	date_request = fields.Date(string='Request Date', default=date.today(), readonly=True)
	date_effective = fields.Date(string='Effective Date', default=date.today())
	date_approve = fields.Date(string='Approve Date', readonly=True)
	description = fields.Text(string='Detailed Reason', required=True, )

	registration_ids = fields.Many2many('odoocms.student.course', 'student_course_delete_rel', 'request_id',
										'course_id', )
	deleted_ids = fields.One2many('odoocms.student.course', 'delete_id', string='Deleted Courses',

								  domain=['|', ('active', '=', True), ('active', '=', False)],
								  context={'active_test': False})

	state = fields.Selection([(
		'draft', 'Draft'),
		('submit', 'Submit'),
		('approve', 'Approved'),
		('cancel', 'Cancel'), ], default='draft', string="Status", tracking=True)






