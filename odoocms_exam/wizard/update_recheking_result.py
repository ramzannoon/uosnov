import pdb
import time
import datetime
from datetime import date
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta


class OdooCMSGenerateRecheckingUpdate(models.TransientModel):
    _name = 'odoocms.rechecking.result.update'
    _description = 'Update Rechecking Result'

    @api.model
    def _get_students(self):
        if self.env.context.get('active_model', False) == 'odoocms.request.subject.rechecking' and self.env.context.get(
                'active_ids',
                False):
            return self.env.context['active_ids']

    student_ids = fields.Many2many('odoocms.request.subject.rechecking','result_rechecking_rel', string='Students',default=_get_students)


    def action_update_result(self):

        re_checking_receipt_type = self.env['ir.config_parameter'].sudo().get_param(
            'odoocms_registration.re_checking_receipt_type')
        re_checking_receipt_type = self.env['odoocms.receipt.type'].search([('id', '=', re_checking_receipt_type)])

        for student in self.student_ids:
            for rec in student.rechecking_line_ids:
                invoice_id = self.env['account.invoice'].search(
                    [('student_id', '=', student.student_id.id), ('term_id', '=', student.term_id.id),
                     ('state', '=', 'paid'), ('receipt_type_ids', 'in', re_checking_receipt_type.id)])

                if student.state == 'invoice_generated' and invoice_id:
                    max_marks = rec.registration_id.class_id.max_marks
                    if max_marks == 0:
                        max_marks = 1
                    new_marks = rec.new_marks / max_marks
                    if new_marks >= 100:
                        new_marks = 100
                    rec.registration_id.normalized_marks = new_marks

                    grade_rec = self.env['odoocms.exam.grade'].search([
                        ('low_per', '<=', new_marks),
                        ('high_per', '>=', new_marks),
                        ('class_id', '=', False)
                    ])
                    if grade_rec:
                        rec.registration_id.grade = grade_rec.name

                    grade_gpa = self.env['odoocms.grade.gpa'].search([('name', '=', rec.registration_id.grade)])
                    if  grade_gpa:

                        rec.registration_id.gpa = grade_gpa.gpa
                        rec.state = 'done'
                        student.state = 'done'

