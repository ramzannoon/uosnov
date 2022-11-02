from datetime import date

from odoo import fields, models, api, _
import pdb


class OdooCMSDiscipline(models.Model):
    _name = 'odoocms.discipline'
    _description = 'CMS Discipline'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Discipline", help="Discipline Name")
    code = fields.Char(string="Code", help="Discipline Code")
    description = fields.Text(string='Description', help="Short Description about the Discipline")
    program_ids = fields.One2many('odoocms.program','discipline_id','Academic Programs')
    
    _sql_constraints = [
        ('code', 'unique(code)', "Code already exists "),
    ]


class OdooCMSCampus(models.Model):
    _name = 'odoocms.campus'
    _description = 'CMS Campus'
    _inherit = ['mail.thread','mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', help='Campus City Code')
    effective_date = fields.Date(string='Effective Date', help='Effective Date of Campus')
    active = fields.Boolean('Active', default=True,
                            help="Current Status of Course")
    description = fields.Text(string='Description', help="Description about the Campus")
    short_description = fields.Text(string='Short Description', help="Short Description about the Campus")
    formal_description = fields.Text(string='Formal Description', help="Formal Description about the Campus")
    street = fields.Char(string='Address 1')
    street2 = fields.Char(string='Address 2')
    zip = fields.Char(change_default=True)
    city = fields.Char('City')
    country_id = fields.Many2one('res.country', string='Country', ondelete='cascade')
    company_id = fields.Many2one('res.company', string='Company')
    institute_ids = fields.One2many('odoocms.institute', 'campus_id', string='Schools')
    faculty_ids = fields.One2many('odoocms.department.line', 'campus_id', string="Faculty")
    is_military=fields.Boolean('Is Military',default=False)
    to_be = fields.Boolean(default=False)
    
    _sql_constraints = [
        ('code', 'unique(code)', "Campus Code already exists."),
    ]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            recs = self.search([('name', operator, name)] + (args or []), limit=limit)
            if not recs:
                recs = self.search([('code', operator, name)] + (args or []), limit=limit)
            return recs.name_get()
        return super().name_search(name, args=args, operator=operator, limit=limit)


class OdooCMSInstitute(models.Model):
    _name = 'odoocms.institute'
    _description = 'CMS Institute'
    _inherit = ['mail.thread', 'mail.activity.mixin','image.mixin']

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True, help='School City Code')
    effective_date = fields.Date(string='Effective Date', help='Effective Date of Institute')
    active = fields.Boolean('Active', default=True, help="Current Status of Institute")
    website = fields.Char(string='Website')
    phone = fields.Char(string='Phone')

    department_ids = fields.One2many('odoocms.department', 'institute_id', string='Departments')
    campus_id = fields.Many2one('odoocms.campus', string='Campus')

    parent_id = fields.Many2one('odoocms.institute', string='Parent School')
    parent_name = fields.Char(related='parent_id.name', readonly=True, string='Parent name')
    child_ids = fields.One2many('odoocms.institute', 'parent_id', string='SubInstitutes',
        domain=[('active', '=', True)])
    faculty_ids = fields.One2many('odoocms.department.line', 'institute_id', string="Faculty")
    to_be = fields.Boolean(default=False)
    
    _sql_constraints = [
        ('code', 'unique(code)', "School Code already exists."), ]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            recs = self.search([('name', operator, name)] + (args or []), limit=limit)
            if not recs:
                recs = self.search([('code', operator, name)] + (args or []), limit=limit)
            return recs.name_get()
        return super().name_search(name, args=args, operator=operator, limit=limit)
    
      
class OdooCMSDepartment(models.Model):
    _name = 'odoocms.department'
    _description = 'CMS Department'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string="Name", help="Department Name", required=True)
    code = fields.Char(string="Code", help="Department Code", required=True)
    effective_date = fields.Date(string="Effective Date", help="Effective Date", required=True)
    color = fields.Integer(string='Color Index')
    active = fields.Boolean('Active', default=True, help="Current Status of Department")
    
    program_ids = fields.One2many('odoocms.program', 'department_id', string="Programs")
    faculty_ids = fields.One2many('odoocms.department.line', 'department_id', string="Faculty")
    
    institute_id = fields.Many2one("odoocms.institute", string="School")
    hod_id = fields.Many2one("hr.employee", string="HOD")
    to_be = fields.Boolean(default=False)
    
    _sql_constraints = [
        ('code', 'unique(code)', "Department Code already exists."), ]

    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.institute_id:
                name = name + ' - ' + record.institute_id.code or ''
            res.append((record.id, name))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            recs = self.search([('name', operator, name)] + (args or []), limit=limit)
            if not recs:
                recs = self.search([('code', operator, name)] + (args or []), limit=limit)
            return recs.name_get()
        return super().name_search(name, args=args, operator=operator, limit=limit)
    

