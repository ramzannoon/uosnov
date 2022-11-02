import pdb
import time
import datetime
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from dateutil.relativedelta import relativedelta


class OdooCMSProcessFeePayment(models.TransientModel):
    _name = 'odoocms.process.fee.payment'
    _description = 'Process Fee Payment'

    tag = fields.Char('Batch-ID/Tag', help='Batch Number etc...',
        default=lambda self: self.env['ir.sequence'].next_by_code('odoocms.fee.payment'), copy=False,
        readonly=True)

    @api.model
    def _get_payments(self):
        if self.env.context.get('active_model', False)=='odoocms.fee.payment' and self.env.context.get('active_ids', False):
            return self.env.context['active_ids']

    payment_ids = fields.Many2many('odoocms.fee.payment', string='Students',
        help="""Only selected Payments will be Processed.""", default=_get_payments)

    def process_payment(self):
        for payment in self.payment_ids:
            invoice = self.env['account.move'].search([('barcode', '=', payment.receipt_number), ('state', '!=', 'draft')])
            if invoice:  # and invoice.amount_total <= payment.amount:

                invoice_ids = [(4, invoice.id, None)]
                invoice_ids2 = invoice

                # config_academic_semester = self.env['ir.config_parameter'].get_param('odoocms.current_academic_semester')
                # if config_academic_semester:
                # 	new_semester = self.env['odoocms.academic.semester'].browse(int(config_academic_semester))
                # else:
                # 	new_semester = invoice.student_id.academic_semester_id

                new_semester = invoice.academic_semester_id
                due_date = invoice.date_due
                planning_line = False
                if new_semester.planning_ids:
                    planning_line = new_semester.planning_ids.filtered(
                        lambda l: l.type=='duesdate' and len(l.campus_ids)==0 and len(l.department_ids)==0 and len(l.semester_ids)==0)

                    if not planning_line:
                        planning_line = new_semester.planning_ids.filtered(lambda l: l.type=='duesdate' and invoice.student_id.campus_id in (l.campus_ids) and len(
                            l.department_ids)==0 and len(l.semester_ids)==0)
                        if not planning_line:
                            planning_line = new_semester.planning_ids.filtered(lambda l: l.type=='duesdate' and len(l.campus_ids)==0 and invoice.student_id.batch_id.department_id in (l.department_ids) and len(
                                l.semester_ids)==0)
                            if not planning_line:
                                planning_line = new_semester.planning_ids.filtered(lambda l: l.type=='duesdate' and len(l.campus_ids)==0 and len(
                                    l.department_ids)==0 and invoice.student_id.semester_id in (l.semester_ids))
                                if not planning_line:
                                    planning_line = new_semester.planning_ids.filtered(lambda l: l.type=='duesdate' and len(
                                        l.campus_ids)==0 and invoice.student_id.batch_id.department_id in (l.department_ids) and invoice.student_id.semester_id in (l.semester_ids))
                                    if not planning_line:
                                        planning_line = new_semester.planning_ids.filtered(
                                            lambda l: l.type=='duesdate' and invoice.student_id.campus_id in (
                                                l.campus_ids) and len(
                                                l.department_ids)==0 and invoice.student_id.semester_id in (l.semester_ids))
                                        if not planning_line:
                                            planning_line = new_semester.planning_ids.filtered(
                                                lambda l: l.type=='duesdate' and invoice.student_id.campus_id in (
                                                    l.campus_ids) and invoice.student_id.batch_id.department_id in (
                                                              l.department_ids) and invoice.student_id.semester_id in (
                                                              l.semester_ids))
                                            if not planning_line:
                                                planning_line = new_semester.planning_ids.filtered(lambda l: l.type=='duesdate' and invoice.student_id.campus_id in (l.campus_ids) and invoice.student_id.batch_id.department_id in (l.department_ids) and len(l.semester_ids)==0)

                if planning_line and planning_line.date_end > due_date:
                    due_date = fields.Date.from_string(planning_line.date_end)

                date_invoice = payment.date
                payment_date = fields.Date.from_string(payment.date)

                invoice.payment_date = payment.date

                days = (payment_date - due_date).days

                analytic_tags = self.env['account.analytic.tag']
                analytic_tags += invoice.student_id.program_id.department_id.campus_id.analytic_tag_id
                # analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in analytic_tags]
                analytic_tag_ids = [(6, 0, analytic_tags.ids)]

                # if "Late Fine" in invoice.receipt_type_ids.mapped('name') and len(invoice.invoice_line_ids) == 1 and not invoice.invoice_line_ids.fee_head_id.late_fine:
                # 	days = 0

                lines = []
                if days > 0:
                    latefee = 0
                    # late_fee_max_fine
                    if invoice.student_id.batch_id and invoice.student_id.batch_id.late_fee_max_fine:
                        late_fee_max_fine = invoice.student_id.batch_id.late_fee_max_fine
                    elif invoice.student_id.campus_id and invoice.student_id.campus_id.late_fee_max_fine:
                        late_fee_max_fine = invoice.student_id.campus_id.late_fee_max_fine
                    else:
                        late_fee_max_fine = self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.late_fee_max_fine') or 10000
                        late_fee_max_fine = eval(late_fee_max_fine)

                    late_fee_per_day_fine = None
                    if invoice.student_id.batch_id and invoice.student_id.batch_id.late_fee_per_day_fine:
                        late_fee_per_day_fine = invoice.student_id.batch_id.late_fee_per_day_fine
                    elif invoice.student_id.campus_id and invoice.student_id.campus_id.late_fee_per_day_fine:
                        late_fee_per_day_fine = invoice.student_id.campus_id.late_fee_per_day_fine
                    else:
                        late_fee_per_day_fine = self.env['ir.config_parameter'].sudo().get_param('odoocms_fee.late_fee_per_day_fine')
                    if not late_fee_per_day_fine:
                        late_fee_per_day_fine = '100'

                    if late_fee_per_day_fine.find('%') > 0:
                        late_fee_unit = eval(late_fee_per_day_fine[0: len(late_fee_per_day_fine) - 1])
                        invoice_lines = invoice.invoice_line_ids.filtered(lambda l: l.fee_head_id.late_fine==True)
                        fine_sum = 0
                        if invoice_lines:
                            fine_sum = sum(line.price_subtotal for line in invoice_lines)
                        late_fee_unit = late_fee_unit * fine_sum / 100.0

                    else:
                        if invoice.invoice_line_ids.filtered(lambda l: l.fee_head_id.late_fine==True):
                            late_fee_unit = eval(late_fee_per_day_fine)
                        else:
                            late_fee_unit = 0

                    latefee = late_fee_unit * days

                    # if invoice.student_id.waiver_ids:
                    # 	waiver_fee_line = invoice.student_id.waiver_ids.mapped('line_ids').filtered(lambda l: l.fee_head_id.name == 'Late Fine')
                    # 	if waiver_fee_line:
                    # 		waiver_fine = latefee * waiver_fee_line.percentage / 100.0
                    # 		latefee = latefee - waiver_fine

                    if invoice.student_id.waiver_ids:
                        waiver_id = invoice.student_id.waiver_ids.filtered(lambda l: l.waiver_type=='latefine')
                        if waiver_id and waiver_id.line_ids:
                            waiver_sum = 0
                            waiver_line_ids = waiver_id.line_ids.filtered(lambda l: l.fee_head_id.waiver==True)
                            if waiver_line_ids:
                                waiver_sum = latefee * waiver_line_ids[0].percentage / 100.0
                            waiver_fine = waiver_sum
                            latefee = latefee - waiver_fine

                    cross_max = False
                    if latefee > late_fee_max_fine:
                        latefee = late_fee_max_fine
                        cross_max = True
                    if latefee > 0:
                        latefee_receipt_type = self.env['ir.config_parameter'].sudo().get_param('odoocms_registration.latefee_receipt_type')
                        if not latefee_receipt_type:
                            raise UserError('Please configure the LateFee Receipt Type in Global Settings')
                        else:
                            latefee_receipt_type_id = self.env['odoocms.receipt.type'].browse([eval(latefee_receipt_type)])

                        price_unit = latefee / (1 if cross_max else days)
                        if late_fee_per_day_fine.find('%') > 0:
                            price_unit = round(price_unit, 0)

                        latefee_line = {
                            'price_unit': price_unit,
                            'quantity': 1 if cross_max else days,
                            # 'product_id': line.invoice_line.product_id.id,
                            'name': 'Late Payment',
                            'account_id': latefee_receipt_type_id.fee_head_ids[0].property_account_income_id.id,  # Have to change 232
                            'analytic_tag_ids': analytic_tag_ids,
                        }
                        lines.append([0, 0, latefee_line])

                        sequence = invoice.fee_structure_id.journal_id.sequence_id
                        new_name = sequence.with_context(ir_sequence_date=date_invoice).next_by_id()

                        # Create Late Fee Invoice
                        data = {
                            'student_id': invoice.student_id.id,
                            'partner_id': invoice.student_id.partner_id.id,
                            'fee_structure_id': invoice.fee_structure_id.id,
                            'program_id': invoice.student_id.program_id.id,
                            'academic_semester_id': invoice.academic_semester_id and invoice.academic_semester_id.id or False,
                            'is_fee': True,
                            'is_cms': True,
                            'is_late_fee': True,
                            'student_name': invoice.student_id.partner_id.name,
                            'invoice_line_ids': lines,
                            'journal_id': invoice.fee_structure_id.journal_id.id,
                            'number': new_name,
                            'date_invoice': date_invoice,
                            'date_due': date_invoice + relativedelta(days=7),
                            'state': 'draft',
                            'receipt_type_ids': [(4, receipt.id, None) for receipt in latefee_receipt_type_id],
                        }
                        latefee_invoice = self.env['account.move'].create(data)
                        ledger_data = {
                            'student_id': invoice.student_id.id,
                            'date': date_invoice,
                            'credit': latefee_invoice.amount_total,
                            'invoice_id': latefee_invoice.id,
                        }
                        ledger_id = self.env['odoocms.student.ledger'].create(ledger_data)
                        latefee_invoice.student_ledger_id = ledger_id.id

                        latefee_invoice.super_invoice = invoice.id
                        invoice.sub_invoice = latefee_invoice.id

                        if (latefee + invoice.amount_total) <= payment.amount:
                            latefee_invoice.action_invoice_send()
                            invoice_ids += [(4, latefee_invoice.id, None)]
                            invoice_ids2 += latefee_invoice

                        # if payment.amount > latefee + invoice.amount_total:
                        # 	debit_amount = payment.amount - latefee + invoice.amount_total
                        # 	data = {
                        # 		'student_id': invoice.student_id.id,
                        # 		'invoice_id': invoice.id,
                        # 		'invoice_id': invoice.id,
                        # 		'date': payment.date,
                        # 		'amount': debit_amount,
                        # 	}
                        # 	student_ledger.create(data)

                data = {
                    'payment_type': 'inbound',
                    'payment_method_id': '1',
                    'partner_type': 'customer',
                    'currency_id': invoice.journal_id.currency_id.id,
                    'partner_id': invoice.student_id and invoice.student_id.partner_id.id or invoice.applicant_id and invoice.applicant_id.partner_id.id,
                    'payment_date': payment.date,
                    'communication': payment.receipt_number,
                    'amount': payment.amount,
                    'journal_id': payment.journal_id.id,
                    'invoice_ids': invoice_ids,
                    'analytic_tag_ids': analytic_tag_ids,
                }

                for invoice_rec in invoice_ids2:
                    if invoice_rec.state=='unpaid':
                        invoice_rec.state = 'draft'
                        invoice_rec.action_invoice_open()

                pay_rec = self.env['account.payment'].create(data)
                pay_rec.post()
                payment.name = pay_rec.name

                ledger_data = {
                    'student_id': invoice.student_id.id,
                    'date': date_invoice,
                    'debit': payment.amount,
                    'invoice_id': invoice.id,
                    'payment_id': payment.id,
                }
                ledger_id = self.env['odoocms.student.ledger'].create(ledger_data)
                payment.student_ledger_id = ledger_id.id

                # pay_rec.action_validate_invoice_payment()
                payment.state = 'done'
                payment.tag = self.tag
                ###########################For Refund Details in Student Profile....................########


                search_credit = self.env['odoocms.student.ledger'].search([('invoice_id', '=', invoice.id), ('credit', '!=', 0)])
                credit_amount = search_credit.credit
                debit_amount = ledger_id.debit
                extra_amount = debit_amount - credit_amount
                search_late = self.env['account.move'].search(
                    [('super_invoice', '=', invoice.id)])
                refund_amount = 0
                if search_late:
                    late_amount = search_late.amount_total
                    refund_amount = extra_amount - late_amount
                else:
                    refund_amount = extra_amount
                if refund_amount > 0:
                    refund_data = {
                        'student_id': invoice.student_id.id,
                        'refund_amount': refund_amount,
                        'invoice_id': invoice.id,
                        'description': 'Outstanding Amount',
                    }
                    # refund_id = self.env['odoocms.student.refund.details'].create(refund_data)

                ############## For Security Refund details on Student profile ..........###############
                security_heads = invoice.invoice_line_ids.filtered(
                    lambda l: l.fee_head_id.security_refund==True)
                for rec in security_heads:
                    refund_data = {
                        'student_id': invoice.student_id.id,
                        'refund_amount': rec.price_subtotal,
                        'invoice_id': invoice.id,
                        'description': 'Security Amount',
                    }
                    # self.env['odoocms.student.refund.details'].create(refund_data)


        # else:
        # 	payment.state = 'error'

        return {'type': 'ir.actions.act_window_close'}
