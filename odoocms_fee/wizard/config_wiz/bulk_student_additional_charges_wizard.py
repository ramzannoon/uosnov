# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError, UserError
import io
import logging
_logger = logging.getLogger(__name__)


class BulkStudentAdditionalChargesWizard(models.TransientModel):
	_name = "bulk.student.additional.charges.wizard"
	_description = "Bulk Student Ad-hoc Charges Wizard"

	charges_type = fields.Many2one('odoocms.fee.additional.charges.type', 'Ad-hoc Charges Type', required=True)
	amount = fields.Float('Amount', required=True)
	session_id = fields.Many2one('odoocms.academic.session', 'Academic Session')
	career_ids = fields.Many2many('odoocms.career', 'bulk_std_add_charges_wiz_career_rel', 'wiz_id', 'career_id', 'Academic Levels')
	program_ids = fields.Many2many('odoocms.program', 'bulk_std_add_charges_wiz_program_rel', 'wiz_id', 'program_id', 'Programs')
	batch_ids = fields.Many2many('odoocms.batch', 'bulk_std_add_charges_wiz_batch_rel', 'wiz_id', 'batch_id', 'Batches')
	campus_ids = fields.Many2many('odoocms.campus', 'bulk_std_add_charges_wiz_campus_rel', 'wiz_id', 'campus_id', 'Campuses')
	term_ids = fields.Many2many('odoocms.academic.term', 'bulk_std_add_charges_wiz_academic_term_rel', 'wiz_id', 'academic_term_id', 'Academic Terms')
	semester_ids = fields.Many2many('odoocms.semester', 'bulk_std_add_charges_wiz_semester_rel', 'wiz_id', 'semester_id', 'Semesters')
	student_ids = fields.Many2many('odoocms.student', 'bulk_std_add_charges_wiz_student_rel', 'wiz_id', 'student_id', 'Students')
	date = fields.Date('Date', default=fields.Date.today())

	def action_generate_entries(self):
		for rec in self:
			students = False
			domain = [('session_id', '=', rec.session_id.id),]
			if rec.career_ids:
				domain.append(('career_id', 'in', rec.career_ids.ids))
			if rec.program_ids:
				domain.append(('program_id', 'in', rec.program_ids.ids))
			if rec.batch_ids:
				domain.append(('batch_id', 'in', rec.batch_ids.ids))
			if rec.campus_ids:
				domain.append(('campus_id', 'in', rec.campus_ids.ids))
			if rec.term_ids:
				domain.append(('term_id', 'in', rec.term_ids.ids))
			if rec.semester_ids:
				domain.append(('semester_id', 'in', rec.semester_ids.ids))
			if not rec.student_ids:
				students = self.env['odoocms.student'].search(domain)
			if rec.student_ids:
				students = rec.student_ids
			if rec.amount <= 0:
				raise UserError(_("Amount Should be Greater then the Zero"))

			if students:
				for student in students:
					student_add_charges = {
						'student_id': student.id,
						'student_code': student.id_number and student.id_number or '',
						'program_id': student.program_id and student.program_id.id or False,
						'batch_id': student.batch_id and student.batch_id.id or False,
						'session_id': student.session_id and student.session_id.id or False,
						'career_id': student.career_id and student.career_id.id or False,
						'term_id': student.term_id and student.term_id.id or False,
						'semester_id': student.semester_id and student.semester_id.id or False,
						'institute_id': student.institute_id and student.institute_id.id or False,
						'discipline_id': student.discipline_id and student.discipline_id.id or False,
						'charges_type': rec.charges_type and rec.charges_type.id or False,
						'amount': rec.amount,
						'date': rec.date,
						'state': 'draft',
					}
					new_rec = self.env['odoocms.fee.additional.charges'].create(student_add_charges)

