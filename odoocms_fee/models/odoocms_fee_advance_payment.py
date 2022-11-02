from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import pdb


class OdooCMSFeeDonors(models.Model):
    _name = 'odoocms.fee.donors'
    _inherits = {'res.partner': 'partner_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Fee Donors"
    _order = 'id'

    @api.depends('first_name', 'last_name')
    def _get_donor_name(self):
        for donor in self:
            donor.name = (donor.first_name or '') + ' ' + (donor.last_name or '')

    first_name = fields.Char('First Name', required=True, tracking=True)
    last_name = fields.Char('Last Name', tracking=True)
    sequence = fields.Integer('Sequence')
    partner_id = fields.Many2one('res.partner', 'Partner', required=True, ondelete='cascade')
    date = fields.Date('Date', default=fields.Date.today())
    state = fields.Selection([('draft', 'Draft'),
                              ('lock', 'Locked')
                              ], string='Status', default='draft', tracking=True)
    invoice_ids = fields.One2many('account.move', 'donor_id', 'Invoices')
    invoice_count = fields.Integer(string="Invoice Count", compute="_compute_invoices_count", groups="base.group_user")

    payment_ids = fields.One2many('account.payment', 'donor_id', 'Payments')
    payment_count = fields.Integer(string="Payment Count", compute="_compute_payment_count", groups="base.group_user")

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'

    @api.constrains('name')
    def donor_name_constrains(self):
        for rec in self:
            if rec.name:
                name_already_exist = self.env['odoocms.fee.donors'].search([('name', '=', rec.name), ('id', '!=', rec.id)])
                if name_already_exist:
                    raise UserError(_('Duplicate Name are not Allowed.'))

    def name_get(self):
        res = []
        for record in self:
            name = record.name
            res.append((record.id, name))
        return res

    @api.model
    def create(self, vals):
        if vals.get('first_name', False) or vals.get('last_name', False):
            first_name = vals.get('first_name', '')
            if first_name:
                first_name = first_name.title()  # capitalize
                vals['first_name'] = first_name
            name = first_name

            last_name = vals.get('last_name', '')
            if last_name:
                last_name = last_name.title()  # capitalize
                vals['last_name'] = last_name
                name = name + ' ' + last_name
            vals['name'] = name

        donor = super().create(vals)
        return donor

    def write(self, vals):
        if vals.get('first_name', False) or vals.get('last_name', False):
            first_name = vals.get('first_name', self.first_name)
            if first_name:
                first_name = first_name.title()
                vals['first_name'] = first_name
            name = first_name

            last_name = vals.get('last_name', self.last_name)
            if last_name:
                last_name = last_name.title()
                vals['last_name'] = last_name
                name = name + ' ' + last_name
            vals['name'] = name
        res = super().write(vals)
        return res

    def _compute_invoices_count(self):
        for rec in self:
            rec.invoice_count = len(rec.invoice_ids)

    def _compute_payment_count(self):
        for rec in self:
            rec.payment_count = len(rec.payment_ids)


class OdooCMSFeeAdvancePayment(models.Model):
    _name = 'odoocms.fee.advance.payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Fee Advance Payment"

    name = fields.Char('Name')
    sequence = fields.Char('Sequence')
    donor_id = fields.Many2one('odoocms.fee.donors', 'Donor', required=True, tracking=True)
    amount = fields.Float('Amount', required=True, tracking=True)
    date = fields.Date('Date', required=True, default=lambda self: fields.Date.today(), tracking=True)
    student_ids = fields.Many2many('odoocms.student', 'student_advance_fee_payment_rel', 'advance_payment_id', 'student_id', 'Students')

    total_student = fields.Float('Total Student', compute='_total_student', store=True)
    division_type = fields.Selection([('Fixed', 'Fixed'),
                                      ('Equal', 'Equal'),
                                      ('Percentage', 'Percentage')], default='Fixed', string='Division Type')
    amount_value = fields.Float('Value')
    remaining_amount = fields.Float('Remaining Amount', compute='_per_student_amount', store=True)
    per_student_amount = fields.Float('Per Student Amount', compute='_per_student_amount', store=True)

    state = fields.Selection([('draft', 'Draft'),
                              ('done', 'Done'),
                              ('cancel', 'Cancelled')], string='Status', tracking=True, default='draft')

    approve_date = fields.Date('Approve Date', tracking=True)
    journal_id = fields.Many2one('account.journal', 'Account Journal', tracking=True, index=True, default=1)
    notes = fields.Text('Notes', tracking=True)
    to_be = fields.Boolean('To Be', default=False)

    @api.constrains('amount')
    def validate_amount(self):
        for rec in self:
            if rec.amount < 0:
                raise ValidationError('Negative Value for the Amount is not Allowed')
            if rec.amount==0:
                raise ValidationError('Amount Should be Greater then the Zero.')

    @api.model
    def create(self, values):
        if not values.get('sequence', False):
            values['name'] = self.env['ir.sequence'].next_by_code('odoocms.fee.advance.payment')
        result = super(OdooCMSFeeAdvancePayment, self).create(values)
        return result

    def unlink(self):
        for rec in self:
            if not rec.state=='draft':
                raise UserError('You Cannot Delete this record, Please contact the System Administrator.')
        return super(OdooCMSFeeAdvancePayment, self).unlink()

    @api.onchange('division_type')
    def onchange_division_type(self):
        for rec in self:
            rec.amount_value = 0

    @api.depends('student_ids')
    def _total_student(self):
        for rec in self:
            if rec.student_ids:
                rec.total_student = len(rec.student_ids)
            else:
                rec.total_student = 0

    @api.depends('amount', 'student_ids', 'division_type', 'amount_value')
    def _per_student_amount(self):
        for rec in self:
            per_student_amt = 0
            remaining_amount = 0
            if rec.student_ids and rec.amount > 0:
                student_len = len(rec.student_ids)
                if rec.division_type=='Fixed':
                    total_fixed_amt = round(rec.amount_value * student_len, 3)
                    if total_fixed_amt > rec.amount:
                        raise UserError(_('Calculated Amount is greater then the Specified Amount'))
                    per_student_amt = rec.amount_value

                if rec.division_type=='Percentage':

                    per_student_percentage = rec.amount * (rec.amount_value / 100)
                    total_fixed_amt = round(per_student_percentage * student_len, 3)
                    if total_fixed_amt > rec.amount:
                        raise UserError(_('Calculated Amount is greater then the Specified Amount'))
                    per_student_amt = per_student_percentage

                if rec.division_type=='Equal':
                    per_student_amt = round(rec.amount / student_len, 3)
                remaining_amount = rec.amount - (per_student_amt * student_len)
            rec.remaining_amount = remaining_amount
            rec.per_student_amount = per_student_amt

    @api.constrains('division_type')
    def amount_value_constrains(self):
        for rec in self:
            if rec.division_type and rec.amount_value:
                if rec.division_type=='Percentage' and rec.amount_value > 100:
                    raise UserError(_('Percentage Value Should be Less then 100'))

                if rec.division_type=='Fixed' and rec.amount_value > rec.amount:
                    raise UserError(_('Fixed Amount Should be Less then Total Amount'))

                if rec.division_type=='Equal' and rec.amount_value > rec.amount:
                    raise UserError(_('Equal Amount Should be Less then Total Amount'))

    def action_approve(self):
        for rec in self:
            if rec.student_ids:
                rec.approve_date = fields.Date.today()
                for student in rec.student_ids:
                    data = {
                        'payment_type': 'inbound',
                        'payment_method_id': '1',
                        'partner_type': 'customer',
                        'partner_id': student.partner_id and student.partner_id.id or False,
                        'payment_date': rec.date,
                        'communication': 'Student Advance Fee Payment from Donor ' + rec.donor_id.name,
                        'amount': rec.per_student_amount,
                        'journal_id': rec.journal_id.id,
                        # 'account_analytic_id': invoice.student_id.campus_id.account_analytic_id.id,
                        # 'account_analytic_id': False,
                        # 'analytic_tag_ids': [],
                        'donor_id': rec.donor_id and rec.donor_id.id or False,
                    }
                    pay_rec = self.env['account.payment'].create(data)
                    pay_rec.post()
                rec.state = 'done'
            else:
                raise UserError(_('Please Select the Student List.'))

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.onchange('donor_id')
    def onchange_donor_id(self):
        dom = []
        if self.donor_id:
            donor_waivers = self.env['odoocms.fee.waiver'].search([('donor_id', '=', self.donor_id.id)])
            if donor_waivers:
                scholarship_recs = self.env['odoocms.student.scholarship.request'].search([('waiver_ids', 'in', donor_waivers.ids), ('state', '=', 'approve')])
                if scholarship_recs:
                    student_ids = scholarship_recs.mapped('student_id')
                    dom = [('id', 'in', student_ids.ids)]
        return {
            'domain': {
                'student_ids': dom
            },
            'value': {
                'student_ids': False,
            }
        }

