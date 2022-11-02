import pdb
import time
import datetime
from datetime import date
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class OdooCMSGenerateRecheckingInvoice(models.TransientModel):
    _name = 'odoocms.generate.invoice.rechecking'
    _description = 'Generate Invoice Rechecking'

    @api.model
    def _get_students(self):
        if self.env.context.get('active_model', False) == 'odoocms.request.subject.rechecking' and self.env.context.get('active_ids', False):
            return self.env.context['active_ids']

    @api.model
    def _get_receipt_type(self):
        re_checking_receipt_type = self.env['ir.config_parameter'].sudo().get_param(
            'odoocms_registration.re_checking_receipt_type')
        if not re_checking_receipt_type:
            raise UserError('Please configure the Rechecking Receipt Type in Global Settings')
        re_checking_receipt_type = self.env['odoocms.receipt.type'].search([('id', '=', re_checking_receipt_type)])

        # for rec in  re_checking_receipt_type:
        #     self.receipt_type_ids = re_checking_receipt_type.mapped('id')
        return re_checking_receipt_type

    student_ids = fields.Many2many('odoocms.request.subject.rechecking',
        'generate_invoice_rechecking_rel', string='Students', default=_get_students)

    receipt_type_ids = fields.Many2many('odoocms.receipt.type', string='Receipt For', default=_get_receipt_type)
    academic_semester_id = fields.Many2one('odoocms.academic.semester', 'Academic Term')
    date_due = fields.Date('Due Date', default=(fields.Date.today() + relativedelta(days=7)))
    tag = fields.Char('Tag', help='Batch Number etc...',
        default=lambda self: self.env['ir.sequence'].next_by_code('odoocms.student.invoice'), copy=False,
        readonly=True)
    reference = fields.Char('Reference')

    description_id = fields.Many2one('odoocms.fee.description', 'Fee Description')
    comment = fields.Html('Description', help='Description of Invoice')
    rechecking_subject = fields.Integer('Rechecking Subjects')
    override_line = fields.One2many('odoocms.invoice.amount.override', 'invoice_id', 'Override Lines')
    registration_id = fields.Many2one('odoocms.student.course', 'Subject')

    def generate_invoice(self):
        invoices = self.env['account.move']
        values = {
            'tag': self.tag,
            'reference': self.reference,
            'description': self.comment,
            'date': date.today(),
        }
        invoices_group = self.env['account.move.group'].create(values)
        submit_student_list = self.student_ids.filtered(lambda l: l.state=='approve')
        for student in submit_student_list:
            if self.academic_semester_id and self.env['account.move'].search([('student_id', '=', student.id), ('academic_semester_id', '=', self.academic_semester_id.id)]):
                continue

            if self.academic_semester_id.planning_ids:
                planning_line = self.academic_semester_id.planning_ids.filtered(
                    lambda l: l.type=='duesdate' and len(l.campus_ids)==0 and len(l.department_ids)==0 and len(
                        l.semester_ids)==0)
                planning_line_campus = self.academic_semester_id.planning_ids.filtered(
                    lambda l: l.type=='duesdate' and student.student_id.campus_id in (l.campus_ids) and len(
                        l.department_ids)==0 and len(l.semester_ids)==0)
                planning_line_depart = self.academic_semester_id.planning_ids.filtered(
                    lambda l: l.type=='duesdate' and len(
                        l.campus_ids)==0 and student.student_id.batch_id.department_id in (
                                  l.department_ids) and len(l.semester_ids)==0)

                planning_line_semester = self.academic_semester_id.planning_ids.filtered(
                    lambda l: l.type=='duesdate' and len(l.campus_ids)==0 and len(
                        l.department_ids)==0 and student.student_id.semester_id in (l.semester_ids))

                planning_line_depart_semester = self.academic_semester_id.planning_ids.filtered(
                    lambda l: l.type=='duesdate' and len(
                        l.campus_ids)==0 and student.student_id.batch_id.department_id in (
                                  l.department_ids) and student.student_id.semester_id in (l.semester_ids))
                planning_line_campus_semester = self.academic_semester_id.planning_ids.filtered(
                    lambda l: l.type=='duesdate' and student.student_id.campus_id in (l.campus_ids) and len(
                        l.department_ids)==0 and student.student_id.semester_id in (l.semester_ids))
                planning_line_campus_depart_semester = self.academic_semester_id.planning_ids.filtered(
                    lambda l: l.type=='duesdate' and student.student_id.campus_id in (
                        l.campus_ids) and student.student_id.batch_id.department_id in (
                                  l.department_ids) and student.student_id.semester_id in (
                                  l.semester_ids))

                planning_line_campus_depart = self.academic_semester_id.planning_ids.filtered(
                    lambda l: l.type=='duesdate' and student.student_id.campus_id in (
                        l.campus_ids) and student.student_id.batch_id.department_id in (l.department_ids) and len(
                        l.semester_ids)==0)

                if planning_line and len(planning_line)==1:
                    self.date_due = planning_line.date_end
                if planning_line_campus and len(planning_line_campus)==1:
                    self.date_due = planning_line_campus.date_end
                if planning_line_depart and len(planning_line_depart)==1:
                    self.date_due = planning_line_depart.date_end
                if planning_line_semester and len(planning_line_semester)==1:
                    self.date_due = planning_line_semester.date_end
                if planning_line_campus_depart and len(planning_line_campus_depart)==1:
                    self.date_due = planning_line_campus_depart.date_end
                if planning_line_campus_semester and len(planning_line_campus_semester)==1:
                    self.date_due = planning_line_campus_semester.date_end
                if planning_line_depart_semester and len(planning_line_depart_semester)==1:
                    self.date_due = planning_line_depart_semester.date_end
                if planning_line_campus_depart_semester and len(planning_line_campus_depart_semester)==1:
                    self.date_due = planning_line_campus_depart_semester.date_end

            des = ""
            for sub in student.rechecking_line_ids:
                des += sub.registration_id.subject_id.subject_id.name + ","

            academic_semester_id = self.academic_semester_id
            if not academic_semester_id:
                academic_semester_id = student.student_id.academic_semester_id
            invoices += student.student_id.generate_invoice(description_sub=des,
                rechecking_subjects=student.rechecking_subject, semester=student.academic_semester_id,
                receipts=self.receipt_type_ids, date_due=self.date_due,
                comment=self.comment, tag=self.tag, override_line=self.override_line, reg=False,
                invoice_group=invoices_group, registration_id=self.registration_id)
            student.state = 'invoice_generated'

        # for reg in self.reg_ids:
        #     invoices += reg.student_id.generate_invoice(
        #         semester=self.academic_semester_id, receipts=self.receipt_type_ids, date_due=self.date_due,
        #         comment=self.comment, tag=self.tag, override_line=self.override_line, reg=reg,
        #         invoice_group=invoices_group)
        #
        # for reg in self.defer_ids:
        #     invoices += reg.student_id.generate_invoice(
        #         semester=self.academic_semester_id, receipts=self.receipt_type_ids, date_due=self.date_due,
        #         comment=self.comment, tag=self.tag, override_line=self.override_line, reg=reg,
        #         invoice_group=invoices_group)
        #
        # for reg in self.resume_ids:
        #     invoices += reg.student_id.generate_invoice(
        #         semester=self.academic_semester_id, receipts=self.receipt_type_ids, date_due=self.date_due,
        #         comment=self.comment, tag=self.tag, override_line=self.override_line, reg=reg,
        #         invoice_group=invoices_group)

        if invoices:
            invoice_list = invoices.mapped('id')
            form_view = self.env.ref('odoocms_fee.odoocms_receipt_form')
            tree_view = self.env.ref('odoocms_fee.odoocms_receipt_tree')
            return {
                'domain': [('id', 'in', invoice_list)],
                'name': _('Invoices'),
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'view_id': False,
                'views': [
                    (tree_view and tree_view.id or False, 'tree'),
                    (form_view and form_view.id or False, 'form'),
                ],
                # 'context': {'default_class_id': self.id},
                'type': 'ir.actions.act_window'
            }
        else:
            return {'type': 'ir.actions.act_window_close'}
