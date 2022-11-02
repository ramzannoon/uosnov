from odoo import models, fields, _, api
from odoo.exceptions import ValidationError

class OdooCMSExamCenter(models.Model):
    _name = 'odoocms.exam.center'
    _description = 'Exam Center'
    _rec_name = 'name'

    name = fields.Char('Name', required=True)
    short_name = fields.Char('Short Name')
    code = fields.Char('Code')
    district_id = fields.Many2one('odoocms.district','District')
    gender = fields.Selection([('m', 'Male'),('f', 'Female'),('c', 'Combined'), ],'Gender', default='m' )
    type = fields.Selection([('c', 'Combined'),('p', 'Private'),('r', 'Regular'), ],'Type', default='p' )
    capacity = fields.Integer('Maximum Capacity')
    center_line = fields.One2many('odoocms.exam.center.line','center_id',string='Center_line')

    # Constraints
    @api.constrains('name')
    def _unique_name(self):
        Record = self.search([('name', '=', self.name)])
        if len(Record) > 1:
            raise ValidationError('Cannot have duplicated records for same Center')


class OdooCMSExamCenterLine(models.Model):
    _name = 'odoocms.exam.center.line'
    _description = 'Exam Center Line'

    sequence = fields.Integer('Seq',default='1')
    type = fields.Many2one('odoocms.exam.center.structure', required=True)
    row = fields.Integer('Row',required=True)
    col = fields.Integer('Column',required=True)
    center_id = fields.Many2one('odoocms.exam.center','Center id')

    # @api.constrains('row', 'col')
    # def _check_capacity_center(self):
    #     Record = self.search([('center_id', '=', self.center_id.id), ])
    #     center= self.env['odoocms.exam.center'].search([('id', '=', self.center_id.id)])
    #     if len(Record) > 1:
    #         capacity  = Record.capacity
    #         row = self.row
    #         col = self.col
    #         size = row * col
    #         if size > capacity:
    #             raise ValidationError('Please ensure Rows and Columns capacity less then Max Capacity of Center')

class OdooCMSExamCenterStructure(models.Model):
    _name = 'odoocms.exam.center.structure'
    _description = 'Exam Center Structure'

    name = fields.Char('Name' ,help="Room Name,Hall Name")
    code = fields.Char('Code' ,help="Room Code,Hall Code")


class OdooCMSExamCenterExam(models.Model):
    _name = 'odoocms.exam.center.assignment'
    _description = 'Exam Center Exam'
    _rec_name = 'center_id'

    center_id = fields.Many2one('odoocms.exam.center','Center')
    center_short_name = fields.Char('Center Short Name',related="center_id.short_name")
    center_code = fields.Char('Center Code',related='center_id.code')
    center_gender_type = fields.Selection('Gender',related='center_id.gender')
    center_capacity = fields.Integer('Capacity',related='center_id.capacity')
    student_ids = fields.Many2many('odoocms.student','rel_exam_center_student','exam_center_id','student_id',string='Students')
    term_id = fields.Many2one('odoocms.academic.term','Term')
    staff_ids = fields.One2many('odoocms.exam.center.assignment.line','exam_id',string='Staff')
    campus_id  = fields.Many2one('odoocms.campus','Campus')
    student_count = fields.Integer(compute='student_counter',store=True,string='Selected Students')

    preferance_ids = fields.One2many('odoocms.exam.center.line',related='center_id.center_line',string='Preferences')


    # Constraints
    @api.constrains('center_id')
    def _unique_examination_center(self):
        Record = self.search([('center_id', '=', self.center_id.id),])
        if len(Record) > 1:
            raise ValidationError('Cannot have duplicated records for same Center')


    @api.constrains('student_ids')
    def _check_limit(self):
        if len(self.student_ids) >= self.center_capacity + 1:

            raise ValidationError("No Enough Capacity")
        for rec in self.student_ids:
            if self.center_gender_type == 'm':
                if rec.gender == 'f':
                    raise ValidationError("Female Students can not be added in this Examination Center")

            if self.center_gender_type == 'f':
                if rec.gender == 'm':
                    raise ValidationError("Male Students can not be added in this Examination Center")

    @api.depends('student_ids')
    def student_counter(self):
        for rec in self:
            rec.student_count = len(rec.student_ids)



class OdooCMSExamCenterAssignmentline(models.Model):
    _name = 'odoocms.exam.center.assignment.line'
    _description = 'Exam Center Assignment Line'
    _rec_name = 'staff_id'

    staff_id = fields.Many2one('odoocms.exam.staff', 'Staff')
    staff_name = fields.Char('Staff Name',related ='staff_id.first_name')
    tag_id = fields.Many2one('odoocms.exam.tag', 'Tag')
    exam_id = fields.Many2one('odoocms.exam.center.assignment', 'Exam')



