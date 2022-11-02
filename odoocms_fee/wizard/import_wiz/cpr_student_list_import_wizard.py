# -*- coding: utf-8 -*-
import pdb
import tempfile
import binascii
import xlrd
from odoo import models, fields, exceptions, api, _
from io import StringIO
import io
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class CPRStudentListImportWizard(models.TransientModel):
    _name = "cpr.student.list.import.wizard"
    _description = 'CPR Student List Import'

    file = fields.Binary('File')
    sequence_opt = fields.Selection([('custom', 'Use Excel/CSV Sequence Number'), ('system', 'Use System Default Sequence Number')], string='Sequence Option', default='custom')
    import_option = fields.Selection([('csv', 'CSV File'), ('xls', 'XLS File')], string='Select', default='xls')

    def action_import_cpr_student_list(self):
        """Load data from the CSV file."""
        if self.import_option=='csv':
            keys = ['student_code', 'tax_amount', 'fee_amount']
            data = base64.b64decode(self.file)
            file_input = io.StringIO(data.decode("utf-8"))
            file_input.seek(0)
            reader_info = []
            reader = csv.reader(file_input, delimiter=',')

            try:
                reader_info.extend(reader)
            except Exception:
                raise exceptions.Warning(_("Not a valid file!"))
            values = {}
            for i in range(len(reader_info)):
                field = list(map(str, reader_info[i]))
                values = dict(zip(keys, field))
                if values:
                    if i==0:
                        continue
                    else:
                        values.update({'option': self.import_option, 'seq_opt': self.sequence_opt})
                        res = self.make_sale(values)
        else:
            if self.file:
                fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
                fp.write(binascii.a2b_base64(self.file))
                fp.seek(0)
                workbook = xlrd.open_workbook(fp.name)
                sheet = workbook.sheet_by_index(0)
                register_id = self.env['odoocms.student.cpr.register'].browse(self._context.get('active_id', False))
                if register_id and register_id.state=='Draft':
                    for row_no in range(sheet.nrows):
                        val = {}
                        if row_no <= 0:
                            fields = list(map(lambda row: row.value.encode('utf-8'), sheet.row(row_no)))
                        else:
                            line = list(map(lambda row: str(row.value), sheet.row(row_no)))
                            student_code = line[0]
                            vals = student_code.split('.')
                            if vals:
                                student_code = vals[0]
                            if student_code:
                                already_exist = False
                                student_id = self.env['odoocms.student'].search([('code', '=', student_code)])
                                if student_id:
                                    already_exist = self.env['odoocms.student.cpr.no'].search([('student_id', '=', student_id.id), ('register_id', '=', register_id.id)])
                                    if not already_exist:
                                        # Create the Record in the Fee Payment Receipts
                                        term_id = self.env['odoocms.academic.term'].search([('name', '=', line[3])])
                                        if not term_id:
                                            UserError(_('Please check the Term Spell, May be you entered it wrongly here.'))
                                        values = {
                                            'student_id': student_id and student_id.id or False,
                                            'student_code': student_code,
                                            'session_id': student_id.session_id and student_id.session_id.id or False,
                                            'career_id': student_id.career_id and student_id.career_id.id or False,
                                            'institute_id': student_id.institute_id and student_id.institute_id.id or False,
                                            'campus_id': student_id.campus_id and student_id.campus_id.id or False,
                                            'program_id': student_id.program_id and student_id.program_id.id or False,
                                            'discipline_id': student_id.discipline_id and student_id.discipline_id.id or False,
                                            # 'term_id': student_id.term_id and student_id.term_id.id or False,
                                            'semester_id': student_id.semester_id and student_id.semester_id.id or False,
                                            'deposit_date': register_id.date,
                                            'father_name': student_id.father_name and student_id.father_name or '',
                                            'father_cnic': student_id.father_guardian_cnic and student_id.father_guardian_cnic or '',
                                            'fee_amount': float(line[1]),
                                            'tax_amount': float(line[2]),
                                            'register_id': register_id.id,
                                            'term_id': term_id and term_id.id or False,
                                        }
                                        new_record = self.env['odoocms.student.cpr.no'].create(values)
                                else:
                                    issue_values = {
                                        'student_code': student_code,
                                        'register_id': register_id.id,
                                        'state': 'Draft',
                                        'notes': 'Student not Found',
                                    }
                                    self.env['odoocms.student.cpr.issues'].create(issue_values)
                else:
                    raise UserError('This CPR Register is not in the Draft State.')

            else:
                raise UserError(_('Please Select the File to Import'))
