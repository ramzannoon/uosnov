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


class OdooCMSStudentsRoomShiftReport(models.TransientModel):
    _name = 'odoocms.students.room.shift.report'
    _description = 'Students Room Shift Report'

    from_date = fields.Date('From Date', default=fields.Date.today() + relativedelta(day=1))
    to_date = fields.Date('To Date', default=fields.Date.today())

    def make_excel(self):
        workbook = xlwt.Workbook(encoding="utf-8")
        worksheet = workbook.add_sheet("Students Room Shift Report")
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
        col6.width = 256 * 15
        col7 = worksheet.col(7)
        col7.width = 256 * 20
        col8 = worksheet.col(8)
        col8.width = 256 * 35
        col9 = worksheet.col(9)
        col9.width = 256 * 20
        col10 = worksheet.col(10)
        col10.width = 256 * 20
        col11 = worksheet.col(11)
        col11.width = 256 * 35
        col12 = worksheet.col(12)
        col12.width = 256 * 20
        col13 = worksheet.col(13)
        col13.width = 256 * 20
        col14 = worksheet.col(14)
        col14.width = 256 * 20
        col15 = worksheet.col(15)
        col15.width = 256 * 20

        ttime = fields.Datetime.now() + timedelta(hours=+5)

        worksheet.write_merge(0, 1, 0, 13, 'Students Room Shift Report From ' + self.from_date.strftime('%d-%m-%Y') + "To " + self.to_date.strftime('%d-%m-%Y'), style=style_table_header2)
        row = 2
        col = 0

        worksheet.write_merge(row, row + 1, col, col, 'SR# No', style=style_table_header2)
        col += 1
        worksheet.write_merge(row, row + 1, col, col, 'CMS ID', style=style_table_header2)
        col += 1
        worksheet.write_merge(row, row + 1, col, col, 'Student Name', style=style_table_header2)
        col += 1
        worksheet.write_merge(row, row + 1, col, col, 'Father Name', style=style_table_header2)
        col += 1
        worksheet.write_merge(row, row + 1, col, col, 'School', style=style_table_header2)
        col += 1
        worksheet.write_merge(row, row + 1, col, col, 'Academic Level', style=style_table_header2)
        col += 1
        worksheet.write_merge(row, row, col, col + 2, 'Shifted From', style=style_table_header2)
        col += 3
        worksheet.write_merge(row, row, col, col + 2, 'Shifted To', style=style_table_header2)
        col += 3
        worksheet.write_merge(row, row + 1, col, col, 'Date', style=style_table_header2)
        col += 1
        worksheet.write_merge(row, row + 1, col, col, 'Remarks', style=style_table_header2)
        col += 1

        row = 3
        col = 6
        worksheet.write(row, col, 'Hostel', style=style_table_header2)
        col += 1
        worksheet.write(row, col, 'Room No', style=style_table_header2)
        col += 1
        worksheet.write(row, col, 'Room Type', style=style_table_header2)
        col += 1
        worksheet.write(row, col, 'Hostel', style=style_table_header2)
        col += 1
        worksheet.write(row, col, 'Room No', style=style_table_header2)
        col += 1
        worksheet.write(row, col, 'Room Type', style=style_table_header2)
        col += 1

        recs = self.env['odoocms.student.hostel.history'].search([('allocate_date', '>=', self.from_date),
                                                                  ('allocate_date', '<=', self.to_date),
                                                                  ('request_type', '=', 'Shift')])

        sr = 1
        if recs:
            for rec in recs:
                row += 1
                col = 0
                worksheet.write(row, col, sr, style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.student_code and rec.student_code or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.student_id.name and rec.student_id.name or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.student_id.father_name and rec.student_id.father_name or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.student_id.institute_id and rec.student_id.institute_id.code or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.student_id.career_id and rec.student_id.career_id.code or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.previous_hostel_id and rec.previous_hostel_id.name or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.previous_room_id and rec.previous_room_id.name or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.previous_room_id.room_type and rec.previous_room_id.room_type.name or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.hostel_id and rec.hostel_id.name or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.room_id.room_id and rec.room_id.room_id.name or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.room_id.room_type and rec.room_id.room_type.name or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.allocate_date and rec.allocate_date.strftime('%d-%m-%Y'), style=style_date_col)
                col += 1
                worksheet.write(row, col, '', style=style_date_col)
                col += 1
                sr += 1

        file_data = io.BytesIO()
        workbook.save(file_data)
        wiz_id = self.env['hostel.summary.report.save.wizard'].create({
            'data': base64.encodebytes(file_data.getvalue()),
            'name': 'Students Room Shift.xls'
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Hostel Shift Student',
            'res_model': 'hostel.summary.report.save.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': wiz_id.id,
            'target': 'new'
        }
