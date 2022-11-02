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

# try:
#     import csv
# except ImportError:
#     _logger.debug('Cannot `import csv`.')

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

    def import_hostel_data(self):
        fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.file))
        fp.seek(0)
        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(0)

        for row_num in range(1, sheet.nrows):  # From row 2 to Last Row
            _logger.info('Employee Record of %s of %s' % (row_num, sheet.nrows))
            row = sheet.row_values(row_num)
            old_list = str(row[0]).split('.')
            old_id = old_list[0]

            pf_pre_list = str(row[1]).split('.')
            pf_pre = pf_pre_list[0]

            pf_post_list = str(row[1]).split('.')
            pf_post = pf_post_list[0]

            gender = ''
            if row[5] and row[5] == 'M':
                gender = 'male'
            if row[5] and row[5] == 'F':
                gender = 'female'

            employment_type = ''
            if row[12] == 'Regular':
                employment_type = 'Regular'
            if row[12] and row[12] == 'Contract':
                employment_type = 'Contract'

            emp_dict = {
                'old_id': old_id,
                'status': 1,
                'pf_pre': pf_pre,
                'pf_post': pf_post,
                'file_no':  row[3] and row[3] or '',
                'giki_payscale': row[4] and row[4] or '',
                'gender': gender,
                'name': row[6] and row[6] or '',
                'father_name': row[7] and row[7] or '',
                'group_insurance': row[11] and row[11] or '',
                'employment_type': employment_type,
                'contract_period': row[13] and row[13] or '',
                'age': row[18] and [18] or '',
                'street': row[20] and row[20] or '',
                'mobile_phone': row[21] and row[21] or '',
                'work_phone': row[21] and row[21] or '',
                'domicile': row[22] and row[22] or '',
                'cnic': row[23] and row[23] or '',
                'subject': row[24] and row[24] or '',
                'specialization_area': row[25] and row[25] or '',
                'university': row[26] and row[26] or '',
                'country_id': 177,
                'degree_awarding_year': row[28] and row[28] or '',
                'file_discrepancy': row[29] and row[29] or '',
                'work_email':row[30] and row[30] or '',
                'private_email': row[31] and row[31] or '',
                'giki_total_service': row[32] and row[32] or '',
                'existing_rank_service_length': row[33] and row[33] or '',
            }
            new_rec = self.env['hr.employee'].create(emp_dict)

            if row[8]:
                date_value = xlrd.xldate_as_tuple(row[8], workbook.datemode)
                grade_date = date(*date_value[:3]).strftime('%Y-%m-%d')
                new_rec.giki_joining_date = grade_date

            if row[9]:
                date_value = xlrd.xldate_as_tuple(row[9], workbook.datemode)
                grade_date = date(*date_value[:3]).strftime('%Y-%m-%d')
                new_rec.existing_rank_joining_date = grade_date

            if row[10]:
                date_value = xlrd.xldate_as_tuple(row[10], workbook.datemode)
                grade_date = date(*date_value[:3]).strftime('%Y-%m-%d')
                new_rec.probation_termination_due_date = grade_date

            if row[14]:
                date_value = xlrd.xldate_as_tuple(row[14], workbook.datemode)
                grade_date = date(*date_value[:3]).strftime('%Y-%m-%d')
                new_rec.existing_contract_date = grade_date

            if row[15]:
                date_value = xlrd.xldate_as_tuple(row[15], workbook.datemode)
                grade_date = date(*date_value[:3]).strftime('%Y-%m-%d')
                new_rec.current_contract_expiry_date = grade_date

            if row[16]:
                date_value = xlrd.xldate_as_tuple(row[16], workbook.datemode)
                grade_date = date(*date_value[:3]).strftime('%Y-%m-%d')
                new_rec.leaving_date = grade_date

            if row[17]:
                date_value = xlrd.xldate_as_tuple(row[17], workbook.datemode)
                grade_date = date(*date_value[:3]).strftime('%Y-%m-%d')
                new_rec.birthday = grade_date

            if row[19]:
                date_value = xlrd.xldate_as_tuple(row[19], workbook.datemode)
                grade_date = date(*date_value[:3]).strftime('%Y-%m-%d')
                new_rec.superannuation_date = grade_date

            if row[19]:
                date_value = xlrd.xldate_as_tuple(row[19], workbook.datemode)
                grade_date = date(*date_value[:3]).strftime('%Y-%m-%d')
                new_rec.superannuation_date = grade_date

