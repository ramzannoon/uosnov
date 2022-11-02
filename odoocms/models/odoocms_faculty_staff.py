from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import pdb


class OdooCMSFacultyStaffTag(models.Model):
    _name = 'odoocms.faculty.staff.tag'
    _description = 'Faculty Staff Tag'

    name = fields.Char(string="Faculty Tag", required=True)
    color = fields.Integer(string='Color Index')
    faculty_staff_ids = fields.Many2many('odoocms.faculty.staff', string='Teachers')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]


class OdooCMSFacultyStaffPosition(models.Model):
    _name = 'odoocms.faculty.staff.position'
    _description = 'Faculty Staff Position'

    name = fields.Char(string="Label", required=True)  # label
    code = fields.Char(string="Reference", required=True)  # reference


class OdooCMSAward(models.Model):
    _name = 'odoocms.award'
    _description = 'Faculty Honor/Awards'
    
    award_type = fields.Selection([
        ('award', 'AWARD'), ('honor', 'HONOR')], string='Honor/Award Type', required=True, default='award')
    
    nomination = fields.Selection([
        ('nust', 'NUST'),
        ('other', 'Other')], string='Nominated By', required=True, default='nust')
    
    status = fields.Selection([
        ('awarded', 'Awarded'),
        ('not awarded', 'Not Awarded')], string='Status', required=True, default='awarded')
    
    awarding_body = fields.Selection([
        ('nust', 'NUST'),
        ('other', 'Other')], string='Awarding Body', required=True, default='nust')
    
    name = fields.Char(string="Name")
    country_id = fields.Many2one('res.country', string='Country')
    date = fields.Date(string="Date of Award")
    description = fields.Text(string="Description")
    certificate = fields.Binary('Certificate', attachment=True)
    
    student_id = fields.Many2one('odoocms.student', string='Student')
    faculty_staff_id = fields.Many2one('odoocms.faculty.staff', string='Faculty')


