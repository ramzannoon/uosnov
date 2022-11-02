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


class OdoocmsHostelRoomBulkVacantWizard(models.TransientModel):
    _name = "odoocms.hostel.room.bulk.vacant.wizard"
    _description = 'Hostel Room Bulk Vacant Wizard'

    def get_default(self):
        if self.env.context.get("message", False):
            return self.env.context.get("message")
        return False

    file = fields.Binary('File')
    name = fields.Text(string="Message", readonly=True, default=get_default)

    def action_bulk_vacant(self):
        fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.file))
        fp.seek(0)
        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(0)

        for row_num in range(1, sheet.nrows):  # From row 2 to Last Row
            _logger.info('Student Record of %s of %s' % (row_num, sheet.nrows))
            row = sheet.row_values(row_num)

            reg_list = str(row[0]).split('.')
            reg_no = reg_list[0]
            if row[1]:
                date_value = xlrd.xldate_as_tuple(row[1], workbook.datemode)
                vacant_date = date(*date_value[:3]).strftime('%Y-%m-%d')
            else:
                vacant_date = fields.Date.today()

            student_id = False
            student_id = self.env['odoocms.student'].search([('code', '=', reg_no)])
            if student_id.hostel_id:
                if vacant_date < student_id.room_id.allocated_date:
                    raise ValidationError('Student Code, %s ,Vacant Date should be Greater then Allocated Date' % (student_id.code))
                if not student_id.hostel_status=='Allocated':
                    raise ValidationError('Student Code %s Room is already Vacant.' % (student_id.code))
                history_values = {
                    'student_id': student_id.id,
                    'student_code': student_id.id_number and student_id.id_number or '',
                    'session_id': student_id.session_id and student_id.session_id.id or False,
                    'program_id': student_id.program_id and student_id.program_id.id or False,
                    'career_id': student_id.career_id and student_id.career_id.id or False,
                    'request_date': vacant_date,
                    'vacant_date': vacant_date,
                    'request_type': 'De Allocation',
                    'state': 'Done',
                    'active': True,
                    'hostel_id': student_id.hostel_id and student_id.hostel_id.id or False,
                    'room_id': student_id.room_id and student_id.room_id.id or False,
                    'room_type': student_id.room_type and student_id.room_type.id or False
                }
                new_hist_rec = self.env['odoocms.student.hostel.history'].create(history_values)
                if new_hist_rec:
                    student_id.write({'hostel_id': False,
                                      'room_id': False,
                                      'room_type': False,
                                      'hostel_state': 'Vacated',
                                      'allocated_date': '',
                                      'vacated_date': vacant_date})
                if not student_id.room_id.student_ids:
                    student_id.room_id.state = 'Vacant'

        view = self.env.ref('odoocms_hostel.view_bulk_vacant_message_wizard_form')
        view_id = view and view.id or False
        context = dict(self._context or {})
        context['message'] = "Bulk Student Vacant File Processed"
        return {
            'name': 'Success',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'odoocms.hostel.room.bulk.vacant.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context,
        }
