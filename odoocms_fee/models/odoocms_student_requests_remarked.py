from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from dateutil.relativedelta import relativedelta
from odoo.tools.safe_eval import safe_eval
import pdb
from datetime import date


class OdooCMSRequestStubjectDrop(models.Model):
    _name = "odoocms.request.subject.drop"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Student Subject Drop"

    program_id = fields.Many2one('odoocms.program', string='Academic Program')
    academic_semester_id = fields.Many2one('odoocms.academic.semester', string='Academic Term')
    class_id = fields.Many2one('odoocms.class', string='Course')
    # invoice_id = fields.Many2one(related='subject_reg_id.invoice_id', string="Invoice", readonly=True)

    description = fields.Text(string='Description')
    date_request = fields.Date('Request Date', default=date.today(), readonly=True)
    approve_date = fields.Date('Approved Date', readonly=True)
    reason_id = fields.Many2one('odoocms.drop.reason', string='Reason', required=True)

    subject_reg_ids = fields.Many2one('odoocms.subject.registration', string="Student Registrations", compute='get_registrations()')

    # source = fields.Selection([('admin','Admin'),('portal','portal')],default='admin',string="Source", readonly=True)
    drop_with = fields.Selection([('admin', 'Administrative'), ('medical', 'Medical'), ('request', 'Student Request')], default='request', string="Drop With", track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('submit', 'Submit'), ('approve', 'Approved'), ('cancel', 'Cancel'), ('done', 'Done')], default='draft', string="Status", track_visibility='onchange')

    @api.depends('academic_semester_id', 'class_id')
    def get_registrations(self):
        if self.class_id and self.academic_semester_id:
            registrations = self.env['odoocms.student.course'].search([('tag', '=', self.tag), ('tag', '=', self.tag)])
            if registrations:
                self.registration_ids = [(6, 0, registrations.ids)]

    def action_submit(self):
        for rec in self:
            if not rec.batch_id.department_id.chairman_id:
                raise UserError('Please Assign Head/Chariman to %s!' % rec.batch_id.department_id.name)
            if not rec.batch_id.department_id.chairman_id.user_id:
                raise UserError('Please Create the Login User for %s!' % rec.batch_id.department_id.chairman_id.name)

            if rec.drop_with=='request':
                config_academic_semester = self.env['ir.config_parameter'].sudo().get_param('odoocms.current_academic_semester')
                if config_academic_semester:
                    new_semester = self.env['odoocms.academic.semester'].sudo().browse(int(config_academic_semester))
                else:
                    new_semester = rec.student_id.academic_semester_id

                planning_line = rec.academic_semester_id.get_planning(rec.student_id, 'drop')
                if not planning_line:
                    raise UserError('No schedule found for Drop Course for Term %s' % new_semester.name)

                if planning_line.date_end < rec.date_request:
                    raise UserError('You are not allowed to do this action. Date is over.')

            if rec.invoice_id and rec.invoice_id.state=='paid':
                invoice_lines = rec.invoice_id.line_ids.filtered(lambda l: l.fee_head_id.refund==True)
                total = 0
                if invoice_lines:
                    total = sum(line.price_subtotal for line in invoice_lines)
                ledger_data = {
                    'student_id': rec.student_id.id,
                    'date': rec.invoice_id.date_invoice,
                    'debit': total,
                    'invoice_id': rec.invoice_id.id,
                }
                if total > 0:
                    ledger_id = rec.env['odoocms.student.ledger'].create(ledger_data)
                    rec.invoice.student_ledger_id = ledger_id.id

            rec.activity_schedule('odoocms_fee.mail_act_subject_drop', user_id=rec.batch_id.department_id.chairman_id.user_id.id)
            rec.state = 'submit'

    def action_approve(self):
        for rec in self:
            if rec.state=='submit':
                rec.state = 'approve'
                rec.approve_date = date.today()
            else:
                raise UserError('Request is not confirmed yet. Please Submit the request first!')

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'


