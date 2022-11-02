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


class OdooCMSStudentsRoomSwapReport(models.TransientModel):
    _name = 'odoocms.students.room.swap.report'
    _description = 'Students Room Swapping Report'

    from_date = fields.Date('From Date', default=fields.Date.today())
    to_date = fields.Date('To Date', default=fields.Date.today())

    def make_excel(self):
        workbook = xlwt.Workbook(encoding="utf-8")
        worksheet = workbook.add_sheet("Students Room Swap Report")
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
        col6 = worksheet.col(7)
        col6.width = 256 * 18

        ttime = fields.Datetime.now() + timedelta(hours=+5)

        worksheet.write_merge(0, 1, 0, 7, 'Students Room Swap Report From ' + self.from_date.strftime('%d-%m-%Y') + "To " + self.to_date.strftime('%d-%m-%Y'), style=style_table_header2)
        row = 2
        col = 0

        table_header = ['SR# No.', 'Reg No', 'Student Name', 'Previous Hostel', 'New Hostel', 'Previous Room', 'New Room', 'Date']
        for i in range(8):
            worksheet.write(row, col, table_header[i], style=style_table_header2)
            col += 1

        recs = self.env['odoocms.student.hostel.history'].search([('allocate_date', '>=', self.from_date), ('allocate_date', '<=', self.to_date), ('request_type', '=', 'Swap')])

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
                worksheet.write(row, col, rec.previous_hostel_id and rec.previous_hostel_id.name or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.hostel_id and rec.hostel_id.name or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.previous_room_id and rec.previous_room_id.name or '', style=style_date_col)
                col += 1
                # worksheet.write(row, col, rec.room_id and rec.room_id.name or '', style=style_date_col)
                worksheet.write(row, col, rec.room_id.room_id and rec.room_id.room_id.name or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.allocate_date and rec.allocate_date.strftime('%d-%m-%Y'), style=style_date_col)
                col += 1
                sr += 1

        file_data = io.BytesIO()
        workbook.save(file_data)
        wiz_id = self.env['hostel.summary.report.save.wizard'].create({
            'data': base64.encodebytes(file_data.getvalue()),
            'name': 'Students Room Swap.xls'
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
