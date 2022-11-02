import pdb
import time
import datetime
from datetime import date
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta


class OdooCMSGenerateInvoice(models.TransientModel):
    _name = 'odoocms.generate.invoice'
    _description = 'Generate Invoice'

    @api.model
    def _get_students(self):
        if self.env.context.get('active_model', False) == 'odoocms.student' and self.env.context.get('active_ids', False):
            return self.env.context['active_ids']

    # SARFRAZ 10-11-2020
    # @api.model
    # def _get_registrations(self):
    #     if self.env.context.get('active_model', False) == 'odoocms.subject.registration' and self.env.context.get('active_ids', False):
    #         return self.env.context['active_ids']

    @api.model
    def _get_defer_requests(self):
        if self.env.context.get('active_model', False) == 'odoocms.student.term.defer' and self.env.context.get('active_ids', False):
            return self.env.context['active_ids']

    @api.model
    def _get_resume_requests(self):
        if self.env.context.get('active_model', False) == 'odoocms.student.term.resume' and self.env.context.get('active_ids', False):
            return self.env.context['active_ids']

    student_ids = fields.Many2many('odoocms.student', 'generate_invoice_student_rel', 'invoice_id', 'student_id', string='Students', help="""Invoices for Only selected Students will be Generated.""", default=_get_students)
    # SARFRAZ 10-11-2020
    # reg_ids = fields.Many2many('odoocms.subject.registration', 'generate_invoice_subject_registration_rel', 'invoice_id', 'subject_reg_id', string="Registrations", help="""Invoices for Only selected Registrations will be Generated.""", default=_get_registrations)
    defer_ids = fields.Many2many('odoocms.student.term.defer', 'generate_invoice_term_defer_rel', 'invoice_id', 'term_defer_id', string="Defer Requests", help="""Invoices for Only selected Requests will be Generated.""", default=_get_defer_requests)
    resume_ids = fields.Many2many('odoocms.student.term.resume', 'generate_invoice_term_resume_rel', 'invoice_id', 'term_resume_id', string="Resume Requests", help="""Invoices for Only selected Requests will be Generated.""", default=_get_resume_requests)

    receipt_type_ids = fields.Many2many('odoocms.receipt.type', 'generate_invoice_receipt_type_rel', 'invoice_id', 'receipt_type_id', string='Receipt For')
    academic_semester_id = fields.Many2one('odoocms.academic.term', 'Academic Term')
    date_due = fields.Date('Due Date', default=(fields.Date.today() + relativedelta(days=7)))
    semester_required = fields.Boolean('Semester Required?', default=False)
    override_amount = fields.Boolean('Override Amount?', default=False)
    fixed_type = fields.Boolean('Fixed Receipt Type', default=False)
    registration_id = fields.Many2one('odoocms.student.subject', 'Subject')

    tag = fields.Char('Tag', help='Batch Number etc...', default=lambda self: self.env['ir.sequence'].next_by_code('odoocms.student.invoice'), copy=False, readonly=True)
    reference = fields.Char('Reference')

    description_id = fields.Many2one('odoocms.fee.description', 'Fee Description')
    comment = fields.Html('Description', help='Description of Invoice')

    override_line = fields.One2many('odoocms.invoice.amount.override', 'invoice_id', 'Override Lines')
    rechecking_subject = fields.Integer('Rechecking Subjects')
    rechecking_id = fields.Char('Rechecking reference')
    description_sub = fields.Char(string='Description')

    @api.onchange('description_id')
    def onchange_description_id(self):
        if self.description_id:
            self.comment = self.description_id.description

    @api.onchange('academic_semester_id')
    def onchange_academic_semester_id(self):
        # if self.academic_semester_id:
        # 	planning_line = False
        # 	if self.academic_semester_id.planning_ids:
        # 		planning_line = self.academic_semester_id.planning_ids.filtered(
        # 			lambda l: l.type == 'duesdate') # and student.batch_id.department_id in (l.department_ids)
        # 		if not planning_line:
        # 			planning_line = self.academic_semester_id.planning_ids.filtered(lambda l: l.type == 'withdraw' and len(l.department_ids) == 0)
        #
        # 	if planning_line:
        # 		self.date_due = planning_line.date_end
        # 	else:

        self.date_due = fields.Date.today() + relativedelta(days=7)

    @api.onchange('receipt_type_ids')
    def onchange_receipt_type(self):
        self.semester_required = any([receipt.semester_required for receipt in self.receipt_type_ids])
        self.override_amount = any([receipt.override_amount for receipt in self.receipt_type_ids])
        if self.override_amount:
            for receipt in self.receipt_type_ids.filtered(lambda l: l.override_amount==True):
                for head in receipt.fee_head_ids:
                    values = {
                        'fee_head_id': head.id,
                        'fee_head': head.id,
                        'fee_amount': head.lst_price,
                        'note': 'Test',
                    }
                    self.update({
                        'override_line': [(0, 0, values)],
                    })
                # return {'value': {'field': value}}
        for receipt in self.receipt_type_ids:
            if receipt.comment and not self.comment:
                self.comment = receipt.comment

    def generate_invoice(self):
        invoices = self.env['account.move']
        values = {
            'tag': self.tag,
            'reference': self.reference,
            'description': self.comment,
            'date': date.today(),
        }
        invoices_group = self.env['account.move.group'].create(values)
        for student in self.student_ids:
            if self.academic_semester_id and self.env['account.move'].search([('student_id', '=', student.id),
                                                                              ('academic_semester_id', '=', self.academic_semester_id.id),
                                                                              ('receipt_type_ids', 'in', self.receipt_type_ids.mapped('id'))]):
                continue
            if self.academic_semester_id.planning_ids:
                planning_line = self.academic_semester_id.planning_ids.filtered(
                    lambda l: l.type=='duesdate' and len(l.campus_ids)==0 and len(l.department_ids)==0 and len(
                        l.semester_ids)==0)
                planning_line_campus = self.academic_semester_id.planning_ids.filtered(
                    lambda l: l.type=='duesdate' and student.campus_id in (l.campus_ids) and len(
                        l.department_ids)==0 and len(l.semester_ids)==0)
                planning_line_depart = self.academic_semester_id.planning_ids.filtered(
                    lambda l: l.type=='duesdate' and len(l.campus_ids)==0 and student.batch_id.department_id in (
                        l.department_ids) and len(l.semester_ids)==0)

                planning_line_semester = self.academic_semester_id.planning_ids.filtered(
                    lambda l: l.type=='duesdate' and len(l.campus_ids)==0 and len(
                        l.department_ids)==0 and student.semester_id in (l.semester_ids))

                planning_line_depart_semester = self.academic_semester_id.planning_ids.filtered(
                    lambda l: l.type=='duesdate' and len(l.campus_ids)==0 and student.batch_id.department_id in (
                        l.department_ids) and student.semester_id in (l.semester_ids))
                planning_line_campus_semester = self.academic_semester_id.planning_ids.filtered(
                    lambda l: l.type=='duesdate' and student.campus_id in (l.campus_ids) and len(
                        l.department_ids)==0 and student.semester_id in (l.semester_ids))
                planning_line_campus_depart_semester = self.academic_semester_id.planning_ids.filtered(
                    lambda l: l.type=='duesdate' and student.campus_id in (
                        l.campus_ids) and student.batch_id.department_id in (
                                  l.department_ids) and student.semester_id in (
                                  l.semester_ids))

                planning_line_campus_depart = self.academic_semester_id.planning_ids.filtered(
                    lambda l: l.type=='duesdate' and student.campus_id in (
                        l.campus_ids) and student.batch_id.department_id in (l.department_ids) and len(
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

            academic_semester_id = self.academic_semester_id
            if not academic_semester_id:
                academic_semester_id = student.academic_semester_id
            invoices += student.generate_invoice(
                description_sub=self.description_sub, rechecking_subjects=self.rechecking_subject,
                semester=academic_semester_id, receipts=self.receipt_type_ids, date_due=self.date_due,
                comment=self.comment, tag=self.tag, override_line=self.override_line, reg=False,
                invoice_group=invoices_group, registration_id=self.registration_id)
            re_checking_receipt_type = self.env['ir.config_parameter'].sudo().get_param(
                'odoocms_registration.re_checking_receipt_type')
            re_checking_receipt_type = self.env['odoocms.receipt.type'].search([('id', '=', re_checking_receipt_type)])
            if re_checking_receipt_type in self.receipt_type_ids.mapped('id'):
                search_rechecking = self.env['odoocms.request.subject.rechecking'].search(
                    [('rechecking_id', '=', self.rechecking_id)])
                search_rechecking.state = 'invoice_generated'

        for reg in self.reg_ids:
            invoices += reg.student_id.generate_invoice(
                semester=self.academic_semester_id, receipts=self.receipt_type_ids, date_due=self.date_due,
                comment=self.comment, tag=self.tag, override_line=self.override_line, reg=reg,
                invoice_group=invoices_group)

        for reg in self.defer_ids:
            invoices += reg.student_id.generate_invoice(
                semester=self.academic_semester_id, receipts=self.receipt_type_ids, date_due=self.date_due,
                comment=self.comment, tag=self.tag, override_line=self.override_line, reg=reg,
                invoice_group=invoices_group)

        for reg in self.resume_ids:
            invoices += reg.student_id.generate_invoice(
                semester=self.academic_semester_id, receipts=self.receipt_type_ids, date_due=self.date_due,
                comment=self.comment, tag=self.tag, override_line=self.override_line, reg=reg,
                invoice_group=invoices_group)

        if invoices:
            invoice_list = invoices.mapped('id')
            form_view = self.env.ref('odoocms_fee.odoocms_receipt_form')
            tree_view = self.env.ref('odoocms_fee.odoocms_receipt_tree')
            return {
                'domain': [('id', 'in', invoice_list)],
                'name': _('Invoices'),
                'view_type': 'form',
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


class OdooCMSInvoiceAmountOverride(models.TransientModel):
    _name = 'odoocms.invoice.amount.override'
    _description = 'Invoice Amount Override'

    fee_head_id = fields.Many2one('odoocms.fee.head', string='Fee')
    fee_head = fields.Integer()
    fee_amount = fields.Float('Amount')
    payment_type = fields.Selection([('admissiontime', 'Admission Time'),
                                     ('permonth', 'Per Month'),
                                     ('peryear', 'Per Year'),
                                     ('persemester', 'Per Semester'),
                                     ('onetime', 'One Time'),
                                     ], string='Payment Type', related="fee_head_id.payment_type")
    fee_description = fields.Text('Description', related='fee_head_id.description_sale')
    note = fields.Char('Note')
    invoice_id = fields.Many2one('odoocms.generate.invoice', 'Invoice')


class OdooCMSAdmissionInvoice(models.TransientModel):
    _name = 'odoocms.admission.invoice'
    _description = 'Admission Invoice'

    @api.model
    def _get_applicants(self):
        applicants = []
        if self.env.context.get('active_model', False)=='odoocms.application' \
                and self.env.context.get('active_ids', False):
            for rec in self.env['odoocms.application'].browse(self.env.context.get('active_ids')):
                applicants.append(rec.id)
            return applicants

    # SARFRAZ 10-11-2020
    # applicant_ids = fields.Many2many('odoocms.application', 'admission_invoice_application_rel', 'admission_invoice_id', 'application_id', string='Applicants', help="""Fee Challan for Only selected applicants will be generated.""", default=_get_applicants)

    def generate_admission_invoice(self):
        invoices = self.env['account.move']
        for applicant in self.applicant_ids:
            invoices += applicant.generate_invoice()
        invoice_list = invoices.mapped('id')
        return {
            'domain': [('id', 'in', invoice_list)],
            'name': _('Invoices'),
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            # 'context': {'default_class_id': self.id},
            'type': 'ir.actions.act_window'
        }
    # return {'type': 'ir.actions.act_window_close'}
