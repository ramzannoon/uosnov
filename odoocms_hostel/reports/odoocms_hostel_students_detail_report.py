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


class OdooCMSHostelStudentsDetailReport(models.TransientModel):
    _name = 'odoocms.hostel.students.detail.report'
    _description = 'Students Room Shift Report'

    hostel_id = fields.Many2one('odoocms.hostel', 'Hostel')
    all_hostel = fields.Boolean('All Hostel', default=False, )

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
        col21 = worksheet.col(21)
        col21.width = 256 * 20
        col22 = worksheet.col(22)
        col22.width = 256 * 20
        col23 = worksheet.col(23)
        col23.width = 256 * 20
        col24 = worksheet.col(24)
        col24.width = 256 * 20
        col25 = worksheet.col(25)
        col25.width = 256 * 20
        col26 = worksheet.col(26)
        col26.width = 256 * 20
        col27 = worksheet.col(27)
        col27.width = 256 * 35
        col28 = worksheet.col(28)
        col28.width = 256 * 35
        col29 = worksheet.col(29)
        col29.width = 256 * 20
        col30 = worksheet.col(30)
        col30.width = 256 * 20
        col31 = worksheet.col(31)
        col31.width = 256 * 20
        col32 = worksheet.col(32)
        col32.width = 256 * 20
        col33 = worksheet.col(33)
        col33.width = 256 * 20
        col34 = worksheet.col(34)
        col34.width = 256 * 20
        col35 = worksheet.col(35)
        col35.width = 256 * 20

        ttime = fields.Datetime.now() + timedelta(hours=+5)
        worksheet.write_merge(0, 1, 0, 33, 'Hostel Students Detail Report', style=style_table_header2)
        row = 2
        col = 0

        table_header = [
            'SR# No.',
            'CMS ID',
            'Student Name',
            'Student CNIC',
            'Student Email',
            'Student Mobile',
            'Father Name',
            'Father Income',
            'Guardian Name',
            'Father Profession',
            'Birth Date',
            'Domicile',
            'Merit No',
            'Gender',
            'Session',
            'Career',
            'School',
            'Program',
            'Term',
            'Discipline',
            'Campus',
            'Semester',
            'Orphan',
            'Shaheed',
            'Any Medical History',
            'Disability History',
            'Blood Group',
            'Any Psychiatrists Problem',
            'Permanent Address',
            'Temporary Address',
            'Hostel',
            'Room No',
            'Room Type',
            'Allocated Date'
        ]
        for i in range(34):
            worksheet.write(row, col, table_header[i], style=style_table_header2)
            col += 1
        if not self.all_hostel:
            recs = self.env['odoocms.student'].search([('hostel_id', '=', self.hostel_id.id),
                                                       ('hostel_state', '=', 'Allocated')])
        if self.all_hostel:
            recs = self.env['odoocms.student'].search([('hostel_state', '=', 'Allocated')], order='hostel_id')

        sr = 1
        if recs:
            for rec in recs:
                p_address = ''
                t_address = ''

                # Permanent Address
                if rec.street:
                    p_address = p_address + rec.street
                if rec.street2:
                    p_address = p_address + " " + rec.street2
                if rec.city:
                    p_address = p_address + " " + rec.city
                if rec.country_id:
                    p_address = p_address + rec.country_id.name

                # Temporary Address
                if rec.per_street:
                    t_address = t_address + rec.per_street
                if rec.per_street2:
                    t_address = t_address + " " + rec.per_street2
                if rec.city:
                    t_address = t_address + " " + rec.per_city
                if rec.per_country_id:
                    t_address = t_address + rec.per_country_id.name

                row += 1
                col = 0
                worksheet.write(row, col, sr, style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.code, style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.name, style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.cnic, style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.email, style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.mobile and rec.mobile or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.father_name, style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.father_income, style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.guardian_name and rec.guardian_name or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.father_profession and rec.father_profession.name or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.date_of_birth and rec.date_of_birth.strftime("%d-%m-%Y") or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.domicile_id and rec.domicile_id.name or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.merit_no, style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.gender, style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.session_id and rec.session_id.name or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.career_id and rec.career_id.code or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.institute_id and rec.institute_id.code or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.program_id and rec.program_id.name or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.term_id and rec.term_id.name or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.discipline_id and rec.discipline_id.name or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.campus_id and rec.campus_id.name or '', style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.semester_id and rec.semester_id.name or '', style=style_date_col)
                col += 1

                # Orphan
                worksheet.write(row, col, '', style=style_date_col)
                col += 1
                # Shaheed
                worksheet.write(row, col, '', style=style_date_col)
                col += 1
                # Any Medical History
                worksheet.write(row, col, '', style=style_date_col)
                col += 1
                # Disability History
                worksheet.write(row, col, rec.disability and rec.disability or '', style=style_date_col)
                col += 1
                # Blood Group
                worksheet.write(row, col, rec.blood_group, style=style_date_col)
                col += 1
                # Any Psychiatrists Problem
                worksheet.write(row, col, '', style=style_date_col)
                col += 1

                worksheet.write(row, col, p_address, style=style_date_col)
                col += 1
                worksheet.write(row, col, t_address, style=style_date_col)
                col += 1

                worksheet.write(row, col, rec.hostel_id.name, style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.room_id.room_id.room_no, style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.room_type.name, style=style_date_col)
                col += 1
                worksheet.write(row, col, rec.allocated_date and rec.allocated_date.strftime('%d-%m-%Y'), style=style_date_col)
                col += 1
                sr += 1

        file_data = io.BytesIO()
        workbook.save(file_data)
        wiz_id = self.env['hostel.summary.report.save.wizard'].create({
            'data': base64.encodebytes(file_data.getvalue()),
            'name': 'Students Detail Report.xls'
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Hostel Students Detail Report',
            'res_model': 'hostel.summary.report.save.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': wiz_id.id,
            'target': 'new'
        }
