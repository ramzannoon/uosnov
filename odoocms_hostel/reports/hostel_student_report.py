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


class HostelStudentReportExport(models.TransientModel):
    _name = 'odoocms.hostel.student.export.wizard'
    _description = 'Hostel Student  Export Wizard'

    hostel_id = fields.Many2one('odoocms.hostel', 'Hostel')

    def make_excel(self):
        workbook = xlwt.Workbook(encoding="utf-8")
        worksheet = workbook.add_sheet("Hostel Students")
        style_title = xlwt.easyxf(
            "font:height 300; font: name Liberation Sans, bold on,color black; align: horiz center;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour cyan_ega;")
        style_table_header = xlwt.easyxf(
            "font:height 200; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour cyan_ega;")
        style_table_header2 = xlwt.easyxf(
            "font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour silver_ega;alignment: wrap True;")
        style_table_totals = xlwt.easyxf(
            "font:height 150; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour cyan_ega;")
        style_date_col = xlwt.easyxf(
            "font:height 180; font: name Liberation Sans,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")
        style_product_header = xlwt.easyxf(
            "font:height 200; font: name Liberation Sans,bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour silver_ega;")
        style_table_totals2 = xlwt.easyxf(
            "font:height 200; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")
        style_clo_col1 = xlwt.easyxf(
            "font:height 180; font: name Liberation Sans,color black; align:horiz center;borders: left thin, right thin, top thin, bottom thin;")
        style_clo_col2 = xlwt.easyxf(
            "font:height 150; font: name Liberation Sans,color black; align:horiz center;borders: left thin, right thin, top thin, bottom thin;")
        style_clo_col_rotation = xlwt.easyxf(
            "font:height 160; font: name Liberation Sans,bold on,color black; align:rotation 90,horiz center,vertical center;borders: left thin, right thin, top thin, bottom thin;")
        style_clo_col_rotation1 = xlwt.easyxf(
            "font:height 150; font: name Liberation Sans,bold on,color black; align:rotation 90,horiz center;borders: left thin, right thin, top thin, bottom thin;")

        # col width
        col0 = worksheet.col(0)
        col0.width = 256 * 8
        col1 = worksheet.col(1)
        col1.width = 256 * 20
        col2 = worksheet.col(2)
        col2.width = 256 * 35
        col3 = worksheet.col(3)
        col3.width = 256 * 20
        col4 = worksheet.col(4)
        col4.width = 256 * 20
        col5 = worksheet.col(5)
        col5.width = 256 * 20
        col6 = worksheet.col(6)
        col6.width = 256 * 20
        col6 = worksheet.col(7)
        col6.width = 256 * 30

        ttime = fields.Datetime.now() + timedelta(hours=+5)

        worksheet.write_merge(0, 1, 0, 7, 'OFFICE OF STUDENT AFFAIRS (Hostel Student Report)', style=style_table_header2)
        row = 2
        col = 0

        table_header = ['SR# No.', 'Student Reg No', 'Student Name', 'Hostel No', 'Room No', 'Room Type', 'Room Capacity', 'Signature']
        for i in range(8):
            worksheet.write(row, col, table_header[i], style=style_table_header2)
            col += 1
        if self.hostel_id:
            students = self.env['odoocms.student'].search([('hostel_id', '=', self.hostel_id.id)], order="room_id asc")
        if not self.hostel_id:
            raise UserError('Please Select the Hostel to Take this Report.')

        sr = 1
        if students:
            for student in students:
                row += 1
                col = 0
                worksheet.write(row, col, sr, style=style_date_col)
                col += 1
                worksheet.write(row, col, student.id_number and student.id_number or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, student.name and student.name or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, student.hostel_id and student.hostel_id.name or '', style=style_date_col)
                col += 1
                # worksheet.write(row, col, student.room_id and student.room_id.name or '', style=style_date_col)
                worksheet.write(row, col, student.room_id.room_id and student.room_id.room_id.name or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, student.room_id.room_type and student.room_id.room_type.name or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, student.room_id.room_capacity and student.room_id.room_capacity or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, '', style=style_date_col)
                col += 1
                sr += 1

            row += 1
            col = 0
            worksheet.write(row, 0, '', style=style_table_header2)
            worksheet.write(row, 1, '', style=style_table_header2)
            worksheet.write(row, 2, '', style=style_table_header2)
            worksheet.write(row, 3, '', style=style_table_header2)
            worksheet.write(row, 4, '', style=style_table_header2)
            worksheet.write(row, 5, '', style=style_table_header2)
            worksheet.write(row, 6, '', style=style_table_header2)
            worksheet.write(row, 7, 'Date:-  ' + ttime.strftime('%d-%b-%Y %H:%M:%S'), style=style_table_header2)

        file_data = io.BytesIO()
        workbook.save(file_data)
        wiz_id = self.env['hostel.summary.report.save.wizard'].create({
            'data': base64.encodebytes(file_data.getvalue()),
            'name': 'Hostel Student.xls'
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Hostel Student',
            'res_model': 'hostel.summary.report.save.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': wiz_id.id,
            'target': 'new'
        }
