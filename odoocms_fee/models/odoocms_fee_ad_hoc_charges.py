from odoo import models, fields, api,_
from odoo.exceptions import ValidationError, UserError


class OdooCMSFeeAdditionalChargesType(models.Model):
    _name = 'odoocms.fee.additional.charges.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Ad-hoc Charges Types"

    name = fields.Char("Name")
    code = fields.Char("Code")
    fee_head_id = fields.Many2one('odoocms.fee.head', 'Fee Head')
    state = fields.Selection([('draft', 'Draft'), ('lock', 'Locked')], string='Status', default='draft', tracking=True)

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'


class OdooCMSFeeAdditionalCharges(models.Model):
    _name = 'odoocms.fee.additional.charges'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Ad-hoc Charges"

    name = fields.Char('Name')
    sequence = fields.Char('Sequence')
    student_id = fields.Many2one('odoocms.student', 'Student', required=True, tracking=True)
    student_code = fields.Char('Student Code', tracking=True)
    program_id = fields.Many2one('odoocms.program', 'Program')
    batch_id = fields.Many2one('odoocms.batch')
    session_id = fields.Many2one('odoocms.academic.session', 'Academic Session')
    career_id = fields.Many2one('odoocms.career', 'Academic Level')
    term_id = fields.Many2one('odoocms.academic.term', 'Charge On Term')
    semester_id = fields.Many2one('odoocms.semester', 'Semester')
    institute_id = fields.Many2one('odoocms.institute', 'School')
    discipline_id = fields.Many2one('odoocms.discipline', 'Discipline')
    campus_id = fields.Many2one('odoocms.campus', 'Campus')

    charges_type = fields.Many2one('odoocms.fee.additional.charges.type', 'Charges Type', required=True, tracking=True)
    amount = fields.Float('Amount', required=True, tracking=True)
    date = fields.Date('Date', required=True, default=lambda self: fields.Date.today(), tracking=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('charged', 'Charged'),
                              ('cancel', 'Cancelled')], string='Status', tracking=True, default='draft')
    receipt_id = fields.Many2one('account.move', 'Receipt Ref.', tracking=True)
    notes = fields.Text('Notes', tracking=True)
    to_be = fields.Boolean('To Be', default=False)

    @api.constrains('amount')
    def validate_amount(self):
        for rec in self:
            if rec.amount < 0:
                raise ValidationError('Negative Value for the Amount is not Allowed')
            if rec.amount == 0:
                raise ValidationError('Amount Should be Greater then the Zero.')

    @api.model
    def create(self, values):
        if not values.get('sequence', False):
            values['name'] = self.env['ir.sequence'].next_by_code('odoocms.fee.additional.charges')
        result = super(OdooCMSFeeAdditionalCharges, self).create(values)
        return result

    def unlink(self):
        for rec in self:
            if self.receipt_id:
                raise UserError('You Cannot Delete this record, As this Record is already Include in the Invoice. Please contact the System Administrator.')
        return super(OdooCMSFeeAdditionalCharges, self).unlink()

    def action_cancel(self):
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'cancel'

    def action_reset_to_draft(self):
        for rec in self:
            if rec.state == 'cancel':
                rec.state = 'draft'

    @api.onchange('student_id')
    def onchange_student_id(self):
        for rec in self:
            if rec.student_id:
                rec.student_code = rec.student_id.id_number and rec.student_id.id_number or ''
                rec.session_id = rec.student_id.session_id and rec.student_id.session_id.id or False
                rec.career_id = rec.student_id.career_id and rec.student_id.career_id.id or False
                rec.program_id = rec.student_id.program_id and rec.student_id.program_id.id or False
                rec.batch_id = rec.student_id.batch_id and rec.student_id.batch_id.id or False
                rec.semester_id = rec.student_id.semester_id and rec.student_id.semester_id.id or False
                rec.discipline_id = rec.student_id.discipline_id and rec.student_id.discipline_id.id or False
                rec.institute_id = rec.student_id.institute_id and rec.student_id.institute_id.id or False
                rec.campus_id = rec.student_id.campus_id and rec.student_id.campus_id.id or False

    @api.model
    def create(self, values):
        res = super(OdooCMSFeeAdditionalCharges, self).create(values)
        if not res.sequence:
            res.name = self.env['ir.sequence'].next_by_code('odoocms.fee.ad.hoc.charges')
        return res

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Ad hoc Fee Charges'),
            'template': '/odoocms_fee/static/xls/ad_hoc_charges.xlsx'
        }]

