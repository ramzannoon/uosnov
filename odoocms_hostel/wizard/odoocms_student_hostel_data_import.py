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


class StudentHostelDataImportWizard(models.TransientModel):
    _name = "odoocms.student.hostel.data.import.wizard"
    _description = 'Student Hostel Data Import Wizard'

    file = fields.Binary('File')

    def import_student_hostel_data(self):
        fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.file))
        fp.seek(0)
        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(0)

        for row_num in range(1, sheet.nrows):  # From row 2 to Last Row
            _logger.info('Student Record of %s of %s' % (row_num, sheet.nrows))
            row = sheet.row_values(row_num)
            allocated_date = False

            reg_no = str(row[0])
            hostel_name = str(row[1])
            room_name = str(row[2])
            room_type = str(row[3])

            if row[4]:
                date_value = xlrd.xldate_as_tuple(row[4], workbook.datemode)
                allocated_date = date(*date_value[:3]).strftime('%Y-%m-%d')

            student_id = False
            student_id = self.env['odoocms.student'].search([('id_number', '=', reg_no)])
            hostel_rec = self.env['odoocms.hostel'].search([('name', '=', hostel_name)])
            room_type_rec = self.env['odoocms.hostel.room.type'].search([('name', '=', room_type)])

            if student_id and hostel_rec:
                room_rec = self.env['odoocms.rooms'].search([('name', '=', room_name)])
                hostel_room = self.env['odoocms.hostel.room'].search([('hostel_id', '=', hostel_rec.id), ('room_id', '=', room_rec.id), ('room_type', '=', room_type_rec.id)])
                if hostel_room:
                    if int(hostel_room.room_capacity) > int(hostel_room.allocated_number):
                        student_id.hostel_id = hostel_rec.id
                        student_id.room_id = hostel_room and hostel_room.id or False
                        student_id.room_type = hostel_room.room_type and hostel_room.room_type.id or False
                        if allocated_date:
                            student_id.allocated_date = allocated_date
                            student_id.hostel_state = 'Allocated'
                        if int(hostel_room.vacancy)==0:
                            hostel_room.state = 'Occupied'

                        history_values = {
                            'student_id': student_id.id,
                            'student_code': student_id.id_number and student_id.id_number or '',
                            'session_id': student_id.session_id and student_id.session_id.id or False,
                            'program_id': student_id.program_id and student_id.program_id.id or False,
                            'career_id': student_id.career_id and student_id.career_id.id or False,
                            'request_date': allocated_date,
                            'allocate_date': allocated_date,
                            'request_type': 'New Allocation',
                            'state': 'Done',
                            'active': True,
                            'hostel_id': hostel_rec and hostel_rec.id or False,
                            'room_id': hostel_room and hostel_room.id or False,
                            'room_type': room_type_rec and room_type_rec.id or False
                        }
                        self.env['odoocms.student.hostel.history'].create(history_values)
