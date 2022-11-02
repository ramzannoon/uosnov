from odoo import api, fields, models, _

import logging

_logger = logging.getLogger(__name__)


class AdmissionRegister(models.AbstractModel):
    _name = 'report.odoocms_admission.admission_register_template'
    _description = 'Admission Register Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        # model = self.env.context.get('active_model')

        if data.get('form', False):
            register_id = data['form']['register_id'] and data['form']['register_id'][0] or False
            register = self.env['odoocms.admission.register'].browse(register_id)
        elif docids:
            register = self.env['odoocms.admission.register'].browse(docids[0])

        docs = self.env['odoocms.admission.register'].browse(docids)
        company = self.env.company

        department_program = self.env['odoocms.department'].search([])

        def get_school_total_program(program):
            if program:
                program_total = self.env['odoocms.application'].search_count([
                    ('state', '=', 'offered_program'), ('program_id', '=', program)])
                return program_total

        def get_school_total(program):
            if program:
                program_total = self.env['odoocms.application'].search_count([
                    ('state', '=', 'offered_program')])
                return program_total

        def get_enrol_student(program):
            if program:
                program_total = self.env['odoocms.application'].search_count([
                    ('state', '=', 'offered_program'), ('program_id', '=', program)])
                return program_total

        def get_enrol_student_total(program):
            if program:
                program_total = self.env['odoocms.application'].search_count([
                    ('state', '=', 'offered_program')])
                return program_total

        admission_register_application = len(
            self.env['odoocms.application'].search([('state', '=', 'application')]).ids)

        docargs = {
            'doc_ids': [],
            'docs': docs,
            'company': company,
            'get_enrol_student': get_enrol_student,
            'get_enrol_student_total': get_enrol_student_total,
            'department_program': department_program,
            'get_school_total_program': get_school_total_program,
            'get_school_total': get_school_total,

        }
        return docargs

