
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import pdb

import logging
_logger = logging.getLogger(__name__)


class OdooCMSExam(models.Model):
    _name = 'odoocms.exam'
    _description = 'CMS Exam'

    name = fields.Char(string='Name', default='New')
    batch_id = fields.Many2one('odoocms.batch', string='Batch')
    exam_type = fields.Many2one('odoocms.exam.type', string='Type', required=True)
    campus_class_division_wise = fields.Selection(related='exam_type.campus_class_division_wise',
            string='Campus/Class/Division Wise')
    
    class_division_hider = fields.Char(string='Class Division Hider')
    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='End Date', required=True)
    
    exam_lines = fields.One2many('odoocms.exam.line', 'exam_id', string='Subjects')
    
    state = fields.Selection([('draft', 'Draft'), ('ongoing', 'On Going'), ('close', 'Closed'), ('cancel', 'Canceled')],
            default='draft')
    term_id = fields.Many2one('odoocms.academic.term', string='Academic Term', related='batch_id.term_id', store=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get())

    @api.model
    def create(self, vals):
        res = super(OdooCMSExam, self).create(vals)
        return res

    @api.onchange('class_division_hider')
    def onchange_class_division_hider(self):
        self.campus_class_division_wise = 'campus'

    @api.constrains('date_start', 'date_end')
    def check_dates(self):
        for rec in self:
            if rec.date_start > rec.date_end:
                raise ValidationError(_("Start Date must be Anterior to End Date"))

    def close_exam(self):
        self.state = 'close'

    def cancel_exam(self):
        self.state = 'cancel'

    def confirm_exam(self):
        if len(self.exam_lines) < 1:
            raise UserError(_('Please Add Subjects'))
        name = str(self.exam_type.name) + '-' + str(self.date_start)[0:10]
        if self.batch_id:
            name = name + ' (' + str(self.batch_id.name) + ')'
        self.name = name
        self.state = 'ongoing'


class OdooCMSExamLine(models.Model):
    _name = 'odoocms.exam.line'
    _description = 'CMS Exam Line'

    subject_id = fields.Many2one('odoocms.class', string='Subject', required=True)
    date = fields.Date(string='Date', required=True)
    time_from = fields.Float(string='Time From', required=True)
    time_to = fields.Float(string='Time To', required=True)
    mark = fields.Integer(string='Mark')
    exam_id = fields.Many2one('odoocms.exam', string='Exam')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get())


class OdooCMSExamType(models.Model):
    _name = 'odoocms.exam.type'
    _description = 'CMS Exam Type'

    name = fields.Char(string='Name', required=True)
    campus_class_division_wise = fields.Selection([
        ('campus', 'Campus'), ('class', 'Class'), ('division', 'Division'), ('final', 'Final Exam')
        ], string='Exam Type', default='class')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get())

#
#
# class PortalClassResultAttachment(models.Model):
#     _name = "odoocms.portal.class.assessment.result"
#     _description = 'Class Assessment Result'
#
#     name = fields.Char('File Name')
#     class_id = fields.Many2one('odoocms.class',string='Class')
#     faculty_id = fields.Many2one('odoocms.faculty.staff',string='Faculty Staff')
#     result_file = fields.Binary('Result Sheet', attachment = True)
#     submit_date = fields.Date('Date')
#
#
# class MissingResult(models.Model):
#     _name = "odoocms.missing.result"
#     _description = 'Missing Result'
#
#     student = fields.Char()
#     stream = fields.Char()
#     class_nbr = fields.Char()
#     units = fields.Char()
#     grade = fields.Char()
#     repeat_code = fields.Char()
#     include_in_cgpa = fields.Char()
#     grade_date = fields.Char()
