from odoo import fields, models, _, api
import pdb
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class OdooCMSMigrationmigration(models.Model):
	_name = 'odoocms.migration'
	_description = 'migrations for the Migration'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_order = 'id desc'
	
	READONLY_STATES = {
		'approve': [('readonly', True)],
		'open': [('readonly', True)],
		'done': [('readonly', True)],
		'reject': [('readonly', True)],
	}
	
	@api.depends('first_name', 'last_name')
	def _get_applicant_name(self):
		for applicant in self:
			applicant.name = (applicant.first_name or '') + ' ' + (applicant.last_name or '')
	
	domicile = fields.Char(string='Domicile',states=READONLY_STATES)
	first_name = fields.Char(string='First Name', help="First name of Student",states=READONLY_STATES)
	last_name = fields.Char(string='Last Name', help="Last name of Student",states=READONLY_STATES)
	name = fields.Char('Name',compute='_get_applicant_name',store=True)
	cnic = fields.Char(string='CNIC')
	image = fields.Binary(string='Image', attachment=True, help="Provide the image of the Student")

	email = fields.Char(string='Email')
	phone = fields.Char(string='Phone')
	mobile = fields.Char(string='Mobile')
	
	father_name = fields.Char(string="Father Name")
	religion_id = fields.Many2one('odoocms.religion', string="Religion")
	date_of_birth = fields.Date(string="Date Of Birth")
	gender = fields.Selection([('m', 'Male'), ('f', 'Female'), ('o', 'Other')],
		string='Gender', default='m', tracking=True) 
	nationality = fields.Many2one('res.country', string='Nationality', ondelete='restrict',
		help="Select the Nationality")
	active = fields.Boolean(string='Active', default=True)
	academic_session_id = fields.Many2one('odoocms.academic.session','Academic Session',store=True)
	career_id = fields.Many2one('odoocms.career','Academic Level',store=True)
	program_id = fields.Many2one('odoocms.program','Academic Program', tracking=True, readonly=True, states={'draft': [('readonly', False)]})
	campus_id = fields.Many2one('odoocms.campus',string='Campus',related='program_id.department_id.campus_id',store=True)
	semester_id = fields.Many2one('odoocms.semester','Current Semester', tracking=True, readonly=True, states={'draft': [('readonly', False)]})
	company_id = fields.Many2one('res.company', string='School', default=lambda self: self.env.user.company_id)
	street = fields.Char(string='Street', help="Enter the First Part of Address")
	street2 = fields.Char(string='Street2', help="Enter the Second Part of Address")
	city = fields.Char(string='City', help="Enter the City Name")
	zip = fields.Char(change_default=True)
	state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
		domain="[('country_id', '=?', country_id)]")
	country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', help="Select the Country")
	
	is_same_address = fields.Boolean(string="Permanent Address same as above", default=False, help="Tick the field if the Present and permanent address is same")
	per_street = fields.Char(string='Per. Street', help="Enter the First Part of Permanenet Address")
	per_street2 = fields.Char(string='Per. Street2', help="Enter the First Part of Permanent Address")
	per_city = fields.Char(string='Per. City', help="Enter the City Name of Permanent Address")
	per_zip = fields.Char(change_default=True)
	per_state_id = fields.Many2one("res.country.state", string='Per State', ondelete='restrict',
		domain="[('country_id', '=?', per_country_id)]")
	per_country_id = fields.Many2one('res.country', string='Per. Country', ondelete='restrict', help="Select the Country")

	description = fields.Text(string="Note")
	entryID = fields.Char('Entry ID',states=READONLY_STATES)
	academic_semester_id = fields.Many2one('odoocms.academic.semester','Current Academic Term', tracking=True, readonly=True, states={'draft': [('readonly', False)]})
	state = fields.Selection([('draft','Draft'),('reject','Reject'),('approve','Approve')],'Status',default='draft')
	migration_line_ids = fields.One2many('odoocms.migration.line','migration_id','Result')







	def create_student(self, view=False):
		if not self.date_of_birth:
			raise UserError('Data of Birth of %s - %s not Set.' % (self.entryID,self.name))
		
		semester = self.env['odoocms.semester'].search([('number', '=', 1)], limit=1)
		user = self.env['res.users'].search([('login', '=', self.entryID)])
		
		
		values = {
			'state': 'enroll',
			'name': self.name,
			'first_name': self.first_name,
			'last_name': self.last_name,
			'father_name': self.father_name,
			
			'cnic': self.cnic,
			'gender': self.gender,
			'date_of_birth': self.date_of_birth,
			'religion_id': self.religion_id.id,
			'nationality': self.nationality.id,
			
			'email': self.email,
			'mobile': self.mobile,
			'phone': self.phone,
			'image': self.image,
			
			'id_number': self.entryID,
			'entryID': self.entryID,
			
			'street': self.street,
			'street2': self.street2,
			'city': self.city,
			'zip': self.zip,
			'state_id': self.state_id.id,
			'country_id': self.country_id.id,
			
			'is_same_address': self.is_same_address,
			'per_street': self.per_street,
			'per_street2': self.per_street2,
			'per_city': self.per_city,
			'per_zip': self.per_zip,
			'per_state_id': self.per_state_id.id,
			'per_country_id': self.per_country_id.id,
			
			'career_id': self.career_id.id,
			'program_id': self.program_id.id,
			'academic_session_id': self.academic_session_id.id,
			'academic_semester_id': self.academic_semester_id.id,
			'semester_id': semester.id,
			
			# 'admission_no': ,
			'company_id': self.company_id.id,
		}
		if user:
			values['partner_id'] = user.partner_id.id
		if not self.is_same_address:
			pass
		else:
			values.update({
				'per_street': self.street,
				'per_street2': self.street2,
				'per_city': self.city,
				'per_zip': self.zip,
				'per_state_id': self.state_id.id,
				'per_country_id': self.country_id.id,
			})

		student = self.env['odoocms.student'].create(values)
		self.write({
			'state': 'approve',
			'student_id': student.id,
		})
		create_semester= self.env['odoocms.student.semester'].create({
			'student_id': student.id,
			'academic_semester_id':self.academic_semester_id.id,
			'semester_id' :1,
			})

		for rec in self.migration_line_ids:
			if rec.state=='accept':
				create_student_subject= self.env['odoocms.student.subject'].create({
					'student_id': student.id,
					'academic_semester_id':self.academic_semester_id.id,
					'semester_id' :1,
					'student_semester_id':create_semester.id,
					'course_code':rec.equ_code,
					'course_name':rec.equ_subject_id.name,
					'credits':rec.equ_subject_id.weightage,
					'grade': rec.equivalent_grade,
					'gpa': rec.equ_gpa,

					})
			
		
			
		if view:
			return {
				'name': _('Student'),
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'odoocms.student',
				'type': 'ir.actions.act_window',
				'res_id': student.id,
				'context': self.env.context
			}
		else:
			return student
	




class OdooCMSMigrationmigrationLine(models.Model):
	_name = 'odoocms.migration.line'
	_description = 'migrations for the Migration Line'

	subject = fields.Char('Subject')
	code = fields.Char('Subject Code')
	gpa = fields.Float('GPA', digits=(8, 2))
	grade = fields.Char('Grade',size=5)
	equ_subject_id = fields.Many2one('odoocms.subject',string='Equivalent Subject', required=True, tracking=True)
	equ_code = fields.Char(related='equ_subject_id.code',string='Equivalent Subject Code')
	equ_gpa = fields.Float('Equivalent GPA', digits=(8, 2))
	equivalent_grade = fields.Char('Equivalent Grade',size=5)
	
	state = fields.Selection([('draft','Draft'),('reject','Reject'),('accept','Accept')],'Status',default='draft')
	migration_id = fields.Many2one('odoocms.migration',string='Migration')

@api.onchange('code')
def _get_subject(self):
	for rec in self:
		
		subject_ids_ids = self.env['odoocms.subject'].search([('code','=',rec.code)])
		if subject_ids_ids:
			rec.equ_subject_id =subject_ids_ids.mapped('id')


