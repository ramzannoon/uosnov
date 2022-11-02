import pdb
import calendar
from datetime import datetime, date
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
from odoo import http


class OdooCMSStudentSuspensionRequest(models.Model):
    _name = "odoocms.student.suspension.request"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Student Suspension Request"
    _rec_name = 'student_id'

    READONLY_STATES = {
        'submit': [('readonly', True)],
        'approve': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    @api.model
    def _get_default_ad_hoc_type(self):
        rec = self.env['odoocms.fee.additional.charges.type'].search([('name', '=', 'Suspension')], order='id desc', limit=1)
        if rec:
            return rec.id
        else:
            return False

    student_id = fields.Many2one('odoocms.student', string="Student", states=READONLY_STATES)
    program_id = fields.Many2one('odoocms.program', string='Academic Program', related='student_id.program_id', store=True)
    batch_id = fields.Many2one('odoocms.batch', string='Batch', related='student_id.batch_id', store=True)
    section_id = fields.Many2one('odoocms.batch.section', string='Class Section', related='student_id.section_id', store=True)
    semester_id = fields.Many2one('odoocms.semester', string='Current Semester', related='student_id.semester_id', store=True)
    career_id = fields.Many2one('odoocms.career', string='Academic Level', related='student_id.career_id', store=True)
    current_term_id = fields.Many2one('odoocms.academic.term', string='Current Term', related='student_id.term_id', store=True)
    term_seq = fields.Integer(related='current_term_id.number', store=True)

    term_id = fields.Many2one('odoocms.academic.term', string='Term to Suspend', states=READONLY_STATES)
    reason = fields.Text(string='Reason', states=READONLY_STATES)
    state = fields.Selection([('draft', 'Draft'),
                              ('submit', 'Submitted'),
                              ('approve', 'Approved'),
                              ('done', 'Done'),
                              ('cancel', 'Canceled')
                              ], default='draft', string="Status", track_visibility='onchange')

    amount = fields.Float('Amount')
    ad_hoc_type_id = fields.Many2one('odoocms.fee.additional.charges.type', 'Charge Type', default=_get_default_ad_hoc_type)
    ad_hoc_charges_id = fields.Many2one('odoocms.fee.additional.charges', 'Ad Hoc Ref.')

    def action_submit(self):
        for rec in self:
            exist_recs = self.env['odoocms.student.suspension.request'].search([('student_id', '=', rec.student_id.id),
                                                                                ('state', 'in', ('submit', 'approve', 'done')),
                                                                                ('term_id', '=', rec.term_id.id)])
            if len(exist_recs) >= 2:
                raise UserError('Two Suspension records already exist')
            rec.state = 'submit'

    def action_approve(self):
        for rec in self:
            rec.state = 'approve'

    def action_done(self):
        for rec in self:
            suspension_tag = self.env['odoocms.student.tag'].search([('name', '=', 'Suspension')])
            if not suspension_tag:
                raise UserError(_('Suspension Tag from Student Tags did not find. Please Ask Admin to define Tag.'))
            tags = rec.student_id.tag_ids + suspension_tag
            rec.student_id.write({
                'tag_ids': [[6, 0, tags.ids]]
            })
            if rec.ad_hoc_type_id:
                values = {
                    'student_id': rec.student_id.id,
                    'student_code': rec.student_id.code,
                    'charges_type': rec.ad_hoc_type_id.id,
                    'program_id': rec.student_id.program_id and rec.student_id.program_id.id or False,
                    'batch_id': rec.student_id.batch_id and rec.student_id.batch_id.id or False,
                    'career_id': rec.student_id.career_id and rec.student_id.career_id.id or False,
                    'term_id': rec.student_id.term_id and rec.student_id.term_id.id or False,
                    'institute_id': rec.student_id.institute_id and rec.student_id.institute_id.id or False,
                    'discipline_id': rec.student_id.discipline_id and rec.student_id.discipline_id.id or False,
                    'campus_id': rec.student_id.campus_id and rec.student_id.campus_id.id or False,
                    'amount': rec.amount,
                    'date': fields.Date.today(),
                }
                rec.ad_hoc_charges_id = self.env['odoocms.fee.additional.charges'].create(values)
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
