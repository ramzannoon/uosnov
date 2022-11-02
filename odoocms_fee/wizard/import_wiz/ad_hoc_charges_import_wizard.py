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


class AdHocChangesImportWizard(models.TransientModel):
    _name = "ad.hoc.charges.import.wizard"
    _description = 'Ad-hoc Charges Import'

    file = fields.Binary('File')
    sequence_opt = fields.Selection([('custom', 'Use Excel/CSV Sequence Number'), ('system', 'Use System Default Sequence Number')], string='Sequence Option', default='custom')
    import_option = fields.Selection([('csv', 'CSV File'), ('xls', 'XLS File')], string='Select', default='xls')

    def action_ad_hoc_charges_import(self):
        """Load data from the CSV file."""
        if self.import_option=='csv':
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

                ad_hoc_list = self.env['odoocms.fee.additional.charges']
                for row_no in range(sheet.nrows):
                    val = {}
                    if row_no <= 0:
                        fields = list(map(lambda row: row.value.encode('utf-8'), sheet.row(row_no)))
                    else:
                        line = list(map(lambda row: str(row.value), sheet.row(row_no)))
                        student_code = line[0] and line[0].strip() or False
                        student_id = False
                        if student_code:
                            student_id = self.env['odoocms.student'].search([('id_number', '=', student_code)])
                        if student_id:
                            ad_hoc_type = line[1] and line[1].strip() or False
                            term_rec = line[2] and line[2].strip() or False

                            if line[4]:
                                date_value = xlrd.xldate_as_tuple(float(line[4]), workbook.datemode)
                                date_value = date(*date_value[:3]).strftime('%Y-%m-%d')
                            else:
                                date_value = fields.Date.today()

                            if ad_hoc_type:
                                term_id = False
                                ad_hoc_type_id = self.env['odoocms.fee.additional.charges.type'].search([('name', '=', ad_hoc_type)])
                                if term_rec:
                                    term_id = self.env['odoocms.academic.term'].search([('name', '=', term_rec)])
                                if ad_hoc_type_id and term_id:
                                    values = {
                                        'student_id': student_id.id,
                                        'student_code': student_code,
                                        'charges_type': ad_hoc_type_id.id,
                                        'program_id': student_id.program_id and student_id.program_id.id or False,
                                        'batch_id': student_id.batch_id and student_id.batch_id.id or False,
                                        'career_id': student_id.career_id and student_id.career_id.id or False,
                                        'term_id': student_id.term_id and student_id.term_id.id or False,
                                        'institute_id': student_id.institute_id and student_id.institute_id.id or False,
                                        'discipline_id': student_id.discipline_id and student_id.discipline_id.id or False,
                                        'campus_id': student_id.campus_id and student_id.campus_id.id or False,
                                        'amount': float(line[3]),
                                        'date': date_value,
                                    }
                                    new_rec = self.env['odoocms.fee.additional.charges'].create(values)
                                    ad_hoc_list |= new_rec
                if ad_hoc_list:
                    invoice_list = ad_hoc_list.mapped('id')
                    form_view = self.env.ref('odoocms_fee.view_odoocms_fee_additional_charges_form')
                    tree_view = self.env.ref('odoocms_fee.view_odoocms_fee_additional_charges_tree')
                    return {
                        'domain': [('id', 'in', ad_hoc_list.ids)],
                        'name': _('Ad hoc Charges'),
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'res_model': 'odoocms.fee.additional.charges',
                        'view_id': False,
                        'views': [
                            (tree_view and tree_view.id or False, 'tree'),
                            (form_view and form_view.id or False, 'form'),
                        ],
                        'type': 'ir.actions.act_window'
                    }
                else:
                    return {'type': 'ir.actions.act_window_close'}
            else:
                raise UserError(_('Please Select the File to Import'))
