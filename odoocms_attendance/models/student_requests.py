
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import pdb
from datetime import date


class OdooCMSStudentLeaveRequest(models.Model):
    _name = 'odoocms.student.leave.request'
    _description = 'Leave Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'student_id'

    student_id = fields.Many2one('odoocms.student', 'Student')
    class_id = fields.Many2one('odoocms.class', 'Class', store=True)
    faculty_id = fields.Many2one('odoocms.faculty.staff', 'Faculty', related='class_id.faculty_staff_id', readonly=True)
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    date_approve = fields.Date('Date Approve')
    reason_id = fields.Many2one('odoocms.attendance.absent.reason','Leave Reason')
    source = fields.Selection([('portal','Portal'),('internal','CMS User')], default='internal')

    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected'), ('done', 'Done')], default='draft',tracking=True)


    def action_approve(self):
        for rec in self:
            class_attendance = self.env['odoocms.class.attendance'].sudo().search([
                ('date_class', '<=', rec.date_to),
                ('date_class', '>=', rec.date_from),
                ('class_id', '=', rec.class_id.id),
                ('faculty_id', '=', rec.faculty_id.id)])
            
            class_attendance_line = class_attendance.attendance_line.filtered(lambda s: s.student_id == rec.student_id)
            if rec.state == 'draft' and class_attendance_line:
                for line in class_attendance_line:
                    if not line.present:
                        line.reason_id = self.reason_id.id
                rec.state = 'done'
                rec.date_approve = date.today()
            elif rec.state == 'draft' and not class_attendance_line:
                rec.state = 'approve'
                rec.date_approve = date.today()


    def action_reject(self):
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'reject'

