from odoo import models, fields, _, api

class OdooCMSExamSitting(models.Model):
    _name = 'odoocms.exam.sitting'
    _description = 'Exam Sitting Plan'
    _rec_name = 'exam_center_id'

    exam_center_id = fields.Many2one('odoocms.exam.center.assignment','Examination Center')
    center_capacity = fields.Integer('Capacity',related='exam_center_id.center_capacity')
    term_id = fields.Many2one('odoocms.academic.term','Term')
    plan_ids = fields.One2many('odoocms.exam.sitting.line','sitting_id',string='Sitting Plan')
    date = fields.Date('Date')


class OdooCMSExamSittingline(models.Model):
    _name = 'odoocms.exam.sitting.line'
    _description = 'Exam Sitting Line'

    student_id = fields.Many2one('odoocms.student', 'Student')
    course = fields.Char('Course')
    sitting_number = fields.Char('Sitting Plan Number')
    sitting_id = fields.Many2one('odoocms.exam.sitting', 'Exam Sitting')



