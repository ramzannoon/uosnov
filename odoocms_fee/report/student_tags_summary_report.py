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


class StudentTagsSummaryReport(models.TransientModel):
    _name = 'student.tags.summary.report'
    _description = 'Student Tags Summary Report'

    report_type = fields.Selection([('a', 'All Tags'),
                                    ('s', 'Scholarship Tags')], default='a', string='Report Type')

    def make_excel(self):
        workbook = xlwt.Workbook(encoding="utf-8")
        worksheet = workbook.add_sheet("Student Tags Summary Report")
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
        col1.width = 256 * 30
        col2 = worksheet.col(2)
        col2.width = 256 * 15

        worksheet.write_merge(0, 1, 0, 2, 'Student Tags Summary Report', style=style_table_header2)
        row = 2
        col = 0
        table_header = ['SR# No.', 'Tag', 'Count']
        for i in range(3):
            worksheet.write(row, col, table_header[i], style=style_table_header2)
            col += 1

        tags = self.env['odoocms.student.tag'].search([])
        if self.report_type=='s':
            tags_list = []
            tags2 = self.env['odoocms.fee.waiver'].read_group([('type', '=', 'scholarship')], ['tag_id'], groupby=['tag_id'])
            for tag2 in tags2:
                tags_list.append(tag2['tag_id'][0])
            tags = self.env['odoocms.student.tag'].search([('id', 'in', tags_list)])
        else:
            tags = self.env['odoocms.student.tag'].search([])
        sr = 1
        if tags:
            for tag in tags:
                students = self.env['odoocms.student'].search_count([('tag_ids', '=', tag.id)])
                if students:
                    row += 1
                    col = 0
                    worksheet.write(row, col, sr, style=style_date_col)
                    col += 1
                    worksheet.write(row, col, tag.name, style=style_date_col2)
                    col += 1
                    worksheet.write(row, col, students, style=style_date_col2)
                    col += 1
                    sr += 1

        file_data = io.BytesIO()
        workbook.save(file_data)
        wiz_id = self.env['odoocms.fee.report.save.wizard'].create({
            'data': base64.encodebytes(file_data.getvalue()),
            'name': 'Students Tags Summary Report.xls'
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Students Tags Summary Report',
            'res_model': 'odoocms.fee.report.save.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': wiz_id.id,
            'target': 'new'
        }
