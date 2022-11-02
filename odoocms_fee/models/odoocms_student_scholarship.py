import time
import datetime
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, UserError
import pdb
import logging

_logger = logging.getLogger(__name__)


class OdooCMSStudentScholarshipRequest(models.Model):
    _name = 'odoocms.student.scholarship.request'
    _inherit = ['odoocms.student.fee.public']
    _description = "Student ScholarShip Requests"

    name = fields.Char(string='Name')
    sequence = fields.Integer('Sequence')
    student_id = fields.Many2one('odoocms.student', string='Student', tracking=True, index=True)
    state = fields.Selection([('draft', 'Request'),
                              ('approve', 'Approved'),
                              ('reject', 'Rejected')
                              ], string='Status', default='draft', indedx=True)
    waiver_ids = fields.Many2many('odoocms.fee.waiver', 'student_scholarship_waiver_rel', 'scholarship_req_id', 'waiver_id', 'Scholarship')
    request_date = fields.Date('Request Date', default=fields.Date.today())
    approved_date = fields.Date('Approved Date')
    reject_date = fields.Date('Rejected Date')
    remarks = fields.Text('Remarks')

    _sql_constraints = [('unique_student_session', 'unique(student_id,session_id)', "Duplicates are not allowed!")]

    @api.model
    def create(self, values):
        if not values.get('sequence', False):
            values['name'] = self.env['ir.sequence'].next_by_code('odoocms.student.scholarship.request')
        result = super(OdooCMSStudentScholarshipRequest, self).create(values)
        return result

    def unlink(self):
        for rec in self:
            if not rec.state=='draft':
                raise UserError('You can Delete records in Draft State only.')
        return super(OdooCMSStudentScholarshipRequest, self).unlink()

    def action_approved(self):
        for rec in self:
            if not rec.waiver_ids:
                raise UserError(_('Please enter the Scholarships.'))
            student_tags = []
            for waiver in rec.waiver_ids:
                student_tag = self.env['odoocms.student.tag'].search([('code', '=', waiver.tag_id.code)], order='id desc', limit=1)
                if student_tag:
                    student_tags.append(student_tag.id)
                else:
                    raise UserError(_('%s does not exist in the system, please define it first') % waiver.tag_id.code)

                if student_tags:
                    for tag in rec.student_id.tag_ids:
                        student_tags.append(tag.id)
                    rec.student_id.sudo().write({'tag_ids': [[6, 0, student_tags]]})
            rec.state = 'approve'
            rec.approved_date = fields.Date.today()

    def action_rejected(self):
        for rec in self:
            rec.state = 'reject'
            rec.reject_date = fields.Date.today()


class OdooCMSStudentFeeScholarship(models.Model):
    _name = 'odoocms.student.fee.scholarship'
    _description = 'Student Fee Scholarship'

    name = fields.Char('Name')
    student_id = fields.Many2one('odoocms.student', 'Student')
    invoice_id = fields.Many2one('account.move', String='Invoice')
    term_id = fields.Many2one('odoocms.academic.term', 'Academic Term')
    semester_id = fields.Many2one('odoocms.semester', 'Semester')
    waiver_type = fields.Selection([('fixed', 'Fixed'),
                                    ('percentage', 'Percentage')
                                    ], 'Type', default='fixed')
    amount = fields.Float('Amount')
    amount_percentage = fields.Char('Value')
    waiver_line_id = fields.Many2one('odoocms.fee.waiver.line', 'Waiver Line')
    donor_id = fields.Many2one('odoocms.fee.donors', 'Donor')
