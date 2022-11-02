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


class FeeImportWizard(models.TransientModel):
    _name = "odoocms.fee.import.wizard"
    _description = 'Fee Import Wizard'
    
    file = fields.Binary('File')
    # register_only = fields.Boolean('Register Only',default=False)
    # classes_only = fields.Boolean('Classes Only',default=True)
    

    def import_fee_data(self):
        sinvoice = self.env['account.move']
        
        fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.file))
        fp.seek(0)
        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(0)
        
        rows = self.env['odoo.progress'].search([('name','<=',sheet.nrows)])
        
        for row_num in rows.with_progress(msg="Fee Import"):
            row = sheet.row_values(row_num.name)

            student_code = row[0]
            student = self.env['odoocms.student'].search([('code', '=', student_code)])
            if not student:
                raise UserError('Student %s not found in database' % (student_code,))
            
            term = int(row[1])
            academic_semester = self.env['odoocms.academic.semester'].search([('short_code', '=', term)])
            if not academic_semester:
                raise UserError('Term not found: %s' % (term))

            date_value = xlrd.xldate_as_tuple(row[2], workbook.datemode)
            posted_date = date(*date_value[:3]).strftime('%Y-%m-%d')

            receipt = row[3]
            # fee_structure_id =
            
            st_invoice = sinvoice.search([('name', '=', receipt)])
            if not st_invoice:
                data = {
                    'student_id': student.id,
                    'academic_semester_id': academic_semester.id,
                    'date_invoice': posted_date,
                    'name': receipt,
                    'currency_id': 165,
                    # 'fee_structure_id': fee_structure_id.id,
                }
                st_invoice = sinvoice.create(data)
            
            
            item_type = int(row[4])
            description = row[5]
            head_id = self.env['odoocms.fee.head'].search([('item_type', '=', item_type)])
            item_type_code = row[6]
            
            data = {
                'name': description,
                'item_type': item_type,
                'item_type_code': item_type_code,
                'fee_head_id': head_id.id,
                'amount': float(row[7]),
                'paid_amount': float(row[8]),
                'balance': float(row[9]),
                'prev_invoice_no': row[10],
                'invoice_id': st_invoice.id
            }
            self.env['account.move.line'].create(data)
  
