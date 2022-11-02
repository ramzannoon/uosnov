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


class ScholarshipAwardeesReport(models.TransientModel):
    _name = 'scholarship.awardees.report'
    _description = 'Scholarship Awardees Report'

    report_type = fields.Selection([('waiver', 'Waivers'),
                                    ('scholarship', 'ScholarShip'),
                                    ('both', 'Both')
                                    ], default='scholarship', string='Report Type')

    def make_excel(self):
        workbook = xlwt.Workbook(encoding="utf-8")
        worksheet = workbook.add_sheet("Scholarship Awardees Report")
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
        col1.width = 256 * 40
        col2 = worksheet.col(2)
        col2.width = 256 * 35
        col3 = worksheet.col(3)
        col3.width = 256 * 25
        col4 = worksheet.col(4)
        col4.width = 256 * 25
        col5 = worksheet.col(5)
        col5.width = 256 * 25
        col6 = worksheet.col(6)
        col6.width = 256 * 35
        col7 = worksheet.col(7)
        col7.width = 256 * 35
        col8 = worksheet.col(8)
        col8.width = 256 * 35
        col9 = worksheet.col(9)
        col9.width = 256 * 15
        col10 = worksheet.col(10)
        col10.width = 256 * 15

        worksheet.write_merge(0, 1, 0, 9, 'Scholarship Awardees Report', style=style_table_header2)
        row = 2
        col = 0
        table_header = ['SR# No.', 'Name', 'Father Name', 'Regn No', 'NIC', 'Institution', 'Scholarship Name', 'Scholarship Group', 'Program', 'Year of Admission']
        for i in range(10):
            worksheet.write(row, col, table_header[i], style=style_table_header2)
            col += 1

        if not self.report_type=='both':
            scholarships = self.env['odoocms.fee.waiver'].search([('type', '=', self.report_type)])
        else:
            scholarships = self.env['odoocms.fee.waiver'].search([])

        sr = 1
        if scholarships:
            for scholarship in scholarships:
                students = self.env['odoocms.student'].search([('tag_ids', '=', scholarship.tag_id.id)])
                if students:
                    for student in students:
                        row += 1
                        col = 0
                        worksheet.write(row, col, sr, style=style_date_col)
                        col += 1
                        worksheet.write(row, col, student.name and student.name or '', style=style_date_col2)
                        col += 1
                        worksheet.write(row, col, student.father_name and student.father_name or '', style=style_date_col2)
                        col += 1
                        worksheet.write(row, col, student.id_number and student.id_number or '', style=style_date_col2)
                        col += 1
                        worksheet.write(row, col, student.cnic and student.cnic or '', style=style_date_col2)
                        col += 1
                        worksheet.write(row, col, student.campus_id and student.campus_id.name or '', style=style_date_col2)
                        col += 1
                        worksheet.write(row, col, scholarship.name, style=style_date_col2)
                        col += 1
                        worksheet.write(row, col, scholarship.waiver_type and scholarship.waiver_type.name or '', style=style_date_col2)
                        col += 1
                        worksheet.write(row, col, student.program_id and student.program_id.name or '', style=style_date_col2)
                        col += 1
                        worksheet.write(row, col, student.session_id and student.session_id.name or '', style=style_date_col2)
                        col += 1
                        sr += 1

        file_data = io.BytesIO()
        workbook.save(file_data)
        wiz_id = self.env['odoocms.fee.report.save.wizard'].create({
            'data': base64.encodebytes(file_data.getvalue()),
            'name': 'Scholarship Awardees Report.xls'
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Scholarship Awardees Report',
            'res_model': 'odoocms.fee.report.save.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': wiz_id.id,
            'target': 'new'
        }
