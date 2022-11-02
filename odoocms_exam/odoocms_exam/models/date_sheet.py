from odoo import models, fields, api, _
from datetime import datetime, date
import calendar
import pdb


class OdooCMSDateSheet(models.Model):
    _name = 'odoocms.datesheet'
    _description = 'Datesheet'

    department_id = fields.Many2one('odoocms.department', string='Department', required=True)
    program_id = fields.Many2one('odoocms.program', string='Program')
    batch_ids = fields.Many2many('odoocms.batch', string='Batch', required=True)
    term_id = fields.Many2one('odoocms.academic.term', string='Academic Semester', required=True)
    number = fields.Integer(related='term_id.number',string='Term Number')
    exam_type_id = fields.Many2one('odoocms.exam.type', 'Exam Type', required=True)
    active = fields.Boolean('Active', default=True)
    name = fields.Char(compute='_get_name', store=True)
    line_ids = fields.One2many('odoocms.datesheet.line', 'datesheet_id')

    @api.depends('department_id', 'term_id', 'exam_type_id')
    def _get_name(self):
        for rec in self:
            if rec.department_id and rec.term_id and rec.exam_type_id:
                rec.name = rec.department_id.name + " (" + rec.term_id.name + ")" + " /" + rec.exam_type_id.name + "Term"

    def generate_date_sheet(self):
        self.line_ids.unlink()
        courses = []
        for batch in self.batch_ids:
            course_ids = self.env['odoocms.class.primary'].search([('batch_id', '=', batch.id),('term_id','=',self.term_id.id)]).mapped('course_id')
            for course in course_ids:
                data = {
                    'date': date.today(),
                    'time_start': 1,
                    'course_id': course.id,
                    'batch_id': batch.id,
                    'term_id':self.term_id.id
                }
                courses.append((0, 0, data))
        self.line_ids = courses


class OdooCMSDateSheetLine(models.Model):
    _name = 'odoocms.datesheet.line'
    _description = 'Datesheet Line'

    datesheet_id = fields.Many2one('odoocms.datesheet', required=True)
    date = fields.Date('Date')
    date_day = fields.Char('Day',compute='_get_day_of_date')
    time_start = fields.Many2one('odoocms.datesheet.timeslot', string='Time', required=True,
                                 help="Start Time of Paper.")
    scheme_line_id = fields.Many2one('odoocms.study.scheme.line', string='Scheme Line')
    
    course_id = fields.Many2one('odoocms.course', string='Course', required=True)
    batch_id = fields.Many2one('odoocms.batch', string='Batch')
    term_id = fields.Many2one('odoocms.academic.term', string='Term')

    department_id = fields.Many2one(related='datesheet_id.department_id', string='Department', store=True, copy=False)
    

    # _sql_constraints = [
    #     ('unique_time_table', 'unique(datesheet_id, date, course_id,time_start)',
    #      "Course already exists with in same Date Time"),
    # ]
    _sql_constraints = [
        ('unique_time_table', 'Check(1=1)',
         "Course already exists with in same Date Time"),
    ]

    @api.depends('date')
    def _get_day_of_date(self):
        for r in self:
            if r.date:
                selected = fields.Datetime.from_string(r.date)
                r.date_day = calendar.day_name[selected.weekday()]


class OdooCMSDateSheetTimeSlot(models.Model):
    _name = 'odoocms.datesheet.timeslot'
    _description = 'Datesheet Time Slot'

    start_time = fields.Float(string='Start Time', required=True, index=True, help="Start time of Paper.")
    end_time = fields.Float(string='End Time', required=True, index=True, help="End time of Paper.")
    name = fields.Char(compute='_get_name', store=True)

    @api.depends('start_time', 'end_time')
    def _get_name(self):
        for rec in self:
            if rec.start_time and rec.end_time:
                rec.name = "%02d:%02d" % (divmod(rec.start_time * 60, 60)) + " -" + "%02d:%02d" % (divmod(rec.end_time * 60, 60))
