import datetime
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from dateutil.relativedelta import relativedelta
from odoo.tools.safe_eval import safe_eval
from datetime import date
from dateutil.relativedelta import relativedelta
import re
import pdb


# Remarks (FAROOQ) on 02-01-2021
# Have to remove the link of odoocms.term.scheme from this file

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


class OdoocmsStudentFeePublic(models.AbstractModel):
    _name = 'odoocms.student.fee.public'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _description = 'Students Public Model'

    session_id = fields.Many2one('odoocms.academic.session', 'Academic Session', tracking=True, compute='_compute_student_data', store=True)
    career_id = fields.Many2one('odoocms.career', 'Academic Level', compute='_compute_student_data', store=True)
    program_id = fields.Many2one('odoocms.program', 'Academic Program', tracking=True, compute='_compute_student_data', store=True)
    institute_id = fields.Many2one('odoocms.institute', 'School', compute='_compute_student_data', store=True)
    discipline_id = fields.Many2one('odoocms.discipline', 'Discipline', compute='_compute_student_data', store=True)
    campus_id = fields.Many2one('odoocms.campus', 'Campus', compute='_compute_student_data', store=True)
    term_id = fields.Many2one('odoocms.academic.term', 'Current Term', tracking=True, compute='_compute_student_data', store=True)
    semester_id = fields.Many2one('odoocms.semester', 'Semester', tracking=True, compute='_compute_student_data', store=True)
    to_be = fields.Boolean('To Be', default=False)

    @api.depends('student_id')
    def _compute_student_data(self):
        for rec in self:
            if rec.student_id:
                rec.session_id = rec.student_id.session_id and rec.student_id.session_id.id or False
                rec.career_id = rec.student_id.career_id and rec.student_id.career_id.id or False
                rec.institute_id = rec.student_id.institute_id and rec.student_id.institute_id.id or False
                rec.campus_id = rec.student_id.campus_id and rec.student_id.campus_id.id or False
                rec.program_id = rec.student_id.program_id and rec.student_id.program_id.id or False
                rec.discipline_id = rec.student_id.discipline_id and rec.student_id.discipline_id.id or False
                rec.term_id = rec.student_id.term_id and rec.student_id.term_id.id or False
                rec.semester_id = rec.student_id.semester_id and rec.student_id.semester_id.id or False


