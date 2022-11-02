from odoo import fields, models, api, _
from datetime import datetime, date


class OdooCMSFreeze(models.Model):
    _name = "odoocms.freeze.course"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Freeze Course"

    READONLY_STATES = {
        'submit': [('readonly', True)],
        'approve': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    student_id = fields.Many2one('odoocms.student', string="Student", tracking=True, states=READONLY_STATES)
    program_id = fields.Many2one(related='student_id.program_id', string='Academic Program', states=READONLY_STATES)
    batch_id = fields.Many2one(related='student_id.batch_id', string='Class Batch', states=READONLY_STATES)
    section_id = fields.Many2one(related='student_id.section_id', string='Class Section', states=READONLY_STATES)
    term_id = fields.Many2one(related='batch_id.term_id', string='Academic Term', states=READONLY_STATES)
    semester_id = fields.Many2one(related='student_id.semester_id', string='Current Semester', states=READONLY_STATES)

    registration_id = fields.Many2one('odoocms.student.course', string='Freeze Semester', tracking=True,
                                      states=READONLY_STATES)
    description = fields.Text(string='Description', states=READONLY_STATES)
    reason_id = fields.Many2one('odoocms.drop.reason', string='Reason', states=READONLY_STATES)
    date_request = fields.Date('Request Date', default=date.today(), readonly=True)
    date_effective = fields.Date('Effective Date', default=date.today())
    date_approve = fields.Date(string='Approve Date', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('approve', 'Approved'),
        ('cancel', 'Cancel')], default='draft', string="Status", tracking=True)

    override_min_limit = fields.Boolean('Override Minimum Limit?', default=False, states=READONLY_STATES, tracking=True)
    limit_error = fields.Boolean('Over Limit', default=False)
    limit_error_text = fields.Text(default='')
