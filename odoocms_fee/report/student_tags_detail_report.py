import pdb
from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

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


class StudentTagsDetailReport(models.TransientModel):
    _name = 'student.tags.detail.report'
    _description = 'Student Tags Detail Report'

    state = fields.Selection([('draft', 'Draft'),
                              ('enroll', 'Admitted'),
                              ('alumni', 'Alumni'),
                              ('suspend', 'Suspend'),
                              ('struck', 'Struck Off'),
                              ('defer', 'Deferred'),
                              ('cancel', 'Cancel'),
                              ('all', 'All'),
                              ], 'Status', default='enroll')

    def make_excel(self):
        workbook = xlwt.Workbook(encoding="utf-8")
        worksheet = workbook.add_sheet("Student Tags Detail Report")
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
        col1.width = 256 * 20
        col2 = worksheet.col(2)
        col2.width = 256 * 30
        col3 = worksheet.col(3)
        col3.width = 256 * 20
        col4 = worksheet.col(4)
        col4.width = 256 * 20
        col5 = worksheet.col(5)
        col5.width = 256 * 20
        col6 = worksheet.col(6)
        col6.width = 256 * 20
        col7 = worksheet.col(7)
        col7.width = 256 * 35
        col8 = worksheet.col(8)
        col8.width = 256 * 20
        col9 = worksheet.col(9)
        col9.width = 256 * 20
        col10 = worksheet.col(10)
        col10.width = 256 * 50
        col11 = worksheet.col(11)
        col11.width = 256 * 20

        ttime = fields.datetime.now() + relativedelta(hours=5)

        worksheet.write_merge(0, 1, 0, 10, 'Student Tags Detail Report', style=style_table_header2)
        row = 2
        col = 0
        table_header = ['SR# No.', 'Code', 'Name', 'Gender', 'Status', 'Academic Session', 'Program', 'Campus', 'Academic Level', 'Semester', 'Tags']
        for i in range(11):
            worksheet.write(row, col, table_header[i], style=style_table_header2)
            col += 1

        if not self.state=='all':
            students = self.env['odoocms.student'].search([('state', '=', self.state)], order='campus_id')
        if self.state=='all':
            students = self.env['odoocms.student'].search([], order='campus_id')
        if students:
            sr = 1
            for student in students:
                tags = ''
                if student.tag_ids:
                    for tag in student.tag_ids:
                        if len(student.tag_ids)==1:
                            tags += tag.name
                        if len(student.tag_ids) > 1:
                            tags += tag.name + ","

                    gender = (dict(self.env['odoocms.student'].fields_get(allfields=['gender'])['gender']['selection'])[student.gender])
                    status = (dict(self.env['odoocms.student'].fields_get(allfields=['state'])['state']['selection'])[student.state])

                    row += 1
                    col = 0
                    worksheet.write(row, col, sr, style=style_date_col)
                    col += 1
                    worksheet.write(row, col, student.code, style=style_date_col2)
                    col += 1
                    worksheet.write(row, col, student.name, style=style_date_col2)
                    col += 1
                    worksheet.write(row, col, gender, style=style_date_col2)
                    col += 1
                    worksheet.write(row, col, status, style=style_date_col2)
                    col += 1
                    worksheet.write(row, col, student.session_id and student.session_id.name or '', style=style_date_col2)
                    col += 1
                    worksheet.write(row, col, student.campus_id and student.campus_id.name or '', style=style_date_col2)
                    col += 1
                    worksheet.write(row, col, student.program_id and student.program_id.name or '', style=style_date_col2)
                    col += 1
                    worksheet.write(row, col, student.career_id and student.career_id.name or '', style=style_date_col2)
                    col += 1
                    worksheet.write(row, col, student.semester_id and student.semester_id.name or '', style=style_date_col2)
                    col += 1
                    worksheet.write(row, col, tags, style=style_date_col2)
                    col += 1
                    sr += 1
            col = 0
            row += 2
            worksheet.write(row, col, 'User Name', style=style_date_col2)
            col += 1
            worksheet.write(row, col, self.env.user.name, style=style_date_col2)

            col = 0
            row += 1
            worksheet.write(row, col, 'Report Print Date:-', style=style_date_col2)
            col += 1
            worksheet.write(row, col, str(ttime), style=style_date_col2)
            col += 1

        file_data = io.BytesIO()
        workbook.save(file_data)
        wiz_id = self.env['odoocms.fee.report.save.wizard'].create({
            'data': base64.encodebytes(file_data.getvalue()),
            'name': 'Students Tags Detail Report.xls'
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Student Tags Detail Report',
            'res_model': 'odoocms.fee.report.save.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': wiz_id.id,
            'target': 'new'
        }