class OdooCMSStudent(models.Model):
    _inherit = 'odoocms.student'

    feemerit = fields.Selection([('regular', 'Regular'),
                                 ('self', 'Self Finance'),
                                 ('rationalized', 'Rationalized')], 'Group Code', default='regular')

    hostel_facility = fields.Boolean('Hostel Facility')
    hostel_cubical = fields.Boolean('Cubical')

    waiver_ids = fields.Many2many('odoocms.fee.waiver', 'student_waiver_rel', 'student_id', 'waiver_id', 'Fee Waiver')
    son_waiver_flag = fields.Boolean(string='Employee Son Association', default=False)
    kinship_flag = fields.Boolean(string='Kinship Association ', default=False)

    waiver_association_son = fields.Many2one('hr.employee', 'Employee Association')
    waiver_association_kinship = fields.Many2one('odoocms.student', string='Student Association')

    fee_structure_ids = fields.One2many('odoocms.fee.structure.student', 'student_id', string='Fee Lines')
    receipt_ids = fields.One2many('account.move', 'student_id', 'Fee Receipts')
    ledger_lines = fields.One2many('odoocms.student.ledger', 'student_id', 'Ledger Lines')
    refund_request_ids = fields.One2many('odoocms.fee.refund.request', 'student_id', 'Refund Requests')
    waiver_line_ids = fields.One2many('odoocms.student.fee.waiver', 'student_id', 'Fee Waiver Detail')
    exclude_library_fee = fields.Boolean('Exclude Library Fee', default=False)
    fee_generated = fields.Boolean('Fee Generated', default=False)
    to_be = fields.Boolean('To Be', default=False)

    def generate_invoice(self, description_sub, semester, receipts, date_due, comment='', tag=False, reference=False, override_line=False, reg=False, invoice_group=False, view=False, registration_id=False, charge_annual_fee=False, apply_taxes=False):
        # Check here to generate Hostel Fee Along with Semester Fee or not
        # semester_fee -----> Generate with Semester Fee
        # separate_fee -----> Generate a separate fee for Hostel
        hostel_fee_charge_timing = (self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.hostel_fee_charge_timing') or 'separate_fee')
        # Check Semester Deferment
        semester_defer = False
        suspended_student_fee = False
        student_defer_or_suspension_flag = False
        # semester_defer_rec = self.env['odoocms.student.term.defer'].search([('student_id', '=', self.id),
        #                                                                     ('semester_id', '=', self.semester_id.id),
        #                                                                     ('term_id', '=', self.term_id.id)], order='id desc', limit=1)

        semester_defer_rec = self.env['odoocms.student.term.defer'].search([('student_id', '=', self.id),
                                                                            ('term_id', '=', semester.id),
                                                                            ('state', '!=', 'cancel')], order='id desc', limit=1)

        if semester_defer_rec:
            semester_defer = True
            student_defer_or_suspension_flag = True
        if self.tag_ids.filtered(lambda t: t.name=='Suspension'):
            suspended_student_fee = True
            student_defer_or_suspension_flag = True

        # if not semester_defer_rec and self.tag_ids.filtered(lambda t: t.code=='DEF' and t.category_id.code=='Fee'):
        #     semester_defer = True

        registration_id = registration_id.id
        waiver_amount_for_invoice = 0
        scholarship_amount_for_invoice = 0
        student_receipts = receipts

        fee_structure = self.env['odoocms.fee.structure'].search([('session_id', '=', self.session_id.id), ('term_id', '=', semester.id), ('career_id', '=', self.career_id.id)], order='id desc', limit=1)
        if not fee_structure or not fee_structure.current:
            raise UserError(_('Fee structure is not defined for session %s.' % self.session_id.name))

        if not fee_structure.date_start or not fee_structure.date_end:
            raise UserError(_('Fee structure Effective date Period are not Entered.'))
        if fee_structure.date_start > date.today() or fee_structure.date_end < date.today():
            raise UserError(_('Fee structure is out of date.'))

        receipts = student_receipts
        lines = []
        invoices = self.env['account.move']
        payment_types = ['persemester', 'persubject', 'onetime', 'admissiontime']

        # semester_scheme = self.env['odoocms.term.scheme'].search([('session_id', '=', self.session_id.id),
        #                                                           ('term_id', '=', semester.id),
        #                                                           ('semester_id', '=', self.semester_id.id)])
        #
        # if not semester_scheme or len(semester_scheme)==0:
        #     raise UserError(_('Semester Scheme for session %s and %s is not defined.' % (self.session_id.name, semester.name)))
        #
        # semester_number = semester_scheme.semester_id.number
        # if semester_number % 2==1 or not semester:
        #     payment_types.append('peryear')

        if charge_annual_fee:
            payment_types.append('peryear')

        # fee_head_ids-----> odoocms.fee.head
        fee_head_ids = receipts.mapped('fee_head_ids').ids

        # structure_fee_heads -----> odoocms.fee.structure.head
        structure_fee_heads = fee_structure.head_ids.filtered(lambda l: l.fee_head_id.id in fee_head_ids and l.current and l.payment_type in payment_types)

        analytic_tags = self.env['account.analytic.tag']
        # if self.program_id.department_id.institute_id.analytic_tag_id:
        #     analytic_tags += self.program_id.department_id.institute_id.analytic_tag_id
        #     analytic_tag_ids = [(6, 0, analytic_tags.ids)]

        if not fee_structure.journal_id.sequence_id:
            raise UserError(_('Please define sequence on the Journal related to this Invoice.'))

        date_invoice = fields.Date.context_today(self)
        sequence = fee_structure.journal_id.sequence_id
        new_name = sequence.with_context(ir_sequence_date=date_invoice).next_by_id()

        waivers = []
        student_waiver = self.env['odoocms.student.fee.waiver']
        if semester_defer:
            lines = self.get_semester_defer_fee_lines(lines, structure_fee_heads, semester_defer_rec, semester)

        tut_defer_line = False
        arrears_amt = 0
        donor_invoice = False
        is_hostel_fee = False

        # if not semester_defer or not suspended_student_fee:
        if not student_defer_or_suspension_flag:
            for structure_fee_head in structure_fee_heads:
                name = structure_fee_head.fee_head_id.product_id.name
                # if not line.domain or self.env['odoocms.student'].search(safe_eval(line.domain)).filtered(lambda l: l.id == self.id):

                if structure_fee_head.line_ids:
                    # structure_head_line ----> odoocms.fee.structure.head.line
                    for structure_head_line in structure_fee_head.line_ids:
                        # Check Here if structure Head Line Receipt have been Generated.
                        same_term_invoice = self.env['account.move'].search([('student_id', '=', self.id), ('term_id', '=', semester.id),
                                                                             ('move_type', '=', 'out_invoice'),
                                                                             ('reversed_entry_id', '=', False),
                                                                             ('invoice_payment_state', '!=', 'cancel')], order='id desc', limit=1)
                        same_term_invoice_reverse_entry = self.env['account.move'].search([('student_id', '=', self.id),
                                                                                           ('reversed_entry_id', '=', same_term_invoice.id),
                                                                                           ('invoice_payment_state', '!=', 'cancel')])
                        if same_term_invoice:
                            if not same_term_invoice_reverse_entry:
                                sm_mvl = self.env['account.move.line'].search([('move_id', '=', same_term_invoice.id),
                                                                               ('fee_head_id', '=', structure_fee_head.fee_head_id.id),
                                                                               ('move_id.invoice_payment_state', '!=', 'cancel')])
                                if sm_mvl:
                                    continue

                        price_unit = 0
                        if self.env['odoocms.student'].search(safe_eval(structure_head_line.domain) + [('id', '=', self.id)]):
                            override_fee_line = False
                            if override_line:
                                override_fee_line = override_line.filtered(lambda l: l.fee_head_id.id==structure_fee_head.fee_head_id.id)
                            qty = 1
                            if structure_fee_head.payment_type=='persubject' and reg:
                                qty = len(reg.failed_subject_ids) + len(reg.to_improve_subject_ids)

                            price_unit = override_fee_line and override_fee_line.fee_amount or (structure_head_line and structure_head_line.amount) or 0
                            if not structure_head_line.currency_id.id==self.env.user.company_id.currency_id.id:
                                price_unit = structure_head_line.currency_id._convert(price_unit, self.env.user.company_id.currency_id, self.env.user.company_id, date_invoice)

                            # EMBA
                            # if structure_fee_head.category_id.name=='Course Fee':
                            if self.program_id.code=='NBS-751':
                                courses = self.get_courses(semester)
                                if courses:
                                    if structure_fee_head.category_id.name=='Tuition Fee':
                                        price_unit = price_unit * len(courses)
                                    if not structure_head_line.currency_id.id==self.env.user.company_id.currency_id.id:
                                        price_unit = structure_head_line.currency_id._convert(price_unit, self.env.user.company_id.currency_id, self.env.user.company_id, date_invoice)
                                        price_unit = price_unit * len(courses)

                            if structure_fee_head.category_id.name=='Tuition Fee':
                                if self.check_tuition_fee_deferment():
                                    defer_line_fee_head = structure_fee_head
                                    tut_defer_line = self.action_create_tuition_deferment_entry()
                                    price_unit = tut_defer_line.deferment_id.approved_tuition_fee

                            waiver_fee_lines = self.env['odoocms.fee.waiver.line'].search([('fee_head_id', '=', structure_fee_head.fee_head_id.id)])
                            if waiver_fee_lines:
                                student_id = False

                                for waiver_fee_line in waiver_fee_lines:
                                    # if self.env['odoocms.student'].search(safe_eval(waiver_fee_line.waiver_id.domain) + [('id', '=', self.id)]):
                                    if waiver_fee_line.waiver_id.domain:
                                        student_id = self.env['odoocms.student'].search(safe_eval(waiver_fee_line.waiver_id.domain) + [('id', '=', self.id)])
                                    if not waiver_fee_line.waiver_id.domain:
                                        student_id = self

                                    if student_id and student_id.tag_ids.filtered(lambda f: f.name not in 'Extra Semester') and waiver_fee_line.waiver_id.type=='waiver':
                                        if waiver_fee_line.waiver_id not in waivers:
                                            waivers.append(waiver_fee_line.waiver_id)
                                            if waiver_fee_line.waiver_type=='percentage':
                                                waiver_price_unit = round(price_unit * waiver_fee_line.percentage / 100.0)
                                            if waiver_fee_line.waiver_type=='fixed':
                                                waiver_price_unit = waiver_fee_line.percentage
                                            # price_unit = price_unit - waiver_price_unit
                                            waiver_amount_for_invoice += waiver_price_unit

                                            data = {
                                                'student_id': self.id,
                                                'name': waiver_fee_line.waiver_id.name,
                                                'waiver_line_id': waiver_fee_line.id,
                                                'term_id': semester.id,
                                                # 'semester_id': self.env['odoocms.term.scheme'].search([('session_id', '=', self.session_id.id), ('semester_id', '=', self.semester_id.id)]).semester_id.id,
                                                'amount': waiver_price_unit,
                                                'amount_percentage': waiver_fee_line.percentage,
                                                'waiver_type': waiver_fee_line.waiver_type,
                                            }
                                            student_waiver += self.env['odoocms.student.fee.waiver'].create(data)

                                            # Invoice Line generation
                                            waiver_value_invl_data = {
                                                'sequence': 1050,
                                                'price_unit': -(round(waiver_price_unit)),
                                                'quantity': qty,
                                                'product_id': waiver_fee_line.fee_head_id.product_id and waiver_fee_line.fee_head_id.product_id.id or False,
                                                'name': waiver_fee_line.waiver_id.name + " (Discounts)",
                                                'account_id': waiver_fee_line.fee_head_id.property_account_income_id.id,
                                                # 'fee_head_id': waiver_fee_line.fee_head_id and waiver_fee_line.fee_head_id.id or False,
                                                # 'analytic_tag_ids': analytic_tag_ids,
                                                'exclude_from_invoice_tab': False,
                                            }
                                            lines.append((0, 0, waiver_value_invl_data))

                                    if student_id and student_id.tag_ids.filtered(lambda f: f.name not in 'Extra Semester') and waiver_fee_line.waiver_id.type=='scholarship':
                                        donor_invoice = self.action_create_donor_invoice(waiver_fee_line, price_unit, semester, structure_fee_head,
                                            fee_structure, invoice_group, receipts, registration_id, date_invoice, date_due, comment, tag, reference)
                                        price_unit = price_unit - donor_invoice.amount_total
                            if structure_fee_head.category_id.name=='Tuition Fee' and self.tag_ids.filtered(lambda f: f.name in ('Summer', 'Extra Semester')):
                                lines = self.action_summer_extra_course_fee(lines, structure_head_line, semester)
                            else:
                                fee_line = {
                                    'sequence': 10,
                                    'price_unit': price_unit,
                                    'quantity': qty,
                                    'product_id': structure_fee_head.fee_head_id.product_id.id,
                                    'name': name,
                                    'account_id': structure_fee_head.fee_head_id.property_account_income_id.id,
                                    # 'account_analytic_id': line.fee_head_id.account_analytic_id,
                                    # 'analytic_tag_ids': analytic_tag_ids,
                                    'fee_head_id': structure_fee_head.fee_head_id.id,
                                    'exclude_from_invoice_tab': False,
                                }
                                lines.append([0, 0, fee_line])

        # Check the Student Hostel Fee
        # if self.hostel_state=='Allocated' and hostel_fee_charge_timing=='semester_fee':
        #     lines = self.get_hostel_fee(lines, semester)
        #     is_hostel_fee = True

        # Checking the Student Ad hoc Charges
        lines = self.get_ad_hoc_charges_line(semester, lines)
        # Get the Student Arrears and Adjustment
        if lines:
            arrears_result = self.get_arrears_adjustments(lines)
            lines = arrears_result[0]
            arrears_amt = arrears_result[1]

        # Fine for Late Payment
        if lines:
            lines = self.create_fine_line(lines)

        if receipts and any([ln[2]['price_unit'] > 0 for ln in lines]):
            if apply_taxes:
                lines = self.create_tax_line(lines, semester, fall_20=True)
            validity_days = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.challan_validity_days') or '30')
            validity_date = date_due + datetime.timedelta(days=validity_days)

            data = {
                'student_id': self.id,
                'student_name': self.partner_id.name,
                'partner_id': self.partner_id.id,
                'fee_structure_id': fee_structure.id,
                'registration_id': registration_id,
                'journal_id': fee_structure.journal_id.id,
                'name': new_name,
                'invoice_date': date_invoice,
                'invoice_date_due': date_due,
                'state': 'draft',
                'narration': cleanhtml(comment),
                'tag': tag,
                'is_fee': True,
                'is_cms': True,
                'is_hostel_fee': is_hostel_fee,
                'reference': reference,
                'move_type': 'out_invoice',
                'invoice_line_ids': lines,
                'receipt_type_ids': [(4, receipt.id, None) for receipt in receipts],
                'waiver_amount': waiver_amount_for_invoice,
                'program_id': self.program_id.id,
                'term_id': semester and semester.id or False,
                # 'semester_id': self.semester_id.id or False,
                'career_id': self.career_id and self.career_id.id or False,
                'institute_id': self.institute_id and self.institute_id.id or False,
                'discipline_id': self.discipline_id and self.discipline_id.id or False,
                'campus_id': self.campus_id and self.campus_id.id or False,
                'study_scheme_id': self.study_scheme_id and self.study_scheme_id.id or False,
                'session_id': self.session_id and self.session_id.id or False,
                'validity_date': validity_date,
            }
            if waivers:
                data['waiver_ids'] = [(4, waiver.id, None) for waiver in waivers]
            invoice = self.env['account.move'].create(data)
            for waiver in student_waiver:
                waiver.invoice_id = invoice.id
            invoice.invoice_group_id = invoice_group

            ledger_amt = invoice.amount_total
            if arrears_amt > 0:
                ledger_amt = invoice.amount_total - arrears_amt
            ledger_data = {
                'student_id': self.id,
                'date': date_invoice,
                'credit': ledger_amt,
                'invoice_id': invoice.id,
            }
            ledger_id = self.env['odoocms.student.ledger'].create(ledger_data)
            invoice.student_ledger_id = ledger_id.id

            # if adm_charges_recs:
            #     adm_charges_recs.write({'receipt_id': invoice.id})

            if semester_defer_rec:
                semester_defer_rec.invoice_id = invoice
            if tut_defer_line:
                tut_defer_line.write({'invoice_date': invoice.invoice_date,
                                      'invoice_date_due': invoice.invoice_date_due,
                                      'original_invoice_id': invoice.id})
                new_defer_invoice = invoice.copy(
                    default={
                        'invoice_date': invoice.invoice_date,
                        'name': new_name,
                        'invoice_date_due': tut_defer_line.deferment_id.installments_start_date or (invoice.invoice_date + relativedelta(months=+50)),
                        'invoice_line_ids': False,
                        'line_ids': [],
                        'waiver_amount': 0.0,
                        'waiver_ids': False,
                    }
                )
                defer_lines = []
                defer_inv_fee_line = {
                    'sequence': 300,
                    'price_unit': tut_defer_line.deferment_id.approved_tuition_fee,
                    'quantity': qty,
                    'product_id': defer_line_fee_head.fee_head_id.product_id.id,
                    'name': name,
                    'account_id': defer_line_fee_head.fee_head_id.property_account_income_id.id,
                    # 'account_analytic_id': line.fee_head_id.account_analytic_id,
                    # 'analytic_tag_ids': analytic_tag_ids,
                    'fee_head_id': defer_line_fee_head.fee_head_id.id,
                    'exclude_from_invoice_tab': False,
                }
                defer_lines.append([0, 0, defer_inv_fee_line])
                new_defer_invoice.invoice_line_ids = defer_lines
                tut_defer_line.defer_invoice_id = new_defer_invoice.id

                defer_ledger_data = {
                    'student_id': self.id,
                    'date': date_invoice,
                    'credit': tut_defer_line.deferment_id.approved_tuition_fee,
                    'invoice_id': new_defer_invoice.id,
                    'is_defer_entry': True,
                }
                defer_ledger_id = self.env['odoocms.student.ledger'].create(defer_ledger_data)
                new_defer_invoice.student_ledger_id = defer_ledger_id.id

            if reg:  # If Subject Registration
                reg.invoice_id = invoice.id

            invoices += invoice
            if donor_invoice:
                invoices += donor_invoice
            if view:
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
                    'views': [(form_view and form_view.id or False, 'form'),
                              (tree_view and tree_view.id or False, 'tree')],
                    # 'context': {'default_class_id': self.id},
                    'type': 'ir.actions.act_window'
                }
            else:
                return invoices
        else:
            return self.env['account.move']

    # Call from above ---> generate_invoice()
    def get_ad_hoc_charges_line(self, term_id, lines):
        for rec in self:
            adm_charges_recs = False
            adm_charges_recs = self.env['odoocms.fee.additional.charges'].search([('student_id', '=', rec.id), ('term_id', '=', term_id.id), ('state', '=', 'draft')])
            if adm_charges_recs:
                for adm_charges_rec in adm_charges_recs:
                    adm_charges_fee_head = adm_charges_rec.charges_type.fee_head_id
                    if not adm_charges_fee_head:
                        continue
                    adm_charges_line = {
                        'sequence': 200,
                        'price_unit': adm_charges_rec.amount,
                        'quantity': 1,
                        'product_id': adm_charges_fee_head.product_id.id,
                        'name': adm_charges_rec.charges_type.name,
                        'account_id': adm_charges_fee_head.property_account_income_id.id,
                        # 'account_analytic_id': line.fee_head_id.account_analytic_id,
                        # 'analytic_tag_ids': analytic_tag_ids,
                        'fee_head_id': adm_charges_fee_head.id,
                        'exclude_from_invoice_tab': False,
                    }
                    lines.append((0, 0, adm_charges_line))
                    adm_charges_rec.state = 'charged'
        return lines

    # Call from above ---> generate_invoice()
    def get_semester_defer_fee_lines(self, lines, structure_fee_heads, semester_defer_rec=False, term_id=False):
        for rec in self:
            ug_first_semester_defer_value = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.ug_first_semester_defer_value') or '100')
            pg_first_semester_defer_value = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.pg_first_semester_defer_value') or '50')
            second_semester_defer_value = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.second_semester_defer_value') or '25')

            # Check Here if structure Head Line Receipt have been Generated.
            same_term_invoice = self.env['account.move'].search([('student_id', '=', rec.id), ('term_id', '=', term_id.id),
                                                                 ('move_type', '=', 'out_invoice'),
                                                                 ('reversed_entry_id', '=', False),
                                                                 ('invoice_payment_state', '!=', 'cancel')], order='id desc', limit=1)
            same_term_invoice_reverse_entry = self.env['account.move'].search([('student_id', '=', rec.id),
                                                                               ('reversed_entry_id', '=', same_term_invoice.id),
                                                                               ('invoice_payment_state', '!=', 'cancel')])

            per_factor = 0
            # semester = self.semester_id.number
            if semester_defer_rec:
                semester = semester_defer_rec.semester_id.number
            else:
                semester = rec.semester_id.number

            if semester==1:
                if self.career_id.code=='UG':
                    per_factor = ug_first_semester_defer_value
                if not self.career_id.code=='UG':
                    per_factor = pg_first_semester_defer_value
            else:
                per_factor = second_semester_defer_value

            for structure_fee_head in structure_fee_heads.filtered(lambda h: h.category_id.name=='Tuition Fee'):
                if structure_fee_head.line_ids:
                    for structure_head_line in structure_fee_head.line_ids:
                        if same_term_invoice:
                            if not same_term_invoice_reverse_entry:
                                sm_mvl = self.env['account.move.line'].search([('move_id', '=', same_term_invoice.id), ('fee_head_id', '=', structure_fee_head.fee_head_id.id)])
                                if sm_mvl:
                                    continue

                        if self.env['odoocms.student'].search(safe_eval(structure_head_line.domain) + [('id', '=', self.id)]):
                            price_unit = structure_head_line.amount or 0
                            if not structure_head_line.currency_id.id==self.env.user.company_id.currency_id.id:
                                price_unit = structure_head_line.currency_id._convert(price_unit, self.env.user.company_id.currency_id, self.env.user.company_id, fields.Date.today())
                            price_unit = round(price_unit * per_factor / 100, 2)
                            defer_sem_tut = {
                                'sequence': 1001,
                                'price_unit': price_unit,
                                'quantity': 1,
                                'product_id': structure_fee_head.fee_head_id.product_id.id,
                                'name': structure_fee_head.category_id.name,
                                'account_id': structure_fee_head.fee_head_id.property_account_income_id.id,
                                'fee_head_id': structure_fee_head.fee_head_id.id,
                                'exclude_from_invoice_tab': False,
                                # 'account_analytic_id': line.fee_head_id.account_analytic_id,
                                # 'analytic_tag_ids': analytic_tag_ids,
                            }
                            lines.append((0, 0, defer_sem_tut))

            rep_courses = self.env['odoocms.student.course'].search([('student_id', '=', rec.id),
                                                                     ('term_id', '=', term_id.id)])
            if rep_courses:
                extra_fee_head = self.env['odoocms.fee.head'].search([('name', '=', 'Tuition Fee Per Course')])
                if not extra_fee_head:
                    extra_fee_head = self.env['odoocms.fee.head'].search([('id', '=', '73')])
                local_student_credit_hour_fee = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.local_student_credit_hour_fee') or '5000')
                foreign_student_credit_hour_fee = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.foreign_student_credit_hour_fee') or '40')

                for course in rep_courses:
                    currency_id = self.env['res.currency'].search([('id', '=', 2)])
                    course_credit = course.course_id and course.course_id.credits or 0
                    # price = 5000
                    price = local_student_credit_hour_fee
                    if rec.tag_ids.filtered(lambda t: t.code=='NFS'):
                        # price = 40
                        price = foreign_student_credit_hour_fee
                        price = currency_id._convert(price, self.env.user.company_id.currency_id, self.env.user.company_id, fields.Date.today())
                    price_unit = price * course_credit
                    new_name = course.primary_class_id.code + "-" + course.primary_class_id.name + " Tuition Fee"

                    if same_term_invoice:
                        if not same_term_invoice_reverse_entry:
                            sm_mvl = self.env['account.move.line'].search([('move_id', '=', same_term_invoice.id), ('course_id', '=', course.id)])
                            if sm_mvl:
                                continue

                    defer_sem_tut = {
                        'name': new_name,
                        'quantity': 1,
                        'price_unit': price_unit,
                        'product_id': extra_fee_head and extra_fee_head.id or False,
                        'account_id': extra_fee_head and extra_fee_head.property_account_income_id.id or False,
                        'fee_head_id': extra_fee_head and extra_fee_head.id or False,
                        'exclude_from_invoice_tab': False,
                        # 'account_analytic_id': line.fee_head_id.account_analytic_id,
                        # 'analytic_tag_ids': analytic_tag_ids,
                    }
                    lines.append((0, 0, defer_sem_tut))

        return lines

    # Call from above ---> generate_invoice()
    def check_tuition_fee_deferment(self):
        for rec in self:
            ret_value = False
            rec_exist = self.env['odoocms.tuition.fee.deferment.request'].search([('student_id', '=', rec.id),
                                                                                  ('career_id', '=', rec.career_id.id),
                                                                                  ('state', '=', 'approved')])
            if rec_exist:
                ret_value = True
        return ret_value

    # Call from above ---> generate_invoice()
    def action_create_tuition_deferment_entry(self):
        for rec in self:
            new_defer_line = False
            defer_rec = self.env['odoocms.tuition.fee.deferment.request'].search([('student_id', '=', rec.id),
                                                                                  ('career_id', '=', rec.career_id.id),
                                                                                  ('state', '=', 'approved')])
            if defer_rec:
                defer_values = {
                    'student_id': rec.id,
                    'deferment_id': defer_rec.id,
                    'amount': defer_rec.approved_tuition_fee,
                    'state': 'draft',
                }
                new_defer_line = self.env['odoocms.tuition.fee.deferment.line'].create(defer_values)
        return new_defer_line

    # Call from above ---> generate_invoice()
    def action_summer_extra_course_fee(self, lines, structure_head_line, term_id):
        for rec in self:
            extra_fee_head = self.env['odoocms.fee.head'].search([('name', '=', 'Tuition Fee Per Course')])
            if not extra_fee_head:
                extra_fee_head = self.env['odoocms.fee.head'].search([('id', '=', '73')])

            local_student_credit_hour_fee = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.local_student_credit_hour_fee') or '5000')
            foreign_student_credit_hour_fee = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.foreign_student_credit_hour_fee') or '40')

            extra_courses = self.env['odoocms.student.course'].search([('student_id', '=', rec.id),
                                                                       ('term_id', '=', term_id.id)])
            if extra_courses:
                for course in extra_courses:
                    # price = 5000
                    # Check Here if structure Head Line Receipt have been Generated.
                    same_term_invoice = self.env['account.move'].search([('student_id', '=', rec.id),
                                                                         ('term_id', '=', term_id.id),
                                                                         ('move_type', '=', 'out_invoice'),
                                                                         ('reversed_entry_id', '=', False),
                                                                         ('invoice_payment_state', '!=', 'cancel')], order='id desc', limit=1)
                    same_term_invoice_reverse_entry = self.env['account.move'].search([('student_id', '=', rec.id),
                                                                                       ('reversed_entry_id', '=', same_term_invoice.id),
                                                                                       ('invoice_payment_state', '!=', 'cancel')])
                    if same_term_invoice:
                        if not same_term_invoice_reverse_entry:
                            sm_mvl = self.env['account.move.line'].search([('move_id', '=', same_term_invoice.id), ('course_id', '=', course.id)])
                            if sm_mvl:
                                continue

                    price = local_student_credit_hour_fee
                    course_credit = course.course_id and course.course_id.credits or 0
                    price_unit = price * course_credit
                    if rec.tag_ids.filtered(lambda t: t.code=='NFS'):
                        # price = 40
                        price = foreign_student_credit_hour_fee
                        price = structure_head_line.currency_id._convert(price, self.env.user.company_id.currency_id, self.env.user.company_id, fields.Date.today())
                        price_unit = price * course_credit
                    new_name = course.primary_class_id.code + "-" + course.primary_class_id.name + " Tuition Fee"
                    extra_fee_lines = {
                        'name': new_name,
                        'quantity': 1,
                        'price_unit': price_unit,
                        'course_id': course.id,
                        'product_id': extra_fee_head and extra_fee_head.id or False,
                        'account_id': extra_fee_head and extra_fee_head.property_account_income_id.id or False,
                        'fee_head_id': extra_fee_head and extra_fee_head.id or False,
                        'exclude_from_invoice_tab': False,
                        # 'account_analytic_id': line.fee_head_id.account_analytic_id,
                        # 'analytic_tag_ids': analytic_tag_ids,
                    }
                    lines.append((0, 0, extra_fee_lines))
        return lines

    def get_courses(self, term_id=False):
        for rec in self:
            if term_id:
                courses = self.env['odoocms.student.course'].sudo().search([('student_id', '=', rec.id),
                                                                            ('session_id', '=', rec.session_id.id),
                                                                            ('term_id', '=', term_id.id)])
                if courses:
                    return courses
        return []

    # Checking the Student Arrears and Advance Payment Paid
    def get_arrears_adjustments(self, lines):
        for rec in self:
            qty = 1
            balance = 0
            ledger_lines = self.env['odoocms.student.ledger'].search([('student_id', '=', rec.id), ('is_defer_entry', '!=', True)])
            if ledger_lines:
                credit_sum = 0
                debit_sum = 0
                for ledger_line in ledger_lines:
                    if not ledger_line.invoice_id.is_hostel_fee:  # Temp Added This Condition For Spring 2021
                        credit_sum += ledger_line.credit
                        debit_sum += ledger_line.debit
                        balance = (credit_sum - debit_sum)

                # If Student Have The Arrears
                if balance > 0:
                    open_invoices = self.env['account.move'].search([('invoice_payment_state', '=', 'open'),
                                                                     ('student_id', '=', rec.id),
                                                                     ('move_type', '=', 'out_invoice'),
                                                                     ('sub_invoice', '=', False)])

                    arrears_fee_head = self.env['odoocms.fee.head'].search([('category_id.name', '=', 'Arrears')], order='id', limit=1)
                    arrears_line = {
                        'sequence': 1000,
                        'price_unit': round(balance),
                        'quantity': qty,
                        'product_id': arrears_fee_head.product_id and arrears_fee_head.product_id.id or False,
                        'name': arrears_fee_head.product_id and arrears_fee_head.product_id.name or 'Previous Arrears ',
                        'account_id': arrears_fee_head.property_account_income_id.id,
                        # 'analytic_tag_ids': analytic_tag_ids,
                        'fee_head_id': arrears_fee_head.id,
                        'exclude_from_invoice_tab': False,
                    }
                    lines.append((0, 0, arrears_line))

                # If Student Have The Paid the Extra Amount, then make the Adjustment in the Fee Receipt
                if balance < 0:
                    adjustment_amount = balance
                    adjustment_fee_head = self.env['odoocms.fee.head'].search([('category_id.name', '=', "Previous Month's Fee Adjustment")], order='id', limit=1)
                    adjustment_line = {
                        'price_unit': round(balance),
                        'quantity': qty,
                        'product_id': adjustment_fee_head.product_id and adjustment_fee_head.product_id.id or False,
                        'name': adjustment_fee_head.product_id and adjustment_fee_head.product_id.name or 'Adjustment',
                        'account_id': adjustment_fee_head.property_account_income_id.id,
                        # 'analytic_tag_ids': analytic_tag_ids,
                        'fee_head_id': adjustment_fee_head.id,
                        'exclude_from_invoice_tab': False,
                    }
                    lines.append((0, 0, adjustment_line))
        return lines, balance

    def create_fine_line(self, lines):
        for rec in self:
            fee_head = self.env['odoocms.fee.head'].search([('name', '=', 'Fine')])
            if not fee_head:
                raise UserError(_("Fine Fee Head is not defined in the System."))
            fine_line = {
                'sequence': 900,
                'price_unit': 0,
                'quantity': 1,
                'product_id': fee_head.product_id.id,
                'name': "Fine For Late Payment of Tuition Fee",
                'account_id': fee_head.property_account_income_id.id,
                # 'account_analytic_id': line.fee_head_id.account_analytic_id,
                # 'analytic_tag_ids': analytic_tag_ids,
                'fee_head_id': fee_head.id,
                'exclude_from_invoice_tab': False,
            }
            lines.append([0, 0, fine_line])
        return lines

    def get_hostel_fee(self, lines, term_id):
        for rec in self:
            hostel_fee_charge_months = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.hostel_fee_charge_months') or '6')
            fee_head = self.env['odoocms.fee.head'].search([('hostel_fee', '=', True)], order='id', limit=1)
            if not fee_head:
                raise UserError(_("Hostel Fee Head is not defined in the System."))
            name = self.hostel_id and self.hostel_id.name or ''

            # Check Here if structure Head Line Receipt have been Generated.
            same_term_invoice = self.env['account.move'].search([('student_id', '=', self.id),
                                                                 ('term_id', '=', term_id.id),
                                                                 ('move_type', '=', 'out_invoice'),
                                                                 ('reversed_entry_id', '=', False)], order='id desc', limit=1)
            same_term_invoice_reverse_entry = self.env['account.move'].search([('student_id', '=', self.id),
                                                                               ('reversed_entry_id', '=', same_term_invoice.id)])
            if same_term_invoice:
                if not same_term_invoice_reverse_entry:
                    sm_mvl = self.env['account.move.line'].search([('move_id', '=', same_term_invoice.id),
                                                                   ('fee_head_id', '=', fee_head.id)])
                    if sm_mvl:
                        continue

            price = 0
            price_unit = 0
            if self.tag_ids:
                is_nfs_student = self.tag_ids.filtered(lambda t: t.code=='NFS')
                if is_nfs_student:
                    price = self.room_id.per_month_rent_int
                    price = self.room_id.room_type.currency_id._convert(price, self.env.user.company_id.currency_id, self.env.user.company_id, fields.Date.today())
                    price_unit = round(price * hostel_fee_charge_months, 2)
                else:
                    price = self.room_id.per_month_rent
                    price_unit = round(price * hostel_fee_charge_months, 2)

            hostel_fee_line = {
                'sequence': 500,
                'price_unit': price_unit,
                'quantity': 1,
                'product_id': fee_head.product_id.id,
                'name': name + " Fee",
                'account_id': fee_head.property_account_income_id.id,
                # 'account_analytic_id': line.fee_head_id.account_analytic_id,
                # 'analytic_tag_ids': analytic_tag_ids,
                'fee_head_id': fee_head.id,
                'exclude_from_invoice_tab': False,
            }
            lines.append([0, 0, hostel_fee_line])
        return lines

    def create_tax_line(self, lines, term_id, fall_20):
        tax_rate = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.tax_rate') or '5')
        taxable_amount = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.taxable_amount') or '200000')
        taxable_fee_heads = self.env['odoocms.fee.head'].search([('taxable', '=', True)])

        previous_term_taxable_amt = 0
        current_term_taxable_amt = 0
        net_amount = 0
        tax_amount = 0
        for rec in self:
            if not fall_20:
                prev_term_inv = self.env['account.move'].search([('student_id', '=', rec.id),
                                                                 ('is_scholarship_fee', '!=', True),
                                                                 ('term_id', '!=', term_id.id),
                                                                 ('invoice_payment_state', '!=', 'cancel')], order='id desc', limit=1)
                if prev_term_inv:
                    previous_term = prev_term_inv.term_id
                    prev_term_invoices = self.env['account.move'].search([('student_id', '=', rec.id),
                                                                          ('is_scholarship_fee', '!=', True),
                                                                          ('term_id', '=', previous_term.id),
                                                                          ('invoice_payment_state', '!=', 'cancel')])
                    if prev_term_invoices:
                        if taxable_fee_heads:
                            for prev_term_invoice in prev_term_invoices:
                                taxable_lines = prev_term_invoice.invoice_line_ids.filtered(lambda l: l.fee_head_id.id in taxable_fee_heads.ids)
                                if taxable_lines:
                                    for taxable_line in taxable_lines:
                                        previous_term_taxable_amt += taxable_line.price_subtotal

            # For this Set fall_20 True from Calling point
            if fall_20:
                fall20_fee_recs = self.env['nust.student.fall20.fee'].search([('student_id', '=', rec.id)])
                if fall20_fee_recs:
                    for fall20_fee_rec in fall20_fee_recs:
                        fall20_fee_rec.fee_status = 'c'
                        previous_term_taxable_amt += fall20_fee_rec.amount

            for line in lines:
                # if not 'Discounts' in line[2]:
                if line[2]['price_unit'] < 0:
                    current_term_taxable_amt += line[2]['price_unit']
                else:
                    if line[2]['fee_head_id'] in taxable_fee_heads.ids:
                        current_term_taxable_amt += line[2]['price_unit']

            net_amount = previous_term_taxable_amt + current_term_taxable_amt

            if net_amount > taxable_amount:
                tax_amount = round(net_amount * (tax_rate / 100), 3)

            fee_head = self.env['odoocms.fee.head'].search([('name', '=', 'Advance Tax')])
            if not fee_head:
                raise UserError(_("Advance Tax Fee Head is not defined in the System."))
            if tax_amount > 0:
                tax_line = {
                    'sequence': 900,
                    'price_unit': tax_amount,
                    'quantity': 1,
                    'product_id': fee_head.product_id.id,
                    'name': "Tax Charged on Fee",
                    'account_id': fee_head.property_account_income_id.id,
                    # 'account_analytic_id': line.fee_head_id.account_analytic_id,
                    # 'analytic_tag_ids': analytic_tag_ids,
                    'fee_head_id': fee_head.id,
                    'exclude_from_invoice_tab': False,
                }
                lines.append([0, 0, tax_line])
        return lines

    def action_create_donor_invoice(self, waiver_fee_line, price_unit, semester, structure_fee_head, fee_structure,
                                    invoice_group, receipts, registration_id, date_invoice, date_due, comment, tag, reference):
        due_date = (date_due + relativedelta(months=+6))
        sequence = fee_structure.journal_id.sequence_id
        new_name = sequence.with_context(ir_sequence_date=date_invoice).next_by_id()
        for rec in self:
            student_scholarship = self.env['odoocms.student.fee.scholarship']
            scholarship_amount_for_invoice = 0
            if waiver_fee_line.waiver_type=='percentage':
                scholarship_price_unit = round(price_unit * waiver_fee_line.percentage / 100.0)
            if waiver_fee_line.waiver_type=='fixed':
                scholarship_price_unit = waiver_fee_line.percentage
            price_unit = price_unit - scholarship_price_unit
            scholarship_amount_for_invoice += scholarship_price_unit

            data = {
                'student_id': self.id,
                'name': waiver_fee_line.waiver_id.name,
                'waiver_line_id': waiver_fee_line.id,
                'term_id': semester.id,
                # 'semester_id': self.env['odoocms.term.scheme'].search([('session_id', '=', self.session_id.id), ('semester_id', '=', self.semester_id.id)]).semester_id.id,
                'amount': scholarship_price_unit,
                'amount_percentage': waiver_fee_line.percentage,
                'waiver_type': waiver_fee_line.waiver_type,
                'donor_id': waiver_fee_line.waiver_id.donor_id and waiver_fee_line.waiver_id.donor_id.id or False,
            }
            student_scholarship += self.env['odoocms.student.fee.scholarship'].create(data)

            lines = []
            fee_line = {
                'price_unit': scholarship_amount_for_invoice,
                'quantity': 1,
                'product_id': structure_fee_head.fee_head_id.product_id.id,
                'name': waiver_fee_line.waiver_id.name,
                'account_id': structure_fee_head.fee_head_id.property_account_income_id.id,
                # 'account_analytic_id': line.fee_head_id.account_analytic_id,
                # 'analytic_tag_ids': analytic_tag_ids,
                'fee_head_id': structure_fee_head.fee_head_id.id,
                'exclude_from_invoice_tab': False,
            }
            lines.append([0, 0, fee_line])

            data = {
                'student_id': self.id,
                'student_name': self.partner_id.name,
                'partner_id': waiver_fee_line.waiver_id.donor_id.partner_id.id,
                'fee_structure_id': fee_structure.id,
                'registration_id': registration_id,
                'journal_id': fee_structure.journal_id.id,
                'name': new_name,
                'invoice_date': date_invoice,
                'invoice_date_due': due_date,
                'state': 'draft',
                'narration': comment,
                'tag': tag,
                'is_fee': True,
                'is_cms': True,
                'is_scholarship_fee': True,
                'reference': reference,
                'move_type': 'out_invoice',
                'invoice_line_ids': lines,
                'receipt_type_ids': [(4, receipt.id, None) for receipt in receipts],
                'waiver_amount': 0,
                'program_id': self.program_id.id,
                'term_id': semester and semester.id or False,
                # 'semester_id': self.semester_id.id or False,
                'career_id': self.career_id and self.career_id.id or False,
                'institute_id': self.institute_id and self.institute_id.id or False,
                'discipline_id': self.discipline_id and self.discipline_id.id or False,
                'campus_id': self.campus_id and self.campus_id.id or False,
                'study_scheme_id': self.study_scheme_id and self.study_scheme_id.id or False,
                'session_id': self.session_id and self.session_id.id or False,
                'donor_id': waiver_fee_line.waiver_id.donor_id.id,
            }
            invoice = self.env['account.move'].create(data)
            for scholarship in student_scholarship:
                scholarship.invoice_id = invoice.id
            invoice.invoice_group_id = invoice_group
        return invoice

    def generate_hostel_invoice(self, description_sub, semester, receipts, date_due, comment='', tag=False,
                                reference=False, invoice_group=False, registration_id=False):
        registration_id = registration_id.id
        fee_structure = self.env['odoocms.fee.structure'].search([('session_id', '=', self.session_id.id),
                                                                  ('term_id', '=', semester.id),
                                                                  ('career_id', '=', self.career_id.id)
                                                                  ], order='id desc', limit=1)
        if not fee_structure.journal_id.sequence_id:
            raise UserError(_('Please define sequence on the Journal related to this Invoice.'))

        date_invoice = fields.Date.context_today(self)
        sequence = fee_structure.journal_id.sequence_id
        new_name = sequence.with_context(ir_sequence_date=date_invoice).next_by_id()
        lines = []
        invoices = self.env['account.move']

        if self.hostel_state=='Allocated':
            hostel_fee_charge_months = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.hostel_fee_charge_months') or '6')
            fee_head = self.env['odoocms.fee.head'].search([('hostel_fee', '=', True)], order='id', limit=1)
            if not fee_head:
                raise UserError(_("Hostel Fee Head is not defined in the System."))
            name = self.hostel_id and self.hostel_id.name or ''

            # Check Here if structure Head Line Receipt have been Generated.
            same_term_invoice = self.env['account.move'].search([('student_id', '=', self.id),
                                                                 ('term_id', '=', semester.id),
                                                                 ('move_type', '=', 'out_invoice'),
                                                                 ('reversed_entry_id', '=', False),
                                                                 ('invoice_payment_state', '!=', 'cancel')
                                                                 ], order='id desc', limit=1)
            same_term_invoice_reverse_entry = self.env['account.move'].search([('student_id', '=', self.id),
                                                                               ('reversed_entry_id', '=', same_term_invoice.id),
                                                                               ('invoice_payment_state', '!=', 'cancel')
                                                                               ])
            sm_mvl = False
            if same_term_invoice:
                if not same_term_invoice_reverse_entry:
                    sm_mvl = self.env['account.move.line'].search([('move_id', '=', same_term_invoice.id),
                                                                   ('fee_head_id', '=', fee_head.id),
                                                                   ('move_id.invoice_payment_state', '!=', 'cancel')
                                                                   ])

            if not sm_mvl:
                price = 0
                price_unit = 0
                if self.tag_ids:
                    is_nfs_student = self.tag_ids.filtered(lambda t: t.code=='NFS')
                    if is_nfs_student:
                        price = self.room_id.per_month_rent_int
                        price = self.room_id.room_type.currency_id._convert(price, self.env.user.company_id.currency_id, self.env.user.company_id, fields.Date.today())
                        price_unit = round(price * hostel_fee_charge_months, 2)
                    else:
                        price = self.room_id.per_month_rent
                        price_unit = round(price * hostel_fee_charge_months, 2)

                hostel_fee_line = {
                    'sequence': 10,
                    'price_unit': price_unit,
                    'quantity': 1,
                    'product_id': fee_head.product_id.id,
                    'name': name + " Fee",
                    'account_id': fee_head.property_account_income_id.id,
                    'fee_head_id': fee_head.id,
                    'exclude_from_invoice_tab': False,
                }
                lines.append([0, 0, hostel_fee_line])

        # Tax Calc
        # if Not NUST Foreign Student (Do not Apply the Tax on Foreign Student)
        if not self.tag_ids.filtered(lambda t: t.code=='NFS'):
            if lines:
                tax_rate = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.tax_rate') or '5')
                taxable_amount = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.taxable_amount') or '200000')
                taxable_fee_heads = self.env['odoocms.fee.head'].search([('taxable', '=', True)])

                previous_term_taxable_amt = 0
                current_term_taxable_amt = 0
                net_amount = 0
                tax_amount = 0
                prev_tax_amount = 0
                net_tax_amount = 0

                receipt_ids = self.env['account.move'].search([('student_id', '=', self.id),
                                                               ('term_id', '=', semester.id),
                                                               ('is_hostel_fee', '=', False),
                                                               ('is_scholarship_fee', '=', False),
                                                               ('move_type', '=', 'out_invoice'),
                                                               ('reversed_entry_id', '=', False),
                                                               ('invoice_payment_state', '!=', 'cancel')])
                if receipt_ids:
                    fall20_fee_recs = self.env['nust.student.fall20.fee'].search([('student_id', '=', self.id)])
                    if fall20_fee_recs:
                        for fall20_fee_rec in fall20_fee_recs:
                            previous_term_taxable_amt += fall20_fee_rec.amount
                    for receipt_id in receipt_ids:
                        for receipt_line in receipt_id.invoice_line_ids:
                            if receipt_line.price_unit < 0:
                                current_term_taxable_amt += receipt_line.price_unit
                            else:
                                if receipt_line.fee_head_id.id in taxable_fee_heads.ids:
                                    current_term_taxable_amt += receipt_line.price_unit

                net_amount = previous_term_taxable_amt + current_term_taxable_amt + price_unit

                if net_amount > taxable_amount:
                    tax_amount = round(net_amount * (tax_rate / 100), 3)

                fee_head = self.env['odoocms.fee.head'].search([('name', '=', 'Advance Tax')])
                if not fee_head:
                    raise UserError(_("Advance Tax Fee Head is not defined in the System."))

                for receipt_id in receipt_ids:
                    prev_tax_rec = self.env['account.move.line'].search([('move_id', '=', receipt_id.id),
                                                                         ('fee_head_id', '=', fee_head.id)])
                    if prev_tax_rec:
                        prev_tax_amount = prev_tax_rec.price_subtotal

                net_tax_amount = tax_amount - prev_tax_amount

                if net_tax_amount > 0:
                    tax_line = {
                        'sequence': 900,
                        'price_unit': net_tax_amount,
                        'quantity': 1,
                        'product_id': fee_head.product_id.id,
                        'name': "Tax Charged on Fee",
                        'account_id': fee_head.property_account_income_id.id,
                        # 'account_analytic_id': line.fee_head_id.account_analytic_id,
                        # 'analytic_tag_ids': analytic_tag_ids,
                        'fee_head_id': fee_head.id,
                        'exclude_from_invoice_tab': False,
                    }
                    lines.append([0, 0, tax_line])

        # Fine for Late Payment
        if lines:
            lines = self.create_fine_line(lines)

        if receipts and any([ln[2]['price_unit'] > 0 for ln in lines]):
            validity_days = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.challan_validity_days') or '30')
            validity_date = date_due + datetime.timedelta(days=validity_days)

            data = {
                'student_id': self.id,
                'student_name': self.partner_id.name,
                'partner_id': self.partner_id.id,
                'fee_structure_id': fee_structure.id,
                'registration_id': registration_id,
                'journal_id': fee_structure.journal_id.id,
                'name': new_name,
                'invoice_date': date_invoice,
                'invoice_date_due': date_due,
                'state': 'draft',
                'narration': cleanhtml(comment),
                'tag': tag,
                'is_fee': True,
                'is_cms': True,
                'is_hostel_fee': True,
                'reference': reference,
                'move_type': 'out_invoice',
                'invoice_line_ids': lines,
                'receipt_type_ids': [(4, receipt.id, None) for receipt in receipts],
                'waiver_amount': 0,
                'program_id': self.program_id.id,
                'term_id': semester and semester.id or False,
                # 'semester_id': self.semester_id.id or False,
                'career_id': self.career_id and self.career_id.id or False,
                'institute_id': self.institute_id and self.institute_id.id or False,
                'discipline_id': self.discipline_id and self.discipline_id.id or False,
                'campus_id': self.campus_id and self.campus_id.id or False,
                'study_scheme_id': self.study_scheme_id and self.study_scheme_id.id or False,
                'session_id': self.session_id and self.session_id.id or False,
                'validity_date': validity_date,
            }
            invoice = self.env['account.move'].create(data)
            invoices += invoice
            invoice.invoice_group_id = invoice_group

            ledger_amt = invoice.amount_total
            ledger_data = {
                'student_id': self.id,
                'date': date_invoice,
                'credit': ledger_amt,
                'invoice_id': invoice.id,
                'description': 'Hostel Fee For ' + semester.name
            }
            ledger_id = self.env['odoocms.student.ledger'].create(ledger_data)
            invoice.student_ledger_id = ledger_id.id
        return invoices

    def generate_ad_hoc_charges_invoice(self, description_sub, semester, receipts, date_due, comment='', tag=False,
                                        reference=False, invoice_group=False, registration_id=False):
        registration_id = registration_id.id
        fee_structure = self.env['odoocms.fee.structure'].search([('session_id', '=', self.session_id.id),
                                                                  ('term_id', '=', semester.id),
                                                                  ('career_id', '=', self.career_id.id)
                                                                  ], order='id desc', limit=1)
        if not fee_structure.journal_id.sequence_id:
            raise UserError(_('Please define sequence on the Journal related to this Invoice.'))
        date_invoice = fields.Date.context_today(self)
        sequence = fee_structure.journal_id.sequence_id
        new_name = sequence.with_context(ir_sequence_date=date_invoice).next_by_id()
        lines = []
        invoices = self.env['account.move']
        adm_charges_recs = False
        ledger_desc = 'Ad Hoc Charges Against '
        adm_charges_recs = self.env['odoocms.fee.additional.charges'].search([('student_id', '=', self.id), ('term_id', '=', semester.id), ('state', '=', 'draft')])
        if adm_charges_recs:
            for adm_charges_rec in adm_charges_recs:
                adm_charges_fee_head = adm_charges_rec.charges_type.fee_head_id
                ledger_desc = ledger_desc + adm_charges_rec.charges_type.name + " "
                if not adm_charges_fee_head:
                    continue
                adm_charges_line = {
                    'sequence': 10,
                    'price_unit': adm_charges_rec.amount,
                    'quantity': 1,
                    'product_id': adm_charges_fee_head.product_id.id,
                    'name': adm_charges_rec.charges_type.name,
                    'account_id': adm_charges_fee_head.property_account_income_id.id,
                    # 'account_analytic_id': line.fee_head_id.account_analytic_id,
                    # 'analytic_tag_ids': analytic_tag_ids,
                    'fee_head_id': adm_charges_fee_head.id,
                    'exclude_from_invoice_tab': False,
                }
                lines.append((0, 0, adm_charges_line))
                adm_charges_rec.state = 'charged'

        # Fine for Late Payment
        if lines:
            lines = self.create_fine_line(lines)

        if receipts and any([ln[2]['price_unit'] > 0 for ln in lines]):
            validity_days = int(self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.challan_validity_days') or '30')
            validity_date = date_due + datetime.timedelta(days=validity_days)

            data = {
                'student_id': self.id,
                'student_name': self.partner_id.name,
                'partner_id': self.partner_id.id,
                'fee_structure_id': fee_structure.id,
                'registration_id': registration_id,
                'journal_id': fee_structure.journal_id.id,
                'name': new_name,
                'invoice_date': date_invoice,
                'invoice_date_due': date_due,
                'state': 'draft',
                'narration': cleanhtml(comment),
                'tag': tag,
                'is_fee': True,
                'is_cms': True,
                'is_hostel_fee': False,
                'reference': reference,
                'move_type': 'out_invoice',
                'invoice_line_ids': lines,
                'receipt_type_ids': [(4, receipt.id, None) for receipt in receipts],
                'waiver_amount': 0,
                'program_id': self.program_id.id,
                'term_id': semester and semester.id or False,
                # 'semester_id': self.semester_id.id or False,
                'career_id': self.career_id and self.career_id.id or False,
                'institute_id': self.institute_id and self.institute_id.id or False,
                'discipline_id': self.discipline_id and self.discipline_id.id or False,
                'campus_id': self.campus_id and self.campus_id.id or False,
                'study_scheme_id': self.study_scheme_id and self.study_scheme_id.id or False,
                'session_id': self.session_id and self.session_id.id or False,
                'validity_date': validity_date,
            }
            invoice = self.env['account.move'].create(data)
            invoices += invoice
            invoice.invoice_group_id = invoice_group

            ledger_amt = invoice.amount_total
            ledger_data = {
                'student_id': self.id,
                'date': date_invoice,
                'credit': ledger_amt,
                'invoice_id': invoice.id,
                'description': ledger_desc,
            }
            ledger_id = self.env['odoocms.student.ledger'].create(ledger_data)
            invoice.student_ledger_id = ledger_id.id
        return invoices


# SARFRAZ 10-11-2020
# To check the Structure With FAROOQ SB
# class OdooCMSApplication(models.Model):
#     _inherit = 'odoocms.application'
#
#     feemerit = fields.Selection([
#         ('regular', 'Regular'), ('self', 'Self Finance'), ('rationalized', 'Rationalized')
#     ], 'Fee Merit', default='regular')
#
#     hostel_facility = fields.Boolean('Hostel Facility')
#     hostel_cubical = fields.Boolean('Cubical')
#
#     def generate_invoice(self, view=False):
#         fee_structure = self.env['odoocms.fee.structure'].search(
#             [('academic_session_id', '=', self.academic_session_id.id)])
#
#         lines = []
#         invoices = self.env['account.move']
#         payment_types = ['admissiontime', 'persemester']
#         # current_semester_number = self.semester_id.number
#         next_semester_number = 1  # current_semester_number + 1
#
#         if next_semester_number % 2==1:
#             payment_types.append('peryear')
#
#         structure_fee_heads = fee_structure.line_ids.filtered(
#             lambda l: l.payment_type in payment_types
#                       and (not l.program_ids or self.program_id.id in l.program_ids.ids)
#                       and (not l.semester_ids or next_semester_number in l.semester_ids.ids)
#         )
#
#         analytic_tags = self.env['account.analytic.tag']
#         analytic_tags += self.program_id.department_id.campus_id.analytic_tag_id
#         analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in analytic_tags]
#
#         if not fee_structure.journal_id.sequence_id:
#             raise UserError(_('Please define sequence on the journal related to this invoice.'))
#
#         date_invoice = fields.Date.context_today(self)
#         date_due = date_invoice + relativedelta(days=15)
#
#         sequence = fee_structure.journal_id.sequence_id
#         new_name = sequence.with_context(ir_sequence_date=date_invoice).next_by_id()
#
#         for line in structure_fee_heads:
#             # name = line.fee_type.product_id.description_sale
#             # if not name:
#             #    name = line.fee_type.product_id.name
#             name = line.fee_head_id.product_id.name
#
#             # if not line.applied_if or eval('self.' + line.applied_if.name):
#             # if not line.domain or self.env['odoocms.application'].search([(line.domain + [('id', '=', self.id)])]):
#             fee_line = {
#                 'price_unit': line.fee_amount,
#                 'quantity': 1.00,
#                 'product_id': line.fee_head_id.product_id.id,
#                 'name': name,
#                 'account_id': line.fee_head_id.property_account_income_id.id,
#                 # 'account_analytic_id': line.fee_head_id.account_analytic_id,
#                 'analytic_tag_ids': line.fee_head_id.analytic_tag_ids.ids,
#             }
#             lines.append([0, 0, fee_line])
#
#         data = {
#             'applicant_id': self.id,
#             'partner_id': 1,  # self.partner_id.id,
#             'fee_structure_id': fee_structure.id,
#             'program_id': self.program_id.id,
#             'is_fee': True,
#             'is_cms': True,
#             'student_name': self.name + '-' + self.last_name,
#             'invoice_line_ids': lines,
#             'journal_id': fee_structure.journal_id.id,
#             'number': new_name,
#             'date_invoice': date_invoice,
#             'date_due': date_due,
#             'state': 'draft',
#         }
#         invoices += self.env['account.move'].create(data)
#
#         if view:
#             invoice_list = invoices.mapped('id')
#             form_view = self.env.ref('odoocms_fee.odoocms_receipt_form')
#             tree_view = self.env.ref('odoocms_fee.odoocms_receipt_tree')
#             return {
#                 'domain': [('id', 'in', invoice_list)],
#                 'name': _('Invoices'),
#                 'view_type': 'form',
#                 'view_mode': 'tree,form',
#                 'res_model': 'account.move',
#                 'view_id': False,
#                 'views': [(form_view and form_view.id or False, 'form'),
#                           (tree_view and tree_view.id or False, 'tree')],
#                 # 'context': {'default_class_id': self.id},
#                 'type': 'ir.actions.act_window'
#             }
#         else:
#             return invoices
