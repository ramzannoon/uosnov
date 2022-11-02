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


class HostelSummaryExport(models.TransientModel):
    _name = 'odoocms.hostel.export.wizard'
    _description = 'Hostel Summary Export Wizard'

    def make_excel(self):
        workbook = xlwt.Workbook(encoding="utf-8")
        worksheet = workbook.add_sheet("Hostel Summary")
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
        col1 = worksheet.col(1)
        col1.width = 256 * 35

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

        worksheet.write_merge(0, 1, 0, 21, 'Hostels Summary Report', style=style_table_header2)
        row = 2
        col = 0

        worksheet.write_merge(row, row + 1, 0, 0, "", style=style_table_header)
        worksheet.write_merge(row, row + 1, 1, 1, "", style=style_table_header)
        worksheet.write_merge(row, row + 1, 2, 5, "Single Occupancy Rooms", style=style_table_header)
        worksheet.write_merge(row, row, 6, 13, "Double Occupancy Rooms", style=style_table_header)
        worksheet.write_merge(row, row, 14, 17, "Triple Occupancy Rooms", style=style_table_header)
        worksheet.write_merge(row, row + 1, 18, 21, "Totals", style=style_table_header)
        row += 1

        worksheet.write_merge(row, row, 6, 9, "With Attached Bath", style=style_table_header)
        worksheet.write_merge(row, row, 10, 13, "With Community Bath", style=style_table_header)
        worksheet.write_merge(row, row, 14, 17, "With Community Bath", style=style_table_header)
        row += 1

        worksheet.write(row, 0, "Serial No.", style=style_table_header3)
        worksheet.write(row, 1, "Hostel Name", style=style_table_header3)
        worksheet.write(row, 2, "Rooms", style=style_table_header3)
        worksheet.write(row, 3, "Occupancy", style=style_table_header3)
        worksheet.write(row, 4, "Occupied", style=style_table_header3)
        worksheet.write(row, 5, "Vacant", style=style_table_header3)

        worksheet.write(row, 6, "Rooms", style=style_table_header3)
        worksheet.write(row, 7, "Occupancy", style=style_table_header3)
        worksheet.write(row, 8, "Occupied", style=style_table_header3)
        worksheet.write(row, 9, "Vacant", style=style_table_header3)

        worksheet.write(row, 10, "Rooms", style=style_table_header3)
        worksheet.write(row, 11, "Occupancy", style=style_table_header3)
        worksheet.write(row, 12, "Occupied", style=style_table_header3)
        worksheet.write(row, 13, "Vacant", style=style_table_header3)

        worksheet.write(row, 14, "Rooms", style=style_table_header3)
        worksheet.write(row, 15, "Occupancy", style=style_table_header3)
        worksheet.write(row, 16, "Occupied", style=style_table_header3)
        worksheet.write(row, 17, "Vacant", style=style_table_header3)

        worksheet.write(row, 18, "Rooms", style=style_table_header3)
        worksheet.write(row, 19, "Total Beds", style=style_table_header3)
        worksheet.write(row, 20, "Occupied Beds", style=style_table_header3)
        worksheet.write(row, 21, "Vacant Beds", style=style_table_header3)

        hostel_recs = self.env['odoocms.hostel'].sudo().search([])
        sr = 1

        total_cubicle_occupancy = 0
        total_cubicle_vacant = 0
        total_cubicle_occupied = 0

        total_bi_seater_wab_occupancy = 0
        total_bi_seater_wab_vacant = 0
        total_bi_seater_wab_occupied = 0

        total_bi_seater_wcb_occupancy = 0
        total_bi_seater_wcb_vacant = 0
        total_bi_seater_wcb_occupied = 0

        total_tri_seater_wcb_occupancy = 0
        total_tri_seater_wcb_vacant = 0
        total_tri_seater_wcb_occupied = 0

        total_bed_occupancy = 0
        total_occupied_beds = 0
        total_vacant_beds = 0
        total_c_rooms = 0
        total_bi_wab_rooms = 0
        total_bi_wcb_rooms = 0
        total_tri_wcb_rooms = 0
        total_rooms = 0

        for hostel_rec in hostel_recs:
            hostel_total_bed_occupancy = 0
            hostel_total_occupied_beds = 0
            hostel_total_vacant_beds = 0
            hostel_total_rooms = 0

            row += 1
            col = 0
            # Cubicle Rooms
            cubicle_occupancy = 0
            cubicle_vacant = 0
            cubicle_occupied = 0
            cubicle_rooms_total = 0

            cubicle_rooms = hostel_rec.hostel_rooms.filtered(lambda l: l.room_type.name=='Single Occupancy With Attached Bath')
            for cubicle_room in cubicle_rooms:
                cubicle_rooms_total += 1
                cubicle_occupancy += int(cubicle_room.room_capacity)
                cubicle_vacant += int(cubicle_room.vacancy)
                cubicle_occupied += int(cubicle_room.allocated_number)

            worksheet.write(row, col, sr, style=style_date_col2)
            col += 1
            worksheet.write(row, col, hostel_rec.name, style=style_date_col2)
            col += 1
            worksheet.write(row, col, cubicle_rooms_total, style=style_date_col)
            col += 1
            worksheet.write(row, col, cubicle_occupancy, style=style_date_col)
            col += 1
            worksheet.write(row, col, cubicle_occupied, style=style_date_col)
            col += 1
            worksheet.write(row, col, cubicle_vacant, style=style_date_col)
            col += 1
            total_cubicle_occupancy += cubicle_occupancy
            total_cubicle_vacant += cubicle_vacant
            total_cubicle_occupied += cubicle_occupied
            total_c_rooms += cubicle_rooms_total

            # For Bi-Seater With Attached Bath Rooms
            bi_seater_wab_occupancy = 0
            bi_seater_wab_vacant = 0
            bi_seater_wab_occupied = 0
            bi_seater_wab_room_total = 0

            bi_seater_wab_rooms = hostel_rec.hostel_rooms.filtered(lambda l: l.room_type.name=='Double Occupancy With Attached Bath')
            for bi_seater_wab_room in bi_seater_wab_rooms:
                bi_seater_wab_room_total += 1
                bi_seater_wab_occupancy += int(bi_seater_wab_room.room_capacity)
                bi_seater_wab_vacant += int(bi_seater_wab_room.vacancy)
                bi_seater_wab_occupied += int(bi_seater_wab_room.allocated_number)

            worksheet.write(row, col, bi_seater_wab_room_total, style=style_date_col)
            col += 1
            worksheet.write(row, col, bi_seater_wab_occupancy, style=style_date_col)
            col += 1
            worksheet.write(row, col, bi_seater_wab_occupied, style=style_date_col)
            col += 1
            worksheet.write(row, col, bi_seater_wab_vacant, style=style_date_col)
            col += 1
            total_bi_seater_wab_occupancy += bi_seater_wab_occupancy
            total_bi_seater_wab_vacant += bi_seater_wab_vacant
            total_bi_seater_wab_occupied += bi_seater_wab_occupied
            total_bi_wab_rooms += bi_seater_wab_room_total

            # For Bi-Seater With Community Bath Rooms
            bi_seater_wcb_occupancy = 0
            bi_seater_wcb_vacant = 0
            bi_seater_wcb_occupied = 0
            bi_seater_wcb_room_total = 0

            bi_seater_wcb_rooms = hostel_rec.hostel_rooms.filtered(lambda l: l.room_type.name=='Double Occupancy With Community Bath')
            for bi_seater_wcb_room in bi_seater_wcb_rooms:
                bi_seater_wcb_room_total += 1
                bi_seater_wcb_occupancy += int(bi_seater_wcb_room.room_capacity)
                bi_seater_wcb_vacant += int(bi_seater_wcb_room.vacancy)
                bi_seater_wcb_occupied += int(bi_seater_wcb_room.allocated_number)
            worksheet.write(row, col, bi_seater_wcb_room_total, style=style_date_col)
            col += 1
            worksheet.write(row, col, bi_seater_wcb_occupancy, style=style_date_col)
            col += 1
            worksheet.write(row, col, bi_seater_wcb_occupied, style=style_date_col)
            col += 1
            worksheet.write(row, col, bi_seater_wcb_vacant, style=style_date_col)
            col += 1
            total_bi_seater_wcb_occupancy += bi_seater_wcb_occupancy
            total_bi_seater_wcb_vacant += bi_seater_wcb_vacant
            total_bi_seater_wcb_occupied += bi_seater_wcb_occupied
            total_bi_wcb_rooms += bi_seater_wcb_room_total

            # For Tri-Seater With Community Bath Rooms
            tri_seater_wcb_occupancy = 0
            tri_seater_wcb_vacant = 0
            tri_seater_wcb_occupied = 0
            tri_seater_wcb_room_total = 0
            tri_seater_wcb_rooms = hostel_rec.hostel_rooms.filtered(lambda l: l.room_type.name=='Triple Occupancy With Community Bath')
            for tri_seater_wcb_room in tri_seater_wcb_rooms:
                tri_seater_wcb_room_total += 1
                tri_seater_wcb_occupancy += int(tri_seater_wcb_room.room_capacity)
                tri_seater_wcb_vacant += int(tri_seater_wcb_room.vacancy)
                tri_seater_wcb_occupied += int(tri_seater_wcb_room.allocated_number)
            worksheet.write(row, col, tri_seater_wcb_room_total, style=style_date_col)
            col += 1
            worksheet.write(row, col, tri_seater_wcb_occupancy, style=style_date_col)
            col += 1
            worksheet.write(row, col, tri_seater_wcb_occupied, style=style_date_col)
            col += 1
            worksheet.write(row, col, tri_seater_wcb_vacant, style=style_date_col)
            col += 1
            total_tri_seater_wcb_occupancy += tri_seater_wcb_occupancy
            total_tri_seater_wcb_vacant += tri_seater_wcb_vacant
            total_tri_seater_wcb_occupied += tri_seater_wcb_occupied
            total_tri_wcb_rooms += tri_seater_wcb_room_total

            hostel_total_bed_occupancy = cubicle_occupancy + bi_seater_wab_occupancy + bi_seater_wcb_occupancy + tri_seater_wcb_occupancy
            hostel_total_occupied_beds = cubicle_occupied + bi_seater_wab_occupied + bi_seater_wcb_occupied + tri_seater_wcb_occupied
            hostel_total_vacant_beds = cubicle_vacant + bi_seater_wab_vacant + bi_seater_wcb_vacant + tri_seater_wcb_vacant
            hostel_total_rooms = cubicle_rooms_total + bi_seater_wab_room_total + bi_seater_wcb_room_total + tri_seater_wcb_room_total

            total_bed_occupancy += hostel_total_bed_occupancy
            total_occupied_beds += hostel_total_occupied_beds
            total_vacant_beds += hostel_total_vacant_beds
            total_rooms += hostel_total_rooms

            worksheet.write(row, col, hostel_total_rooms, style=style_date_col)
            col += 1
            worksheet.write(row, col, hostel_total_bed_occupancy, style=style_date_col)
            col += 1
            worksheet.write(row, col, hostel_total_occupied_beds, style=style_date_col)
            col += 1
            worksheet.write(row, col, hostel_total_vacant_beds, style=style_date_col)
            col += 1
            sr += 1

        row += 1
        col = 0
        worksheet.write(row, col, '', style=style_table_totals2)
        col += 1
        worksheet.write(row, col, '', style=style_table_totals2)
        col += 1
        worksheet.write(row, col, total_c_rooms, style=style_table_totals2)
        col += 1
        worksheet.write(row, col, total_cubicle_occupancy, style=style_table_totals2)
        col += 1
        worksheet.write(row, col, total_cubicle_occupied, style=style_table_totals2)
        col += 1
        worksheet.write(row, col, total_cubicle_vacant, style=style_table_totals2)
        col += 1

        worksheet.write(row, col, total_bi_wab_rooms, style=style_table_totals2)
        col += 1
        worksheet.write(row, col, total_bi_seater_wab_occupancy, style=style_table_totals2)
        col += 1
        worksheet.write(row, col, total_bi_seater_wab_occupied, style=style_table_totals2)
        col += 1
        worksheet.write(row, col, total_bi_seater_wab_vacant, style=style_table_totals2)
        col += 1

        worksheet.write(row, col, total_bi_wcb_rooms, style=style_table_totals2)
        col += 1
        worksheet.write(row, col, total_bi_seater_wcb_occupancy, style=style_table_totals2)
        col += 1
        worksheet.write(row, col, total_bi_seater_wcb_occupied, style=style_table_totals2)
        col += 1
        worksheet.write(row, col, total_bi_seater_wcb_vacant, style=style_table_totals2)
        col += 1

        worksheet.write(row, col, total_tri_wcb_rooms, style=style_table_totals2)
        col += 1
        worksheet.write(row, col, total_tri_seater_wcb_occupancy, style=style_table_totals2)
        col += 1
        worksheet.write(row, col, total_tri_seater_wcb_occupied, style=style_table_totals2)
        col += 1
        worksheet.write(row, col, total_tri_seater_wcb_vacant, style=style_table_totals2)
        col += 1

        worksheet.write(row, col, total_rooms, style=style_table_totals2)
        col += 1
        worksheet.write(row, col, total_bed_occupancy, style=style_table_totals2)
        col += 1
        worksheet.write(row, col, total_occupied_beds, style=style_table_totals2)
        col += 1
        worksheet.write(row, col, total_vacant_beds, style=style_table_totals2)
        col += 1

        file_data = io.BytesIO()
        workbook.save(file_data)
        wiz_id = self.env['hostel.summary.report.save.wizard'].create({
            'data': base64.encodebytes(file_data.getvalue()),
            'name': 'Hostel Summary.xls'
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Hostel Summary',
            'res_model': 'hostel.summary.report.save.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': wiz_id.id,
            'target': 'new'
        }


class HostelSummaryReportSaveWizard(models.TransientModel):
    _name = "hostel.summary.report.save.wizard"
    _description = 'Hostel Summary Report Wizard'

    name = fields.Char('filename', readonly=True)
    data = fields.Binary('file', readonly=True)