class OdooCMSDepartmentLineTag(models.Model):
    _name = 'odoocms.department.line.tag'
    _description = 'Department Line Tag'

    name = fields.Char(string="Faculty Tag", required=True)
    color = fields.Integer(string='Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]
    
    
class OdooCMSDepartmentLine(models.Model):
    _name = 'odoocms.department.line'
    _description = 'CMS Department Line'
    
    department_id = fields.Many2one('odoocms.department',string='Department')
    faculty_staff_id = fields.Many2one('odoocms.faculty.staff',string='Faculty Staff')
    institute_id = fields.Many2one('odoocms.institute','School',related='department_id.institute_id',store=True,readonly=False)
    campus_id = fields.Many2one('odoocms.campus', 'Campus', related='institute_id.campus_id', store=True,readonly=False)
    employee_id = fields.Many2one('hr.employee',string='Employee')
    employee_name = fields.Char(related = 'employee_id.name', store=True,string='Employee Name')
    employee_work_phone = fields.Char(related = 'employee_id.work_phone', store=True,string='Work Phone')
    employee_work_email = fields.Char(related = 'employee_id.work_email', store=True,string='Work Email')
    employee_department_id = fields.Many2one(related = 'employee_id.department_id', store=True,string='HR Department')
    employee_job_id = fields.Many2one(related = 'employee_id.job_id', store=True,string='Job Position')
    employee_parent_id = fields.Many2one(related = 'employee_id.parent_id', store=True,string='Manager')
    employee_tag_id = fields.Many2many('odoocms.department.line.tag','department_line_tag_rel','department_line_id','tag_id','Tags')
    
    
class OdooCMSCareer(models.Model):
    _name = "odoocms.career"
    _description = "CMS Career"

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    description  = fields.Text(string='Description')
    to_be = fields.Boolean(default=False)
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            recs = self.search([('name', operator, name)] + (args or []), limit=limit)
            if not recs:
                recs = self.search([('code', operator, name)] + (args or []), limit=limit)
            return recs.name_get()
        return super(OdooCMSCareer, self).name_search(name, args=args, operator=operator, limit=limit)


class OdooCMSProgram(models.Model):
    _name = "odoocms.program"
    _description = "CMS Program"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    short_code = fields.Char('Short Code',size=4)
    color = fields.Integer(string='Color Index')
    duration = fields.Char('Duration')
    credits = fields.Integer('Credit Hours')
    effective_date = fields.Date(string="Effective Date", help="Effective Date", required=True)
    description = fields.Text(string='Formal Description')
    active = fields.Boolean('Active', default=True,
                            help="Current Status of Department")
    department_id = fields.Many2one('odoocms.department', string="Department")
    career_id = fields.Many2one('odoocms.career', string="Academic Level")
    discipline_id = fields.Many2one('odoocms.discipline', string="Discipline")
    institute_id = fields.Many2one("odoocms.institute", string="School",related='department_id.institute_id',store=True)
    campus_id = fields.Many2one('odoocms.campus',string='Campus', related='institute_id.campus_id',store=True)
    
    # scheme_ids = fields.Many2many('odoocms.study.scheme', 'scheme_program_rel', 'program_id', 'scheme_id',
    #     string='Study Schemes')
    specialization_ids = fields.One2many('odoocms.specialization', 'program_id', string='Specializations')
    user_ids = fields.Many2many('res.users', 'program_user_access_rel', 'program_id', 'user_id', 'Users', domain="[('share','=', False)]")
    to_be = fields.Boolean(default=False)
    
    #     import_identifier = fields.Many2one('ir.model.data', 'Import Identifier', compute='_get_import_identifier',
#         store=True)
#
    _sql_constraints = [
        ('code', 'unique(code)', "Code already exists "),
    ]

    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.department_id:
                name = name + ' - ' + (record.department_id.institute_id and record.department_id.institute_id.code or '')
            res.append((record.id, name))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            recs = self.search([('name', operator, name)] + (args or []), limit=limit)
            if not recs:
                recs = self.search([('code', operator, name)] + (args or []), limit=limit)
            return recs.name_get()
        return super().name_search(name, args=args, operator=operator, limit=limit)


class OdooCMSSpecialization(models.Model):
    _name = "odoocms.specialization"
    _description = "CMS Specialization"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    description  = fields.Text(string='Formal Description')
    program_id = fields.Many2one('odoocms.program', string='Program')


class OdooCMSBatch(models.Model):
    _name = "odoocms.batch"
    _description = "Program Batches"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence'

    name = fields.Char(string='Batch Name', required=True)
    code = fields.Char(string='Code',copy=False)
    sequence = fields.Integer('Sequence',default=10)
    color = fields.Integer(string='Color Index')
    department_id = fields.Many2one('odoocms.department', string="Department", required=True)
    institute_id = fields.Many2one("odoocms.institute", string="School",related='department_id.institute_id',store=True)
    career_id = fields.Many2one('odoocms.career', string="Academic Level", required=True)
    program_id = fields.Many2one('odoocms.program', string="Program", required=True)
    session_id = fields.Many2one('odoocms.academic.session', 'Academic Session', required=True)
    term_id = fields.Many2one('odoocms.academic.term', 'Current Term')
    term_line = fields.Many2one('odoocms.academic.term.line','Term Line',compute='get_term_line',store=True)
    semester_id = fields.Many2one('odoocms.semester', 'Semester')
    study_scheme_id = fields.Many2one('odoocms.study.scheme', 'Study Scheme', required=True)
    to_be = fields.Boolean(default=False)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code', 'unique(code)', "Code already exists for some other Batch"),
    ]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            recs = self.search([('name', operator, name)] + (args or []), limit=limit)
            if not recs:
                recs = self.search([('code', operator, name)] + (args or []), limit=limit)
            return recs.name_get()
        return super().name_search(name, args=args, operator=operator, limit=limit)
    
    @api.depends('term_id.term_lines','term_id.term_lines.date_start','term_id.term_lines.date_end')
    def get_term_line(self):
        for batch in self:
            term_line = self.env['odoocms.academic.term.line']
            for rec in batch.term_id.term_lines.sorted(key=lambda s: s.sequence,reverse=False):
                term_line = rec
                if rec.campus_ids and batch.program_id.campus_id not in rec.campus_ids:
                    continue
                elif rec.institute_ids and batch.program_id.department_id.institute_id not in rec.institute_ids:
                    continue
                elif rec.career_ids and batch.career_id not in rec.career_ids:
                    continue
                elif rec.program_ids and batch.program_id not in rec.program_ids:
                    continue
                elif rec.batch_ids and batch not in rec.batch_ids:
                    continue
                else:
                    break
            batch.term_line = term_line and term_line.id or False

    def getermline(self,term_id):
        batch = self.sudo()
        term_line = self.env['odoocms.academic.term.line']
        for rec in term_id.term_lines.sorted(key=lambda s: s.sequence, reverse=False).sudo():
            term_line = rec
            if rec.campus_ids and batch.program_id.campus_id not in rec.campus_ids:
                continue
            elif rec.institute_ids and batch.program_id.department_id.institute_id not in rec.institute_ids:
                continue
            elif rec.career_ids and batch.career_id not in rec.career_ids:
                continue
            elif rec.program_ids and batch.program_id not in rec.program_ids:
                continue
            elif rec.batch_ids and batch not in rec.batch_ids:
                continue
            else:
                break
        return term_line and term_line or False
            
    def can_apply(self, event, term_id=False, date_request =False):
        today = date.today() if not date_request else date_request
        can_apply = False
        term_line = self.getermline(term_id) if term_id else self.term_line
        planning_id = term_line.planning_ids.filtered(lambda l: l.type == event)
        if planning_id and (planning_id.date_start <= today <= planning_id.date_end):
            can_apply = True
        return can_apply


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    code = fields.Char(string="Code")


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    faculty_created = fields.Boolean(string="Faculty Created", default=False)
    personal_contact = fields.Char(string="Personal Contact")

    @api.onchange('user_id')
    def onchange_user(self):
        if self.user_id:
            self.work_email = self.user_id.email
            self.identification_id = False
            self.user_id.employee_id = self.id
            fs_id = self.env['odoocms.faculty.staff'].search([('employee_id', '=', self.id)])
            if fs_id:
                self.user_id.faculty_staff_id = fs_id.id
    
    @api.onchange('address_id')
    def onchange_address_id(self):
        if self.address_id:
            self.work_phone = self.address_id.phone
            self.mobile_phone = self.address_id.mobile

    def write(self, vals):
        auto = vals.get('auto', False)
        if auto:
            del vals['auto']
        res = super().write(vals)
        if vals.get('user_id', False) and not auto:
            self.user_id.write({
                'user_type': self._context.get('user_type','employee'),
                'employee_id': self.id,
                'auto': True,
            })
        return res

    def create_faculty(self):
        """
        Create Faculty From Employee
        """
        faculty_recordset = self.env['odoocms.faculty.staff']
        faculty_recordset = faculty_recordset.search([])
        list = []
        for emp in self:
            faculty = self.env['odoocms.faculty.staff'].search([('work_email', '=', emp.work_email)])
            if faculty:
                raise models.ValidationError('Faculty Already Exists!!')
            if not emp.name:
                raise models.ValidationError('Please Fill Out Employee Name!!')
            vals = {
                'first_name': emp.name,
                'work_email': emp.work_email,
                'code': emp.code,
                'employee_id': emp.id,
                'date_of_birth': emp.birthday,
                'nationality': emp.country_id.id,
                'gender': emp.gender,
                'blood_group': emp.blood_group,
                'emergency_contact': emp.emergency_contact
            }
            created = faculty_recordset.create(vals)
            if created:
                self.faculty_created = True


