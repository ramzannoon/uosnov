import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time

import logging

_logger = logging.getLogger(__name__)

from io import StringIO
import io

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


class StudentFeeReceivableReport(models.TransientModel):
    _name = 'student.fee.receivable.report'
    _description = 'Student Fee Receivable Report'

    institute_ids = fields.Many2many('odoocms.institute', 'student_fee_receivable_institute_rel', 'receivable_rep_id', 'institute_id', 'Schools')
    campus_ids = fields.Many2many('odoocms.campus', 'student_fee_receivable_campus_rel', 'receivable_rep_id', 'campus_id', 'Campuses')

    def make_excel(self):
        workbook = xlwt.Workbook(encoding="utf-8")
        worksheet = workbook.add_sheet("Student Fee Receivable Report")
        style_title = xlwt.easyxf(
            "font:height 350; font: name Liberation Sans, bold on,color black; align: horiz center, vert center; borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour cyan_ega;")
        style_table_header = xlwt.easyxf(
            "font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center, vert center;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour silver_ega;")
        style_table_header2 = xlwt.easyxf(
            "font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour sea_green;alignment: wrap True;")
        style_table_header3 = xlwt.easyxf(
            "font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour ivory;alignment: wrap True;")

        style_table_totals = xlwt.easyxf(
            "font:height 150; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour cyan_ega;")
        style_date_col = xlwt.easyxf(
            "font:height 180; font: name Liberation Sans,color black; align: horiz right;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour white;")
        style_date_col2 = xlwt.easyxf(
            "font:height 180; font: name Liberation Sans,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour white;")
        style_table_totals2 = xlwt.easyxf(
            "font:height 200; font: name Liberation Sans, bold on,color black; align: horiz right;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour ivory;")

        # col width
        col0 = worksheet.col(0)
        col0.width = 256 * 10
        col1 = worksheet.col(1)
        col1.width = 256 * 15
        col2 = worksheet.col(2)
        col2.width = 256 * 30
        col3 = worksheet.col(3)
        col3.width = 256 * 30
        col4 = worksheet.col(4)
        col4.width = 256 * 15
        col5 = worksheet.col(5)
        col5.width = 256 * 30
        col6 = worksheet.col(6)
        col6.width = 256 * 35
        col7 = worksheet.col(7)
        col7.width = 256 * 35
        col8 = worksheet.col(8)
        col8.width = 256 * 20
        col9 = worksheet.col(9)
        col9.width = 256 * 20
        col10 = worksheet.col(10)
        col10.width = 256 * 15
        col11 = worksheet.col(11)
        col11.width = 256 * 20
        col12 = worksheet.col(12)
        col12.width = 256 * 20
        col13 = worksheet.col(13)
        col13.width = 256 * 20
        col14 = worksheet.col(14)
        col14.width = 256 * 20
        col15 = worksheet.col(15)
        col15.width = 256 * 20
        col16 = worksheet.col(16)
        col16.width = 256 * 20
        col17 = worksheet.col(17)
        col17.width = 256 * 20
        col18 = worksheet.col(18)
        col18.width = 256 * 20
        col19 = worksheet.col(19)
        col19.width = 256 * 20
        col20 = worksheet.col(20)
        col20.width = 256 * 20

        dom = [('amount_residual', '>', 0),
               ('move_type', '=', 'out_invoice'),
               ('invoice_payment_state', '!=', 'cancel'),
               ('is_scholarship_fee', '!=', True)]

        if self.institute_ids:
            dom.append(('institute_id', 'in', self.institute_ids.ids))
        if self.campus_ids:
            dom.append(('campus_id', 'in', self.campus_ids.ids))

        student_ids = []
        students = self.env['account.move'].read_group(dom, fields=['student_id'], groupby=['student_id'])
        for l in range(0, len(students)):
            _logger.info('Sequence no %r', l)
            student_ids.append(students[l]['__domain'][1][2])
        student_ids = self.env['odoocms.student'].search([('id', 'in', student_ids)])

        if student_ids:
            table_header = self.action_find_senior_student(student_ids)
            header_len = len(table_header)

            worksheet.write_merge(0, 1, 0, (header_len - 1), 'Fee Receivable Report', style=style_table_header2)
            row = 2
            col = 0

            for i in range(header_len):
                worksheet.write(row, col, table_header[i], style=style_table_header2)
                col += 1

            sr = 1
            for student_id in student_ids.with_progress(msg="Fee Receivable Report"):
                # _logger.info('sr no %r', sr)
                row_total = 0
                admitted_term = ''

                row += 1
                col = 0
                worksheet.write(row, col, sr, style=style_date_col)
                col += 1
                worksheet.write(row, col, student_id.id_number, style=style_date_col2)
                col += 1
                worksheet.write(row, col, student_id.name, style=style_date_col2)
                col += 1
                worksheet.write(row, col, student_id.father_name and student_id.father_name or '', style=style_date_col2)
                col += 1
                worksheet.write(row, col, student_id.career_id.code, style=style_date_col2)
                col += 1
                worksheet.write(row, col, student_id.program_id.code, style=style_date_col2)
                col += 1
                worksheet.write(row, col, student_id.program_id.name, style=style_date_col2)
                col += 1
                worksheet.write(row, col, student_id.institute_id.name, style=style_date_col2)
                col += 1
                # worksheet.write(row, col, move.student_tags and move.student_tags or '', style=style_date_col2)
                worksheet.write(row, col, student_id.receipt_ids[-1:].student_tags, style=style_date_col2)
                col += 1
                worksheet.write(row, col, student_id.session_id.name, style=style_date_col2)
                col += 1
                worksheet.write(row, col, 'No', style=style_date_col2)
                col += 1
                worksheet.write(row, col, student_id.email and student_id.email or '', style=style_date_col2)
                col += 1
                worksheet.write(row, col, student_id.phone and student_id.phone or '', style=style_date_col2)
                col += 1

                for cc in range((header_len - 2), 12, -1):
                    table_header[cc] = table_header[cc]
                    result = self.get_unpaid_detail(student_id, table_header, cc)
                    worksheet.write(row, cc, result, style=style_date_col)
                    col += 1
                    row_total += result
                worksheet.write(row, col, row_total, style=style_date_col)
                col += 1

                sr += 1

        file_data = io.BytesIO()
        workbook.save(file_data)
        wiz_id = self.env['odoocms.fee.report.save.wizard'].create({
            'data': base64.encodebytes(file_data.getvalue()),
            'name': 'Fee Receivable Report.xls'
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Students Fee Receivable Report',
            'res_model': 'odoocms.fee.report.save.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': wiz_id.id,
            'target': 'new'
        }

    def action_find_senior_student(self, student_ids):
        # table_header = False
        if student_ids:
            table_header = ['SR# No.', 'Student ID', 'Student Name', 'Father Name', 'Academic Level', 'Program Code', 'Program Title',
                            'School', 'Student Groups', 'Admit Term', 'Payment Plan', 'Email', 'Phone']
            current_term = False
            student_ids = student_ids.sorted(key=lambda s: s.session_id.code)
            senior_student = student_ids[0]
            # Remarked because report takes time so i changed it to current term for next term i have to change it
            # 15-06-2021
            # admission_session = int(senior_student.session_id.code)
            config_term = self.env['ir.config_parameter'].sudo().get_param('odoocms.current_term')
            if config_term:
                config_term_rec = self.env['odoocms.academic.term'].search([('id', '=', int(config_term))])
                current_term_list = config_term_rec.code.split('-')
                current_term = int(current_term_list[1])
            if current_term:
                admission_session = current_term
                for i in range(admission_session, current_term + 1):
                    table_header.append("Spring-" + str(i))
                    table_header.append(("Summer-" + str(i)))
                    table_header.append('Fall-' + str(i))
            table_header.append('Total Payable')
        return table_header

    def get_unpaid_detail(self, student_id, table_header, cc):
        result = 0
        term_id = self.env['odoocms.academic.term'].search([('code', '=', table_header[cc])])
        if term_id:
            open_invoices = self.env['account.move'].search([('student_id', '=', student_id.id),
                                                             ('term_id', '=', term_id.id),
                                                             ('move_type', '=', 'out_invoice'),
                                                             ('invoice_payment_state', '!=', 'cancel'),
                                                             ('amount_residual', '>', 0),
                                                             ('is_scholarship_fee', '!=', True)])
            if open_invoices:
                for open_invoice in open_invoices:
                    result += open_invoice.amount_residual
        return result


class CMSFeeReportSaveWizard(models.TransientModel):
    _name = "odoocms.fee.report.save.wizard"
    _description = 'Fee Report Save Wizard'

    name = fields.Char('filename', readonly=True)
    data = fields.Binary('file', readonly=True)
