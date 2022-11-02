# -*- coding: utf-8 -*-
import time
import tempfile
import binascii
import xlrd
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime
from odoo.exceptions import Warning
from odoo import models, fields, exceptions, api, _
from io import StringIO
import io
from odoo.exceptions import UserError, ValidationError
import pdb

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


class ReassignmentStudentsImportWiz(models.TransientModel):
    _name = "reassignment.students.import.wiz"
    _description = 'Reassignment Students Import Wizard'

    file = fields.Binary('File')
    sequence_opt = fields.Selection([('custom', 'Use Excel/CSV Sequence Number'), ('system', 'Use System Default Sequence Number')],string='Sequence Option', default='custom')
    import_option = fields.Selection([('csv', 'CSV File'), ('xls', 'XLS File')], string='Select', default='xls')

    def reassignment_students_import_action(self):
        """Load data from the CSV file."""
        if self.import_option == 'csv':
            keys = ['barcode']
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
                # val = {}
                field = list(map(str, reader_info[i]))
                values = dict(zip(keys, field))
                if values:
                    if i == 0:
                        continue
                    else:
                        values.update({'option': self.import_option, 'seq_opt': self.sequence_opt})
                        res = self.make_sale(values)
        else:
            fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.file))
            fp.seek(0)
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)
            reassignment_id = self.env['odoocms.student.hostel.reassignment'].browse(self._context.get('active_id', False))

            if reassignment_id and reassignment_id.state == 'Draft':
                for row_no in range(sheet.nrows):
                    val = {}
                    student_list = []
                    if row_no <= 0:
                        fields = list(map(lambda row: row.value.encode('utf-8'), sheet.row(row_no)))
                    else:
                        line = list(map(lambda row: str(row.value), sheet.row(row_no)))
                        reg_no = line[0]
                        vals = reg_no.split('.')
                        if vals:
                            reg_no = vals[0]
                        if reg_no:
                            student_id = False
                            student_id = self.env['odoocms.student'].search([('registration_no', '=', reg_no)])
                            if student_id:
                                reassign_values = {
                                    'student_id': student_id.id,
                                    'student_reg_no': reg_no,
                                    'session_id': student_id.session_id and student_id.session_id.id or False,
                                    'program_id': student_id.program_id and student_id.program_id.id or False,
                                    'type': reassignment_id.type and reassignment_id.type or '',
                                    'reassignment_id': reassignment_id and reassignment_id.id or False,
                                    'date': reassignment_id.date,
                                    'gender': student_id.gender and student_id.gender.upper() or '',
                                }
                                if reassignment_id.type == 'Old Student':
                                    reassign_values['cgpa'] = line[1] and float(line[1]) or 0.0
                                if reassignment_id.type == 'Freshmen':
                                    reassign_values['merit_no'] = line[1] and str(line[1]) or ''
                                reassignment_line_id = self.env['odoocms.student.hostel.reassignment.line'].create(reassign_values)

                            # if student not found in the System
                            # Then Create a record in the Reassignment Issue Table
                            else:
                                issue_values = {
                                    'student_reg_no': reg_no,
                                    'reassignment_id': reassignment_id.id,
                                    'remarks': 'This Reg No. Not Found in the System. Please Check it.',
                                    'state': 'Draft',
                                }
                                issue_line_id = self.env['odoocms.student.hostel.reassignment.issue'].create(issue_values)

            else:
                raise UserError('This is not in the Draft State.')