class ResCompany(models.Model):
    _inherit = "res.company"
    
    identifier = fields.Char('Import Identifier')
    
    
class ResUsers(models.Model):
    _inherit = "res.users"
    
    user_type = fields.Selection([('faculty', 'Faculty'), ('student', 'Student'),
                                  ('employee', 'Employee'), ('public', 'Public')], 'User Type', default='employee')
    student_id = fields.Many2one('odoocms.student', 'Student')
    faculty_staff_id = fields.Many2one('odoocms.faculty.staff','Faculty Staff')
    employee_id = fields.Many2one('hr.employee','Related Employee')
    program_ids = fields.Many2many('odoocms.program', 'program_user_access_rel', 'user_id', 'program_id', 'Programs')

    def write(self, vals):
        auto = vals.get('auto', False)
        if auto:
            del vals['auto']
        if vals.get('user_type', False):
            if vals.get('user_type') == 'student':
                vals['employee_id'] = False
                vals['faculty_staff_id'] = False
            if vals.get('user_type') == 'faculty':
                vals['employee_id'] = False
                vals['student_id'] = False
            if vals.get('user_type') == 'employee':
                vals['student_id'] = False
                vals['faculty_staff_id'] = False
        
        res = super().write(vals)
        if vals.get('student_id', False) and not auto:
            self.student_id.write({
                'user_id': self.id,
                'auto': True,
            })
        elif vals.get('faculty_staff_id', False):
            #self.faculty_staff_id.employee_id.resource_id.user_id = self.id
            self.faculty_staff_id.with_context(user_type='faculty').write({
                'user_id': self.id,
                'auto': True,
            })
        elif vals.get('employee_id', False) and not auto:
            #self.employee_id.resource_id.user_id = self.id
            self.employee_id.with_context(user_type='employee').write({
                'user_id': self.id,
                'auto': True,
            })
        
        return res

        
    # @api.onchange('student_id')
    # def onchange_student(self):
    #     if self.student_id:
    #         self.employee_id = False
    #         self.faculty_staff_id = False
    #
    # @api.onchange('employee_id')
    # def onchange_employee(self):
    #     if self.employee_id:
    #         self.faculty_staff_id = False
    #         self.student_id = False
    #
    # @api.onchange('faculty_staff_id')
    # def onchange_faculty_staff(self):
    #     if self.faculty_staff_id:
    #         self.employee_id = False
    #         self.student_id = False
            
    def create_user(self, records, user_group=None):
        for rec in records:
            if not rec.user_id:
                user_vals = {
                    'name': rec.name,
                    'login': rec.email or rec.name,
                    'partner_id': rec.partner_id.id,
                    'password': rec.mobile or '123456',
                    'groups_id': user_group,
                }
                user_id = self.create(user_vals)
                rec.user_id = user_id
                # if user_group:
                #    user_group.users = user_group.users + user_id