class OdooCMSRequestStubjectChange(models.Model):
    _name = "odoocms.request.subject.change"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Student Subject Change "

    program_id = fields.Many2one('odoocms.program', string='Academic Program')
    student_id = fields.Many2one('odoocms.student', string='Student')
    academic_semester_id = fields.Many2one('odoocms.academic.semester', string='Academic Term')
    subject_reg_id = fields.Many2one('odoocms.student.course', string="Subject", track_visibility='onchange', required=True)
    subject_id = fields.Many2one('odoocms.class', domain="[('academic_semester_id','=', academic_semester_id),('batch_id','=',batch_id),('state','in', ('draft','current'))]", string="New Subject", track_visibility='onchange', required=True)
    description = fields.Text(string='Description')
    date_request = fields.Date('Request Date', default=date.today(), readonly=True)
    approve_date = fields.Date('Approved Date', readonly=True)
    reason_id = fields.Many2one('odoocms.drop.reason', string='Reason', required=True)
    batch_id = fields.Many2one(related='student_id.batch_id', string="Batch Program", readonly=True)

    # source = fields.Selection([('admin','Admin'),('portal','portal')],default='admin',string="Source", readonly=True)
    drop_with = fields.Selection([('admin', 'Administrative'), ('medical', 'Medical'), ('request', 'Student Request')], default='request', string="Change With", track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('submit', 'Submit'), ('approve', 'Approved'), ('cancel', 'Cancel'), ('done', 'Done')], default='draft', string="Status", track_visibility='onchange')

    def action_submit(self):
        for rec in self:
            if not rec.batch_id.department_id.chairman_id:
                raise UserError('Please Assign Head/Chariman to %s!' % rec.batch_id.department_id.name)
            if not rec.batch_id.department_id.chairman_id.user_id:
                raise UserError('Please Create the Login User for %s!' % rec.batch_id.department_id.chairman_id.name)
            rec.activity_schedule('odoocms_fee.mail_act_subject_change', user_id=rec.batch_id.department_id.chairman_id.user_id.id)
            rec.state = 'submit'

    def action_approve(self):
        for rec in self:
            rec.subject_reg_id.class_id = rec.subject_id
            if rec.state=='submit':
                rec.state = 'approve'
                rec.approve_date = date.today()
            else:
                raise UserError('Request is not confirmed yet. Please Submit the request first!')

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'


class OdooCMSRequestAdmissionCancelation(models.Model):
    _name = "odoocms.request.admission.cancel"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Cancel Admission"
    _rec_name = 'student_id'

    program_id = fields.Many2one('odoocms.program', string='Academic Program')
    batch_id = fields.Many2one('odoocms.batch', string='Program Batch')
    student_id = fields.Many2one('odoocms.student', string='Student')
    invoice_ids = fields.Many2many('account.move', string="Invoices")

    description = fields.Text(string='Description')
    date_request = fields.Date('Request Date', default=date.today(), readonly=True)
    approve_date = fields.Date('Approved Date', readonly=True)
    reason_id = fields.Many2one('odoocms.drop.reason', string='Reason', required=True)

    source = fields.Selection([('admin', 'Admin'), ('portal', 'portal')], default='admin', string="Source", readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('submit', 'Submit'), ('approve', 'Approved'), ('cancel', 'Cancel'), ('done', 'Done')], default='draft', string="Status", track_visibility='onchange')

    def action_submit(self):
        for rec in self:
            if not rec.batch_id.department_id.chairman_id:
                raise UserError('Please Assign Head/Chariman to %s!' % (rec.batch_id.department_id.name))
            if not rec.batch_id.department_id.chairman_id.user_id:
                raise UserError('Please Create the Login User for %s!' % (rec.batch_id.department_id.chairman_id.name))

            config_academic_semester = self.env['ir.config_parameter'].sudo().get_param('odoocms.current_academic_semester')
            if config_academic_semester:
                new_semester = self.env['odoocms.academic.semester'].sudo().browse(int(config_academic_semester))
            else:
                new_semester = rec.student_id.academic_semester_id

            planning_lines = False
            if new_semester.planning_ids:
                planning_lines = new_semester.planning_ids.filtered(
                    lambda l: l.type=='cancellation' and rec.student_id.batch_id.department_id in (l.department_ids))
                if not planning_lines:
                    planning_line = new_semester.planning_ids.filtered(lambda l: l.type=='cancellation' and len(l.department_ids)==0)

            if not planning_lines:
                raise UserError('No schedule found for Admission Cancellation for Term %s' % (new_semester.name))

            if planning_lines and rec.invoice_id and rec.invoice_id.state=='paid':
                invoice_lines = rec.invoice_id.line_line_ids.filtered(lambda l: l.fee_head_id.refund==True)
                total = 0
                if invoice_lines:
                    total = sum(line.price_subtotal for line in invoice_lines)

                ledger_data = {
                    'student_id': rec.student_id.id,
                    'date': rec.invoice_id.date_invoice,
                    'debit': total,
                    'invoice_id': rec.invoice_id.id,
                }
                if total > 0:
                    ledger_id = rec.env['odoocms.student.ledger'].create(ledger_data)
                    rec.invoice.student_ledger_id = ledger_id.id

            rec.activity_schedule('odoocms_fee.mail_act_admission_cancel', user_id=rec.batch_id.department_id.chairman_id.user_id.id)
            rec.state = 'submit'

    def action_approve(self):
        for rec in self:
            if rec.state=='submit':
                rec.state = 'approve'
                rec.approve_date = date.today()
            else:
                raise UserError('Request is not confirmed yet. Please Submit the request first!')

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
