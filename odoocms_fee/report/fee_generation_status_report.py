from odoo import api, fields, models, _

import logging

_logger = logging.getLogger(__name__)
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


class StudentFeeGenerateStatusReport(models.TransientModel):
    _name = 'student.fee.generation.status.report'
    _description = 'Student Fee Generation Status Report'

    term_id = fields.Many2one('odoocms.academic.term', 'Term')
    institute_ids = fields.Many2many('odoocms.institute', 'student_fee_generation_status_institute_rel', 'report_wiz_id', 'institute_id', 'Schools')
    campus_ids = fields.Many2many('odoocms.campus', 'student_fee_generation_status_campus_rel', 'report_wiz_id', 'campus_id', 'Campuses')
    career_ids = fields.Many2many('odoocms.career', 'student_fee_generation_status_career_rel', 'report_wiz_id', 'career_id', 'Academic Level')

    def make_excel(self):
        workbook = xlwt.Workbook(encoding="utf-8")
        worksheet = workbook.add_sheet("Student Fee Generation Status Report")
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

        worksheet.write_merge(0, 1, 0, 9, 'Student Fee Generation Status Report of ' + self.term_id.name, style=style_table_header2)
        row = 2
        col = 0
        table_header = ['SR# No.', 'Student ID', 'Student Name', 'Father Name', 'Academic Level',
                        'Program Code', 'Program Title', 'School', 'Student Groups', 'Fee Status']

        for i in range(10):
            worksheet.write(row, col, table_header[i], style=style_table_header2)
            col += 1

        dom = [('state', '=', 'enroll')]
        if self.institute_ids:
            dom.append(('institute_id', 'in', self.institute_ids.ids))
        if self.campus_ids:
            dom.append(('campus_id', 'in', self.campus_ids.ids))
        if self.career_ids:
            dom.append(('career_id', 'in', self.career_ids.ids))

        students = self.env['odoocms.student'].search(dom)
        sr = 1
        for student_id in students.with_progress(msg="Fee Generation Status Report"):
            student_groups = ''
            fee_status = False

            for tag in student_id.tag_ids:
                if tag.code:
                    student_groups = student_groups + tag.code + ", "

            last_fee_receipt = self.env['account.move'].search([('student_id', '=', student_id.id),
                                                                ('term_id', '=', self.term_id.id),
                                                                ('move_type', '=', 'out_invoice'),
                                                                ('reversed_entry_id', '=', False),
                                                                ('invoice_payment_state', '!=', 'cancel')])
            if last_fee_receipt:
                fee_status = True

            row += 1
            col = 0
            worksheet.write(row, col, sr, style=style_date_col)
            col += 1
            worksheet.write(row, col, student_id.id_number and student_id.id_number or '', style=style_date_col2)
            col += 1
            worksheet.write(row, col, student_id.name and student_id.name or '', style=style_date_col2)
            col += 1
            worksheet.write(row, col, student_id.father_name and student_id.father_name or '', style=style_date_col2)
            col += 1
            worksheet.write(row, col, student_id.career_id and student_id.career_id.code or '', style=style_date_col2)
            col += 1
            worksheet.write(row, col, student_id.program_id and student_id.program_id.code or '', style=style_date_col2)
            col += 1
            worksheet.write(row, col, student_id.program_id and student_id.program_id.name or '', style=style_date_col2)
            col += 1
            worksheet.write(row, col, student_id.institute_id and student_id.institute_id.name or '', style=style_date_col2)
            col += 1
            worksheet.write(row, col, student_groups, style=style_date_col2)
            col += 1
            if fee_status:
                worksheet.write(row, col, '✔', style=style_date_col2)
                col += 1
            if not fee_status:
                worksheet.write(row, col, '✖', style=style_date_col2)
                col += 1
            sr += 1

        file_data = io.BytesIO()
        workbook.save(file_data)
        wiz_id = self.env['odoocms.fee.report.save.wizard'].create({
            'data': base64.encodebytes(file_data.getvalue()),
            'name': 'Student Fee Generation Status Report.xls'
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Student Fee Generation Status Report',
            'res_model': 'odoocms.fee.report.save.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': wiz_id.id,
            'target': 'new'
        }
