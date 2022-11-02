
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import math
import pdb

def round_half_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n*multiplier + 0.5) / multiplier


class OdooCMSStudentCourseComponent(models.Model):
    _inherit = 'odoocms.student.course.component'

    att_line_ids = fields.One2many('odoocms.class.attendance.line', 'student_course_component_id', 'Attendance Lines')
    attendance_percentage = fields.Float('Attendance Percentage', compute = '_get_attendance_percentage', store= True)

    @api.depends('att_line_ids','att_line_ids.state','att_line_ids.present','att_line_ids.reason_id')
    def _get_attendance_percentage(self):
        for rec in self:
            attendance_percentage = 0
            present = len( rec.att_line_ids.filtered(lambda l:l.state != 'draft' and
                (l.present == True or (l.present == False and l.reason_id and l.reason_id.present == True))))
            absent = len(rec.att_line_ids.filtered(lambda l: l.state != 'draft' and l.present == False and
                (l.reason_id == False or (l.reason_id and l.reason_id.absent == True))))
            total = present + absent
            if total > 0:
                attendance_percentage = round_half_up( (present/total)*100, 2)
            else:
                attendance_percentage = 100
            rec.attendance_percentage = attendance_percentage
            

class OdooCMSStudentCourse(models.Model):
    _inherit = 'odoocms.student.course'

    attendance_percentage = fields.Float('Attendance Percentage', compute = '_get_attendance_percentage', store= True)

    @api.depends('component_ids.attendance_percentage')
    def _get_attendance_percentage(self):
        for rec in self:
            total = 0
            for reg in rec.component_ids:
                total += reg.attendance_percentage * (reg.class_id.weightage)
            rec.attendance_percentage = round_half_up(total / (rec.primary_class_id.credits or 1),0)

    def add_attendance(self,component, date_effective):
        attendance_line_obj = self.env['odoocms.class.attendance.line']
        registers = self.env['odoocms.class.attendance'].search([
            ('class_id','=',component.class_id.id),('date_class','>=',date_effective)])
        for register in registers:
            data = {
                'attendance_id': register.id,
                'student_id': component.student_id.id,
                'student_name': component.student_id.name,
                'class_id': component.class_id.id,
            }
            attendance_line_obj.create(data)
    
    def remove_attendance(self, component, date_effective):
        att_lines = self.env['odoocms.class.attendance.line'].search([
            ('student_id','=',self.student_id.id),('student_course_component_id','=',component.id),
            ('date_class','>=', date_effective)
        ])
        att_lines.unlink()
        

class OdooCMSClassGrade(models.Model):
    _inherit = 'odoocms.class.grade'

    def assign_xf(self):
        for primary_class in self.sudo().primary_class_ids:
            primary_class.assign_xf()
        return 1
    
    def unassign_xf(self):
        for primary_class in self.sudo().primary_class_ids:
            primary_class.unassign_xf()
        return 1
    
    
class OdooCMSClassPrimary(models.Model):
    _inherit = 'odoocms.class.primary'
    
    def cron_xf(self):
        pass
    
    def assign_xf(self):
        attendance_req_per = float(self.env['ir.config_parameter'].sudo().get_param('odoocms_attendance.attendance_req_per') or 80)
        for reg in self.registration_ids.filtered(lambda l: l.attendance_percentage < attendance_req_per):
            reg.grade = 'XF'

    def unassign_xf(self):
        for reg in self.registration_ids.filtered(lambda l: l.grade == 'XF'):
            reg.grade = False
