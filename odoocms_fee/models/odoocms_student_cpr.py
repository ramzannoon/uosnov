from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import pdb
from datetime import date


class OdoocmsStudentCPRRegister(models.Model):
    _name = 'odoocms.student.cpr.register'
    _description = 'CPR Register'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', tracking=True, index=True)
    sequence = fields.Char('Sequence')
    date = fields.Date('Date', default=fields.Date.today(), tracking=True, index=True)
    bank_name = fields.Char('Bank', tracking=True)
    branch_name = fields.Char('Branch Name', tracking=True)
    cpr_no = fields.Char('CPR No', tracking=True)
    total_students = fields.Integer('Total Students', compute='_compute_total_student', store=True)
    total_amount = fields.Float('Total Deposited Amount', compute='_compute_total_amount', store=True)
    line_ids = fields.One2many('odoocms.student.cpr.no', 'register_id', 'Student CPR Detail')
    issue_line_ids = fields.One2many('odoocms.student.cpr.issues', 'register_id', 'Student Issue Detail')
    state = fields.Selection([('Draft', 'Draft'),
                              ('Posted', 'Posted'),
                              ('Cancel', 'Cancel')], string='Status', default='Draft')
    financial_year = fields.Selection([('2019-2020', '2019-2020'),
                                       ('2020-2021', '2020-2021'),
                                       ('2021-2022', '2021-2022'),
                                       ('2022-2023', '2022-2023'),
                                       ('2023-2024', '2023-2024'),
                                       ('2023-2025', '2024-2025'),
                                       ('2025-2026', '2025-2026'),
                                       ('2026-2027', '2026-2027'),
                                       ('2027-2028', '2027-2028'),
                                       ('2028-2029', '2028-2029'),
                                       ('2029-2030', '2029-2030'),
                                       ('2030-2031', '2030-2031'),
                                       ('2031-2032', '2031-2032'),
                                       ('2032-2033', '2032-2033'),
                                       ('2033-2034', '2033-2034'),
                                       ('2034-2035', '2034-2035'),
                                       ('2035-2036', '2035-2036'),
                                       ('2036-2037', '2036-2037'),
                                       ('2037-2038', '2037-2038'),
                                       ('2038-2039', '2038-2039'),
                                       ('2039-2040', '2039-2040'),
                                       ('2040-2041', '2040-2041'),
                                       ('2041-2042', '2041-2042'),
                                       ('2042-2043', '2042-2043'),
                                       ('2043-2044', '2043-2044'),
                                       ('2044-2045', '2044-2045'),
                                       ('2045-2046', '2045-2046'),
                                       ('2046-2047', '2046-2047'),
                                       ('2047-2048', '2047-2048'),
                                       ('2048-2049', '2048-2049'),
                                       ('2049-2050', '2049-2050'),
                                       ], 'Financial Year', tracking=True)
    remarks = fields.Text('Remarks')

    @api.model
    def create(self, values):
        if not values.get('sequence', False):
            values['name'] = self.env['ir.sequence'].next_by_code('odoocms.student.cpr.register')
        result = super(OdoocmsStudentCPRRegister, self).create(values)
        return result

    def unlink(self):
        for rec in self:
            if not rec.state=='Draft':
                raise UserError('You Cannot delete this Record, This Record is not in the Draft State.')
            return super(OdoocmsStudentCPRRegister, self).unlink()

    @api.depends('line_ids')
    def _compute_total_student(self):
        for rec in self:
            if rec.line_ids:
                rec.total_students = len(rec.line_ids)

    @api.depends('line_ids')
    def _compute_total_student(self):
        for rec in self:
            if rec.line_ids:
                rec.total_students = len(rec.line_ids)

    @api.depends('line_ids', 'line_ids.tax_amount')
    def _compute_total_amount(self):
        for rec in self:
            tax_amount = 0
            if rec.line_ids:
                for line in rec.line_ids:
                    tax_amount += line.tax_amount
            rec.total_amount = tax_amount

    def action_post(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_('Please Define the Student Detail'))
            if rec.line_ids:
                rec.line_ids.write({'state': 'Posted'})
            if rec.issue_line_ids:
                rec.issue_line_ids.write({'state': 'Posted'})
            rec.state = 'Posted'

    def action_cancel(self):
        for rec in self:
            if rec.line_ids:
                rec.line_ids.write({'state': 'Cancel'})
            if rec.issue_line_ids:
                rec.issue_line_ids.write({'state': 'Cancel'})
            rec.state = 'Cancel'

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template To Student for CPR'),
            'template': '/odoocms_fee/static/xls/cpr_student_list.xlsx'
        }]