class OdooCMSFacultyStaff(models.Model):
    _name = 'odoocms.faculty.staff'
    _description = 'CMS Faculty'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'hr.employee': 'employee_id'}

    @api.depends('first_name', 'last_name')
    def _get_faculty_name(self):
        for faculty in self:
            faculty.name = (faculty.first_name or '') + ' ' + (faculty.last_name or '')
            
    def calculate_year_month_mask(self, date_one, date_two):
        '''
        Function returns Date string:
        Format:
            XY - XM - XD i.e. X are numbers computed from date_one and date_two
        Pass Your Dates to get the masked date
        '''
        if not type(date_one) or type(date_two) == type(date):
            return False
        rdelta = relativedelta(date_two, date_one)
        date_masked = str(rdelta.years) + 'Y - ' + str(rdelta.months) + 'M - ' + str(rdelta.days) + 'D'
        return date_masked
    
    code1 = fields.Char(string="Code1")
    first_name = fields.Char(string='Name')
    last_name = fields.Char(string='Last Name')
    date_of_birth = fields.Date(string="Date Of birth")
    father_name = fields.Char(string="Father")
    
    nationality = fields.Many2one('res.country', 'Nationality')
    # degree = fields.Many2one('hr.recruitment.degree', string="Degree", Help="Select your Highest degree")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
                              string='Gender', required=True, default='male', tracking=True)
    blood_group = fields.Selection([('a+', 'A+'), ('a-', 'A-'), ('b+', 'B+'), ('b-', 'B-'), ('o+', 'O+'), ('o-', 'O-'),
                                    ('ab-', 'AB-'), ('ab+', 'AB+')],
                                   string='Blood Group', required=True, default='a+', tracking=True)

    tag_ids = fields.Many2many('odoocms.faculty.staff.tag', 'faculty_staff_tag_rel', 'faculty_staff_id', 'tag_id',
                               string='Tag')
    # subject_ids = fields.Many2many('odoocms.subject', string='Subject(s)', tracking=True)
    employee_id = fields.Many2one('hr.employee', 'Linked Employee', required=True, ondelete="cascade")
    birthday = fields.Date('Date of Birth', related='employee_id.birthday', readonly=True, store=True)
    mobile_phone = fields.Char('Mobile (Primary)', related='employee_id.mobile_phone', readonly=True, store=True)
    phone = fields.Char('Mobile (Secondary)', related='employee_id.phone', readonly=True, store=True)
    work_phone = fields.Char('Land Line (Res)', related='employee_id.work_phone', readonly=True, store=True)
    work_email = fields.Char('Email (Official)', related='employee_id.work_email', readonly=True, store=True)
    private_email = fields.Char('Email', related='employee_id.private_email', readonly=True, store=True)
    work_location = fields.Char('University Mailing Address', related='employee_id.work_location', readonly=True, store=True)
    emergency_contact = fields.Char('Emergency Contact', related='employee_id.emergency_contact', readonly=True, store=True)
    emergency_phone = fields.Char('Emergency Phone', related='employee_id.emergency_phone', readonly=True, store=True)
    # ----------------------------------------------------
    partner_id = fields.Many2one('res.partner', 'Partner', required=False, ondelete="cascade")
    emp_age = fields.Char(string='Age', compute='_compute_employee_age', readonly=True, store=True, help="Employee Age")
    
    login = fields.Char('Login', related='employee_id.user_id.login', readonly=1, store=True)
    last_login = fields.Datetime('Latest Connection', readonly=1, related='employee_id.user_id.login_date')

    #login = fields.Char('Login', related='partner_id.user_id.login', readonly=1, store=True)
    #last_login = fields.Datetime('Latest Connection', readonly=1, related='partner_id.user_id.login_date')

    unitimeId = fields.Integer()
    position_id = fields.Many2one('odoocms.faculty.staff.position', 'Position')

    award_ids = fields.One2many('odoocms.award','faculty_staff_id','Awards')
    publication_ids = fields.One2many('odoocms.publication', 'faculty_staff_id', 'Publications')
    language_ids = fields.Many2many('odoocms.language', string='Languages')
    extra_activity_ids = fields.One2many('odoocms.extra.activity', 'faculty_staff_id', 'Activites')
    school_id = fields.Many2one('odoocms.institute', string='School')

    @api.depends('employee_id.birthday')
    def _compute_employee_age(self):
        for record in self:
            age = ''
            if record.employee_id.birthday:
                age = record.calculate_year_month_mask(record.employee_id.birthday, date.today())
            record.emp_age = age
            
    def sync_unitime_odoo(self, instructors):
        for instructor in instructors:
            position = self.env['odoocms.faculty.staff.position'].search(
                [('code', '=', instructor['position']['reference'])])
            if not position:
                position = self.env['odoocms.faculty.staff.position'].create({
                    'name': instructor['position']['label'],
                    'code': instructor['position']['reference'],
                })
            dept = self.env['odoocms.department'].search([('code', '=', instructor['deptcode'])])
            data = {
                'unitimeId': instructor['unitimeId'],
                'first_name': instructor['first_name'],
                'last_name': instructor['last_name'],
                'name': instructor.get('first_name', '') + ' ' + instructor.get('last_name', ''),
                'position_id': position.id,
                'department_id': dept.id,
            }
            pattern = self.env['odoocms.faculty.staff'].search([('unitimeId', '=', instructor['unitimeId'])])
            if pattern:
                pattern.write(data)
            else:
                pattern = self.env['odoocms.faculty.staff'].create(data)
    
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.code:
                name = record.code + ' - ' + name
            # if record.institute:
            #     name += ' - ' + record.institute.code or ''
            res.append((record.id, name))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            recs = self.search([('name', operator, name)] + (args or []), limit=limit)
            if not recs:
                recs = self.search([('code', operator, name)] + (args or []), limit=limit)
                #recs = self.search(['|', ('code', operator, name), ('code', operator, name)] + (args or []), limit=limit)
            return recs.name_get()
        return super().name_search(name, args=args, operator=operator, limit=limit)

    @api.model
    def create(self, vals):
        if vals.get('first_name', False) or vals.get('last_name', False):
            vals['name'] = vals.get('first_name', '') + ' ' + vals.get('last_name', '')
        res = super().create(vals)
        return res

    def write(self, vals):
        auto = vals.get('auto', False)
        if auto:
            del vals['auto']
        if vals.get('first_name', False) or vals.get('last_name', False):
            vals['name'] = vals.get('first_name', self.first_name) + ' ' + vals.get('last_name', self.last_name)

        res = super().write(vals)
        if vals.get('user_id',False) and not auto:
            self.user_id.write({
                'user_type': self._context.get('user_type','faculty'),
                'faculty_staff_id': self.id,
                'auto': True,
            })
        return res

    @api.constrains('date_of_birth')
    def _check_birthdate(self):
        for record in self:
            if record.date_of_birth and record.date_of_birth > fields.Date.today():
                raise ValidationError(_(
                    "Birth Date can't be greater than Current Date!"))

    def create_user(self):
        group_portal = self.env.ref('base.group_portal')
        for record in self:
            if not record.user_id or len(record.user_id) == 0:
                data = {
                    'name': record.name,
                    'partner_id': record.employee_id.user_partner_id.id,
                    'faculty_staff_id': record.id,
                    'user_type': 'faculty',
                    'login': record.work_email,
                    'password': record.mobile_phone or '123456',
                    'image_1920': record.image_1920,
                    'email': record.work_email,
                    'groups_id': group_portal,
                }
                user = self.env['res.users'].create(data)
                record.user_id = user.id
    
    # def create_employee(self):
    #     for record in self:
    #         vals = {
    #             'name': record.name,
    #             'country_id': record.nationality.id,
    #             'gender': record.gender,
    #             #'address_home_id': record.employee_id.partner_id.id,
    #             'birthday': record.date_of_birth,
    #             'image': record.image,
    #             'work_phone': record.phone,
    #             'work_mobile': record.mobile,
    #             'work_email': record.email,
    #         }
    #         if not record.employee_id or len(record.employee_id) == 0:
    #             emp_id = self.env['hr.employee'].create(vals)
    #             record.write({'employee_id': emp_id.id})
    #
    #         if not record.user_id or len(record.user_id) == 0:
    #             record.create_user()
    #         record.employee_id.user_id = record.user_id
    #         record.user_id = record.user_id
    #         record.employee_id.user_partner_id.write({'employee': True})


    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Faculty Staff'),
            'template': '/odoocms/static/xls/odoocms_faculty_staff.xls'
        }]


class WizardFacultyEmployee(models.TransientModel):
    _name = 'wizard.faculty.employee'
    _description = "Create Employee and User of Faculty"

    user_boolean = fields.Boolean("Want to create User too ?", default=True)

    def create_employee(self):
        for record in self:
            active_id = self.env.context.get('active_ids', []) or []
            faculty = self.env['odoocms.faculty.staff'].browse(active_id)
            faculty.create_employee()
            if record.user_boolean and not faculty.user_id:
                group_portal = self.env.ref('base.group_portal')
                self.env['res.users'].create_user(faculty, group_portal)
                faculty.employee_id.user_id = faculty.user_id
