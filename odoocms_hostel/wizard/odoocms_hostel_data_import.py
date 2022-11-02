# -*- coding: utf-8 -*-
import time
import tempfile
import binascii
import xlrd
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime
from odoo.exceptions import Warning
from odoo import models, fields, exceptions, api, _

import logging

_logger = logging.getLogger(__name__)
from io import StringIO
import io
from odoo.exceptions import UserError, ValidationError
import pdb

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


# if row[7].ctype == 3:  # Date
# if row[7]:
#     date_value = xlrd.xldate_as_tuple(row[7], workbook.datemode)
#     grade_date = date(*date_value[:3]).strftime('%Y-%m-%d')
#     registration.grade_date = grade_date


class HostelDataImportWizard(models.TransientModel):
    _name = "odoocms.hostel.data.import.wizard"
    _description = 'Hostel Data Import Wizard'

    file = fields.Binary('File')

    # *******************************************
    # for Opening Balances                      *
    # *******************************************

    # def import_hostel_data(self):
    #     fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
    #     fp.write(binascii.a2b_base64(self.file))
    #     fp.seek(0)
    #     workbook = xlrd.open_workbook(fp.name)
    #     sheet = workbook.sheet_by_index(0)
    #
    #     move_lines = []
    #     move_rec = self.env['account.move'].search([('id', '=', 10)])
    #     debit_sum = 0
    #     credit_sum = 0
    #     balance = 0
    #
    #     for row_num in range(1, sheet.nrows):  # From row 2 to Last Row
    #         _logger.info('Employee Record of %s of %s' % (row_num, sheet.nrows))
    #         row = sheet.row_values(row_num)
    #         code_list = str(row[0]).split('.')
    #         code = code_list[0]
    #         account_id = self.env['account.account'].search([('code', '=', code)])
    #
    #         debit_sum += row[2] and int(row[2]) or 0
    #         credit_sum += row[3] and int(row[3]) or 0
    #         if account_id:
    #             move_line_values =(0, 0, {
    #                 'account_id': account_id.id,
    #                 'name': row[1] and str(row[1]) or '',
    #                 'debit': row[2] and int(row[2]) or 0,
    #                 'credit': row[3] and int(row[3]) or 0,
    #             })
    #             move_lines.append(move_line_values)
    #
    #     balance = debit_sum - credit_sum
    #     move_line_values = (0, 0, {
    #         'account_id': 404,
    #         'name': 'Adjustment of Opening Balance',
    #         'debit': abs(balance) if balance < 0 else 0,
    #         'credit': balance if balance > 0 else 0,
    #     })
    #     move_lines.append(move_line_values)
    #     move_rec.update({'line_ids': move_lines})

    # ******************************************#
    # Create the Hostel History of the student  #
    # ******************************************#
    def import_hostel_data(self):
        fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.file))
        fp.seek(0)
        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(0)

        for row_num in range(1, sheet.nrows):  # From row 2 to Last Row
            _logger.info('Employee Record of %s of %s' % (row_num, sheet.nrows))
            row = sheet.row_values(row_num)

            reg_list = str(row[1]).split('.')
            reg_no = reg_list[0]

            room_list = str(row[2]).split('.')
            room_no = room_list[0]

            hostel_list = str(row[3]).split('.')
            hostel_id = int(hostel_list[0])

            student_id = False
            student_id = self.env['odoocms.student'].search([('registration_no', '=', reg_no)])
            if student_id:
                room_id = self.env['odoocms.hostel.room'].search([('hostel_id', '=', hostel_id), ('code', '=', room_no)])
                if room_id:
                    if int(room_id.room_capacity) > int(room_id.allocated_number):
                        history_vals = {
                            'student_id': student_id.id,
                            'student_code': reg_no,
                            'session_id': student_id.session_id and student_id.session_id.id or False,
                            'program_id': student_id.program_id and student_id.program_id.id or False,
                            'career_id': student_id.career_id and student_id.career_id.id or False,
                            'request_date': fields.Date.today(),
                            'allocate_date': fields.Date.today(),
                            'request_type': 'Re-Allocate',
                            'state': 'Done',
                            'active': True,
                            'hostel_id': hostel_id,
                            'room_id': room_id and room_id.id or False,
                            'room_type': room_id.room_type and room_id.room_type.id or False
                        }
                        self.env['odoocms.student.hostel.history'].create(history_vals)
                        student_id.hostel_id = hostel_id
                        student_id.room_id = room_id and room_id.id or False
                        student_id.room_type = room_id.room_type and room_id.room_type.id or False
                        student_id.allocated_date = fields.Date.today()

    # *******************************************
    # Student Creation                          *
    # *******************************************

    # def import_hostel_data(self):
    #     fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
    #     fp.write(binascii.a2b_base64(self.file))
    #     fp.seek(0)
    #     workbook = xlrd.open_workbook(fp.name)
    #     sheet = workbook.sheet_by_index(0)
    #
    #     for row_num in range(1, sheet.nrows):  # From row 2 to Last Row
    #         _logger.info('Student Record of %s of %s' % (row_num, sheet.nrows))
    #         row = sheet.row_values(row_num)
    #
    #         reg_list = str(row[1]).split('.')
    #         reg_no = reg_list[0]
    #         student_id = False
    #         student_id = self.env['odoocms.student'].search([('registration_no', '=', reg_no)])
    #         if not student_id:
    #             faculty_id = self.env['odoocms.faculty'].search([('name', '=', row[3])])
    #             department_id = self.env['odoocms.department'].search([('name', '=', row[4])])
    #             program_id = self.env['odoocms.program'].search([('name', '=', row[5])])
    #             career_id = self.env['odoocms.career'].search([('name', '=', row[5])])
    #
    #             std_values = {
    #                 'registration_no': reg_no,
    #                 'first_name': row[2],
    #                 'faculty_id': faculty_id and faculty_id.id or False,
    #                 'department_id': department_id and department_id.id or False,
    #                 'program_id': program_id and program_id.id or False,
    #                 'career_id': career_id and career_id.id or False,
    #                 'gender': 'f',
    #                 'nationality': 177,
    #                 'session_id': 5,
    #                 'email': "u" + reg_no + "@giki.edu.pk",
    #                 'mess_status': 'OUT',
    #                 'mess_security': 8000,
    #                 'blower_non_blower_users': 'Blower',
    #             }
    #             self.env['odoocms.student'].create(std_values)
    #

    def import_fall2020_data(self):
        fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.file))
        fp.seek(0)
        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(0)

        for row_num in range(1, sheet.nrows):  # From row 2 to Last Row
            _logger.info('Employee Record of %s of %s' % (row_num, sheet.nrows))
            row = sheet.row_values(row_num)
            reg_no = row[0]

            student_id = False
            student_id = self.env['odoocms.student'].search([('code', '=', reg_no)])
            fall202_vals = {
                'student_id': student_id and student_id.id or False,
                'student_code': reg_no,
                'student_name': row[1],
                'amount': row[2],
                'status': 'm' if student_id else 'n',
                'fee_status': 'n',
                'date': fields.Date.today(),
            }
            new_rec = self.env['nust.student.fall20.fee'].create(fall202_vals)