class OdoocmsStudentCPRNo(models.Model):
    _name = 'odoocms.student.cpr.no'
    _description = 'Student CPR No'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', tracking=True)
    sequence = fields.Char('Sequence')
    student_id = fields.Many2one('odoocms.student', 'Student', tracking=True, ondelete="restrict")
    student_code = fields.Char('Student ID', tracking=True)

    career_id = fields.Many2one('odoocms.career', 'Academic Level', compute='_compute_student_info', store=True, ondelete="restrict")
    program_id = fields.Many2one('odoocms.program', 'Academic Program', tracking=True, compute='_compute_student_info', store=True, ondelete="restrict")
    institute_id = fields.Many2one('odoocms.institute', 'School', compute='_compute_student_info', store=True, ondelete="restrict")
    discipline_id = fields.Many2one('odoocms.discipline', 'Discipline', compute='_compute_student_info', store=True, ondelete="restrict")
    campus_id = fields.Many2one('odoocms.campus', 'Campus', compute='_compute_student_info', store=True, ondelete="restrict")
    term_id = fields.Many2one('odoocms.academic.term', 'Current Academic Term', tracking=True, ondelete="restrict")
    session_id = fields.Many2one('odoocms.academic.session', 'Academic Session', tracking=True, compute='_compute_student_info', store=True, ondelete="restrict")
    semester_id = fields.Many2one('odoocms.semester', 'Semester', tracking=True, compute='_compute_student_info', store=True, ondelete="restrict")

    father_name = fields.Char('Father Name', tracking=True, compute='_compute_student_info', store=True)
    father_cnic = fields.Char('Father CNIC', tracking=True, compute='_compute_student_info', store=True)

    fee_amount = fields.Float('Fee Amount', tracking=True)
    tax_amount = fields.Float('Tax Amount', tracking=True)
    deposit_date = fields.Date('Deposit Date', tracking=True)
    register_id = fields.Many2one('odoocms.student.cpr.register', 'CPR Register', tracking=True, index=True, auto_join=True, ondelete='cascade')
    state = fields.Selection([('Draft', 'Draft'),
                              ('Posted', 'Posted'),
                              ('Cancel', 'Cancel')], string='Status', default='Draft')

    _sql_constraints = [
        ("uniq_student_id_register", "unique(student_id,register_id)", "Duplicates are not allowed.",)
    ]

    @api.depends('student_id')
    def _compute_student_info(self):
        for rec in self:
            if rec.student_id:
                rec.student_code = rec.student_id.code and rec.student_id.code or ''
                rec.session_id = rec.student_id.session_id and rec.student_id.session_id.id or False
                rec.career_id = rec.student_id.career_id and rec.student_id.career_id.id or False
                rec.program_id = rec.student_id.program_id and rec.student_id.program_id.id or False
                rec.institute_id = rec.student_id.institute_id and rec.student_id.institute_id.id or False
                rec.discipline_id = rec.student_id.discipline_id and rec.student_id.discipline_id.id or False
                rec.campus_id = rec.student_id.campus_id and rec.student_id.campus_id.id or False
                # rec.term_id = rec.student_id.term_id and rec.student_id.term_id.id or False
                rec.semester_id = rec.student_id.semester_id and rec.student_id.semester_id.id or False

                rec.father_name = rec.student_id.father_name and rec.student_id.father_name or ''
                rec.father_cnic = rec.student_id.father_guardian_cnic and rec.student_id.father_guardian_cnic or ''


class OdoocmsStudentCPRIssues(models.Model):
    _name = 'odoocms.student.cpr.issues'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Student CPR Issues'

    name = fields.Char('Name')
    student_id = fields.Many2one('odoocms.student', 'Student')
    student_code = fields.Char('Student ID')
    register_id = fields.Many2one('odoocms.student.cpr.register', 'CPR Register', tracking=True, index=True, auto_join=True, ondelete='cascade')
    state = fields.Selection([('Draft', 'Draft'),
                              ('Posted', 'Posted'),
                              ('Cancel', 'Cancel')], string='Status', default='Draft')
    notes = fields.Text('Notes')
