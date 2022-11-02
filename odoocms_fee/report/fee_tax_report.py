from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
import logging
import pdb

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


class StudentFeeTaxReport(models.TransientModel):
    _name = 'student.fee.tax.report'
    _description = 'Student Fee Tax Report'

    date_from = fields.Date('From Date', default=fields.Date.today() + relativedelta(day=1))
    date_to = fields.Date('To Date', default=fields.Date.today())

    # term_id = fields.Many2one('odoocms.academic.term', 'Academic Term')

    def make_excel(self):
        workbook = xlwt.Workbook(encoding="utf-8")
        worksheet = workbook.add_sheet("Student Fee Tax Report")
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
        style_date_col3 = xlwt.easyxf(
            "font:height 180; font: name Liberation Sans,color black; align: horiz right;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour white;")
        style_table_totals2 = xlwt.easyxf(
            "font:height 200; font: name Liberation Sans, bold on,color black; align: horiz right;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour ivory;")

        # col width
        col0 = worksheet.col(0)
        col0.width = 256 * 10
        col1 = worksheet.col(1)
        col1.width = 256 * 25
        col2 = worksheet.col(2)
        col2.width = 256 * 40
        col3 = worksheet.col(3)
        col3.width = 256 * 25
        col4 = worksheet.col(4)
        col4.width = 256 * 35
        col5 = worksheet.col(5)
        col5.width = 256 * 25
        col6 = worksheet.col(6)
        col6.width = 256 * 15
        col7 = worksheet.col(7)
        col7.width = 256 * 10
        col8 = worksheet.col(8)
        col8.width = 256 * 20
        col9 = worksheet.col(9)
        col9.width = 256 * 35
        col10 = worksheet.col(10)
        col10.width = 256 * 20
        col11 = worksheet.col(11)
        col11.width = 256 * 20
        col11 = worksheet.col(12)
        col11.width = 256 * 20

        rept_period = "Student Fee Tax Report From " + self.date_from.strftime("%d-%m-%Y") + " To " + self.date_to.strftime("%d-%m-%Y")
        worksheet.write_merge(0, 1, 0, 12, rept_period, style=style_table_header2)
        row = 2
        col = 0
        table_header = ['SR# No.', 'Regn No', 'Name', 'CNIC', 'Father Name', 'Father/Guardian CNIC', 'Campus', 'School', 'Academic Level', 'Email', 'Charged Amount', 'Tax Charged Amount', 'Tax Paid Amount']
        for i in range(13):
            worksheet.write(row, col, table_header[i], style=style_table_header2)
            col += 1

        tax_fee_head = self.env['odoocms.fee.head'].search([('name', '=', 'Advance Tax')])
        domain = [('fee_head_id', '=', tax_fee_head.id),
                  # ('term_id', '=', self.term_id.id),
                  ('move_id.invoice_date', '>=', self.date_from),
                  ('move_id.invoice_date', '<=', self.date_to),
                  ('move_id.invoice_payment_state', '!=', 'cancel')]

        sr = 1
        if tax_fee_head:
            student_ids = []
            students = self.env['account.move.line'].read_group(domain, fields=['student_id'], groupby=['student_id'])
            for l in range(0, len(students)):
                _logger.info('Sequence no %r', l)
                student_ids.append(students[l]['__domain'][1][2])
            student_ids = self.env['odoocms.student'].search([('id', 'in', student_ids)])

            if student_ids:
                for student_id in student_ids.with_progress(msg="Fee Tax Report"):
                    # _logger.info('Sr -> %s', sr)
                    tax_amt = 0
                    tax_paid_amt = 0
                    charge_amt = 0
                    student = self.env['odoocms.student'].search([('id', '=', student_id.id)])
                    mov_lines = self.env['account.move.line'].search([('student_id', '=', student.id),
                                                                      # ('term_id', '=', self.term_id.id),
                                                                      ('move_id.invoice_date', '>=', self.date_from),
                                                                      ('move_id.invoice_date', '<=', self.date_to),
                                                                      ('fee_head_id', '=', tax_fee_head.id),
                                                                      ('move_id.invoice_payment_state', '!=', 'cancel')])
                    for mov_line in mov_lines:
                        tax_amt += mov_line.price_subtotal
                        charge_amt += mov_line.move_id.amount_total

                    paid_mov_lines = mov_lines.filtered(lambda mm: mm.move_id.invoice_payment_state in ('in_payment', 'paid'))
                    if paid_mov_lines:
                        for paid_mov_line in paid_mov_lines:
                            tax_paid_amt += paid_mov_line.price_subtotal

                    row += 1
                    col = 0

                    worksheet.write(row, col, sr, style=style_date_col)
                    col += 1
                    worksheet.write(row, col, student.id_number and student.id_number or '', style=style_date_col2)
                    col += 1
                    worksheet.write(row, col, student.name and student.name or '', style=style_date_col2)
                    col += 1
                    worksheet.write(row, col, student.cnic and student.cnic or '', style=style_date_col2)
                    col += 1
                    worksheet.write(row, col, student.father_name and student.father_name or '', style=style_date_col2)
                    col += 1
                    worksheet.write(row, col, student.father_guardian_cnic and student.father_guardian_cnic or '', style=style_date_col2)
                    col += 1
                    worksheet.write(row, col, student.campus_id and student.campus_id.name or '', style=style_date_col2)
                    col += 1
                    worksheet.write(row, col, student.institute_id and student.institute_id.code or '', style=style_date_col2)
                    col += 1
                    worksheet.write(row, col, student.career_id and student.career_id.code or '', style=style_date_col2)
                    col += 1
                    worksheet.write(row, col, student.email and student.email or '', style=style_date_col2)
                    col += 1
                    worksheet.write(row, col, charge_amt, style=style_date_col3)
                    col += 1
                    worksheet.write(row, col, tax_amt, style=style_date_col3)
                    col += 1
                    worksheet.write(row, col, tax_paid_amt, style=style_date_col3)
                    col += 1
                    sr += 1

        file_data = io.BytesIO()
        workbook.save(file_data)
        wiz_id = self.env['odoocms.fee.report.save.wizard'].create({
            'data': base64.encodebytes(file_data.getvalue()),
            'name': 'Student Fee Tax Report.xls'
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Students Fee Tax Report',
            'res_model': 'odoocms.fee.report.save.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': wiz_id.id,
            'target': 'new'
        }
