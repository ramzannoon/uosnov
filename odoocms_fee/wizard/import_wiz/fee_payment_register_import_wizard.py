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


class FeePaymentRegisterImportWizard(models.TransientModel):
    _name = "fee.payment.register.import.wizard"
    _description = 'Fee Import into the Payment Register'

    file = fields.Binary('File')
    sequence_opt = fields.Selection([('custom', 'Use Excel/CSV Sequence Number'), ('system', 'Use System Default Sequence Number')], string='Sequence Option', default='custom')
    import_option = fields.Selection([('csv', 'CSV File'), ('xls', 'XLS File')], string='Select', default='xls')

    def fee_payment_import_action(self):
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
                register_id = self.env['odoocms.fee.payment.register'].browse(self._context.get('active_id', False))
                if register_id and register_id.state=='Draft':
                    for row_no in range(sheet.nrows):
                        val = {}
                        if row_no <= 0:
                            fields = list(map(lambda row: row.value.encode('utf-8'), sheet.row(row_no)))
                        else:
                            line = list(map(lambda row: str(row.value), sheet.row(row_no)))
                            barcode = line[0]
                            vals = barcode.split('.')
                            if vals:
                                barcode = vals[0]
                            if barcode:
                                invoice_id = False
                                already_exist = False
                                already_exist = self.env['odoocms.fee.payment'].search([('receipt_number', '=', barcode),
                                                                                        ('payment_register_id', '=', register_id.id)])
                                if not already_exist:
                                    already_exist = self.env['odoocms.fee.payment'].search([('receipt_number', '=', barcode),
                                                                                            ('invoice_id.amount_residual', '=', 0.0)])
                                if not already_exist:
                                    already_exist = self.env['account.move'].search([('name', '=', barcode),
                                                                                     ('move_type', '=', 'out_invoice'), ('amount_residual', '=', 0.0)])
                                if not already_exist:
                                    fee_payment_rec_exist = self.env['odoocms.fee.payment'].search([('receipt_number', '=', barcode)], order='id', limit=1)
                                    if fee_payment_rec_exist:
                                        if fee_payment_rec_exist.received_amount >= fee_payment_rec_exist.amount:
                                            already_exist = fee_payment_rec_exist

                                if not already_exist:
                                    invoice_id = self.env['account.move'].search([('barcode', '=', barcode), ('move_type', '=', 'out_invoice'), ('amount_residual', '>', 0)])
                                    if not invoice_id:
                                        invoice_id = self.env['account.move'].search([('name', '=', barcode), ('move_type', '=', 'out_invoice'), ('amount_residual', '>', 0)])

                                    # Create the Record in the Fee Payment Receipts
                                    if invoice_id:
                                        values = {
                                            'invoice_id': invoice_id.id,
                                            'receipt_number': barcode,
                                            'id_number': invoice_id.student_id.id_number,
                                            'student_id': invoice_id.student_id and invoice_id.student_id.id or False,
                                            'invoice_status': invoice_id.invoice_payment_state and invoice_id.invoice_payment_state or '',
                                            'amount': invoice_id.amount_residual,
                                            'session_id': invoice_id.student_id.session_id and invoice_id.student_id.session_id.id or False,
                                            'career_id': invoice_id.student_id.career_id and invoice_id.student_id.career_id.id or False,
                                            'institute_id': invoice_id.student_id.institute_id and invoice_id.student_id.institute_id.id or False,
                                            'campus_id': invoice_id.student_id.campus_id and invoice_id.student_id.campus_id.id or False,
                                            'program_id': invoice_id.student_id.program_id and invoice_id.student_id.program_id.id or False,
                                            'discipline_id': invoice_id.student_id.discipline_id and invoice_id.student_id.discipline_id.id or False,
                                            'term_id': invoice_id.student_id.term_id and invoice_id.student_id.term_id.id or False,
                                            'semester_id': invoice_id.student_id.semester_id and invoice_id.student_id.semester_id.id or False,
                                            'journal_id': 1,
                                            'date': register_id.date,
                                            'payment_register_id': register_id.id,
                                            'received_amount': line[1] and float(line[1]),
                                        }
                                        self.env['odoocms.fee.payment'].create(values)

                                # Already Exit But Payment Register is not Set
                                if already_exist and already_exist._table=='odoocms_fee_payment':
                                    for already_exist_id in already_exist:
                                        if already_exist_id.payment_register_id:
                                            already_exist_id.payment_register_id = register_id.id

                                # Already Exit And Payment Register is also Set
                                if already_exist and already_exist._table=='odoocms_fee_payment':
                                    for already_exist_id in already_exist:
                                        if already_exist.payment_register_id:
                                            # Create Records in the Processed Receipts
                                            notes = "Already Processed in " + (already_exist_id.payment_register_id.name and already_exist_id.payment_register_id.name or '') + " on " + already_exist_id.date.strftime("%d/%m/%Y")
                                            processed_values = {
                                                'barcode': barcode,
                                                'name': barcode,
                                                'payment_register_id': register_id.id,
                                                'notes': notes,
                                            }
                                            self.env['odoocms.fee.processed.receipts'].create(processed_values)

                                # If invoice_id is not found then create in the Non Barcode Receipts
                                if not invoice_id and not already_exist:
                                    non_barcode_exit = self.env['odoocms.fee.non.barcode.receipts'].search([('barcode', '=', barcode)])
                                    if not non_barcode_exit:
                                        non_barcode_vals = {
                                            'barcode': barcode,
                                            'name': barcode,
                                            'payment_register_id': register_id.id,
                                        }
                                        self.env['odoocms.fee.non.barcode.receipts'].create(non_barcode_vals)
                else:
                    raise UserError('This Fee Register (Bank Scroll) is not in the Draft State.')

            else:
                raise UserError(_('Please Select the File to Import'))
