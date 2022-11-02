# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OpLibraryCardType(models.Model):
    _name = "op.library.card.type"
    _description = "Library Card Type"

    name = fields.Char('Name', size=256, required=True)
    allow_media = fields.Integer('No of reference Allowed', size=10,
                                 required=True)
    duration = fields.Integer(
        'Duration', help='Duration in terms of Number of Lead Days',
        required=True)
    penalty_amt_per_day = fields.Float('Penalty Amount per Day',
                                       required=True)

    @api.constrains('allow_media', 'duration', 'penalty_amt_per_day')
    def check_details(self):
        if self.allow_media < 0 or self.duration < 0.0 or \
                self.penalty_amt_per_day < 0.0:
            raise ValidationError(_('Enter proper value'))


class OpLibraryCard(models.Model):
    _name = "op.library.card"
    _rec_name = "number"
    _description = "Library Card"

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    blood_group = fields.Selection(
        [('A+', 'A+ve'), ('B+', 'B+ve'), ('O+', 'O+ve'), ('AB+', 'AB+ve'),
         ('A-', 'A-ve'), ('B-', 'B-ve'), ('O-', 'O-ve'), ('AB-', 'AB-ve'), ('N', 'Not Known')],
        'Blood Group', default='N', tracking=True)
    partner_id = fields.Many2one(
        'res.partner', 'Student/Faculty')
    number = fields.Char('Number', size=256, readonly=True)
    library_card_type_id = fields.Many2one(
        'op.library.card.type', 'Card Type', required=True)
    issue_date = fields.Date(
        'Issue Date', required=True, default=fields.Date.today())
    type = fields.Selection(
        [('student', 'Student'), ('faculty', 'Faculty'), ('employee', 'Other Staff')],
        'Type', default='student', required=True)
    student_id = fields.Many2one('odoocms.student', 'Student',
                                 domain=[('library_card_id', '=', False)])
    faculty_id = fields.Many2one('odoocms.faculty.staff', 'Faculty',
                                 domain=[('library_card_id', '=', False)])
    employee_id = fields.Many2one('hr.employee', 'Employee',
                                 domain=[('faculty_created', '=', False)])
    active = fields.Boolean(default=True)

    _sql_constraints = [(
        'unique_library_card_number',
        'unique(number)',
        'Library card Number should be unique per card!')]

    @api.model
    def create(self, vals):
        if vals['type'] == 'student':
            student_rec = self.env['odoocms.student'].browse(vals['student_id'])
            vals['number'] = student_rec.id_number or student_rec.entryID or ('ST/' + str(student_rec.id))
        if vals['type'] == 'faculty':
            fac_seq = self.env['ir.sequence'].next_by_code('op.library.card.faculty') or 'FAC/'
            spl_fac_seq = fac_seq.split('/')
            faculty_rec = self.env['odoocms.faculty.staff'].browse(vals['faculty_id'])
            vals['number'] = str(spl_fac_seq[0]) + "/" + str(faculty_rec.school_id.code) + "/" + str(spl_fac_seq[1])
        if vals['type'] == 'employee':
            vals['number'] = self.env['ir.sequence'].next_by_code('op.library.card.staff') or 'STAFF/'

        res = super(OpLibraryCard, self).create(vals)
        if res.type == 'student':
            res.student_id.library_card_id = res
        else:
            res.faculty_id.library_card_id = res
        return res

    @api.onchange('type')
    def onchange_type(self):
        self.student_id = False
        self.faculty_id = False
        self.employee_id = False
        self.partner_id = False

    @api.onchange('student_id', 'faculty_id', 'employee_id')
    def onchange_student_faculty(self):
        if self.student_id:
            self.partner_id = self.student_id.partner_id
        if not self.student_id and self.faculty_id:
            self.partner_id = self.faculty_id.user_partner_id
        if not self.student_id and not self.faculty_id and self.employee_id:
            self.partner_id = self.employee_id.user_partner_id
