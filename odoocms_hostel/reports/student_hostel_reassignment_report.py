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


class StudentHostelReassignmentReport(models.TransientModel):
    _name = 'student.hostel.reassignment.report'
    _description = 'Student Hostel Reassignment Report'

    @api.model
    def _get_reassignment_id(self):
        if self._context.get('active_model', False)=='odoocms.student.hostel.reassignment' and self._context.get('active_id', False):
            return self.env['odoocms.student.hostel.reassignment'].browse(self._context.get('active_id', False))

    reassignment_id = fields.Many2one('odoocms.student.hostel.reassignment', 'Reassignment Ref', default=_get_reassignment_id)

    def make_excel(self):
        workbook = xlwt.Workbook(encoding="utf-8")
        worksheet = workbook.add_sheet("Students Hostel Reassignment Report")
        style_title = xlwt.easyxf(
            "font:height 250; font: name Liberation Sans, bold on,color black; align: horiz center,vert centre;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour lime;")
        style_table_header = xlwt.easyxf(
            "font:height 190; font: name Liberation Sans, bold on,color black; align: horiz center,vert centre;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour silver_ega;")
        style_table_header2 = xlwt.easyxf(
            "font:height 190; font: name Liberation Sans, bold on,color white; align: horiz center;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour silver_ega;alignment: wrap True;")
        style_table_header3 = xlwt.easyxf(
            "font:height 190; font: name Liberation Sans, bold on,color white; align: horiz left;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour dark_purple; alignment: wrap True;")
        style_table_header4 = xlwt.easyxf(
            "font:height 190; font: name Liberation Sans, bold on,color white; align: horiz right;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour dark_purple; alignment: wrap True;")
        style_table_totals = xlwt.easyxf(
            "font:height 150; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour cyan_ega;")
        style_date_col = xlwt.easyxf(
            "font:height 180; font: name Liberation Sans,color black; align: horiz right;borders: left thin, right thin, top thin, bottom thin;")
        style_date_col2 = xlwt.easyxf(
            "font:height 180; font: name Liberation Sans,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")

        # col width
        col0 = worksheet.col(0)
        col0.width = 256 * 8
        col1 = worksheet.col(1)
        col1.width = 256 * 20
        col2 = worksheet.col(2)
        col2.width = 256 * 40
        col3 = worksheet.col(3)
        col3.width = 256 * 25
        col4 = worksheet.col(4)
        col4.width = 256 * 25
        col5 = worksheet.col(5)
        col5.width = 256 * 20
        col6 = worksheet.col(6)
        col6.width = 256 * 20
        col7 = worksheet.col(7)
        col7.width = 256 * 20
        col8 = worksheet.col(8)
        col8.width = 256 * 20
        col9 = worksheet.col(9)
        col9.width = 256 * 20
        col10 = worksheet.col(10)
        col10.width = 256 * 20
        col11 = worksheet.col(11)
        col11.width = 256 * 20

        ttime = fields.Datetime.now() + timedelta(hours=+5)
        worksheet.write_merge(0, 2, 0, 10, 'GHULAM ISHAQ KHAN INSTITUTE OF ENGINEERING SCIENCE & TECHNOLOGY TOPI', style=style_title)
        worksheet.write_merge(3, 4, 0, 10, 'Students Hostel Reassignment (' + self.reassignment_id.name + ") Report", style=style_table_header)
        row = 5
        col = 0
        worksheet.write_merge(5, 5, 0, 10, 'Date: ' + ttime.strftime('%d-%m-%Y %H:%M:%S'), style=style_date_col)

        row += 1
        table_header = ['SR# No.', 'Student Reg No', 'Student Name', 'Program', 'Academic Session', 'CGPA/Merit No', 'Hostel', 'Room', 'Room Type', 'Assignment Status', 'Type']
        for i in range(11):
            worksheet.write(row, col, table_header[i], style=style_table_header2)
            col += 1

        total = 0
        if self.reassignment_id and self.reassignment_id.line_ids:
            sr = 1
            for reassignment_line in self.reassignment_id.line_ids:
                row += 1
                col = 0
                worksheet.write(row, col, sr, style=style_date_col2)
                col += 1
                worksheet.write(row, col, reassignment_line.student_reg_no and reassignment_line.student_reg_no or '', style=style_date_col2)
                col += 1
                worksheet.write(row, col, reassignment_line.student_id and reassignment_line.student_id.name or '', style=style_date_col2)
                col += 1
                worksheet.write(row, col, reassignment_line.student_id.program_id and reassignment_line.student_id.program_id.name or '', style=style_date_col2)
                col += 1
                worksheet.write(row, col, reassignment_line.student_id.session_id and reassignment_line.student_id.session_id.name or '', style=style_date_col2)
                col += 1
                worksheet.write(row, col, (reassignment_line.cgpa and reassignment_line.cgpa) or (reassignment_line.merit_no and reassignment_line.merit_no) or '', style=style_date_col2)
                col += 1
                worksheet.write(row, col, reassignment_line.assigned_hostel_id and reassignment_line.assigned_hostel_id.name or '', style=style_date_col2)
                col += 1
                # worksheet.write(row, col, reassignment_line.assigned_room_id and reassignment_line.assigned_room_id.name or '', style=style_date_col2)
                worksheet.write(row, col, reassignment_line.assigned_room_id.room_id and reassignment_line.assigned_room_id.room_id.name or '', style=style_date_col2)
                col += 1
                worksheet.write(row, col, reassignment_line.assigned_room_type and reassignment_line.assigned_room_type.name or '', style=style_date_col2)
                col += 1
                worksheet.write(row, col, reassignment_line.assignment_status and reassignment_line.assignment_status or '', style=style_date_col2)
                col += 1
                worksheet.write(row, col, reassignment_line.type, style=style_date_col2)
                col += 1
                sr += 1

        row += 1
        col = 0
        worksheet.write(row, col, '', style=style_table_header3)
        col += 1
        worksheet.write(row, col, '', style=style_table_header3)
        col += 1
        worksheet.write(row, col, '', style=style_table_header3)
        col += 1
        worksheet.write(row, col, '', style=style_table_header3)
        col += 1
        worksheet.write(row, col, '', style=style_table_header3)
        col += 1
        worksheet.write(row, col, '', style=style_table_header3)
        col += 1
        worksheet.write(row, col, '', style=style_table_header3)
        col += 1
        worksheet.write(row, col, '', style=style_table_header3)
        col += 1
        worksheet.write(row, col, '', style=style_table_header4)
        col += 1
        worksheet.write(row, col, '', style=style_table_header4)
        col += 1
        worksheet.write(row, col, '', style=style_table_header4)
        col += 1

        file_data = io.BytesIO()
        workbook.save(file_data)
        wiz_id = self.env['hostel.summary.report.save.wizard'].create({
            'data': base64.encodebytes(file_data.getvalue()),
            'name': 'Students Hostel Reassignment Report.xls'
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Students Hostel Reassignment Report',
            'res_model': 'hostel.summary.report.save.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': wiz_id.id,
            'target': 'new'
        }
