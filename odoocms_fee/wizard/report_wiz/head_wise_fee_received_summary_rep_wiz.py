import pdb
from odoo import api, fields, models, _, tools
from dateutil.relativedelta import relativedelta
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


class HeadWiseFeeReceivedSummaryRepWiz(models.TransientModel):
    _name = 'head.wise.fee.received.summary.rep.wiz'
    _description = 'Head Wise Fee Received Summary Report'

    date_from = fields.Date('From Date', default=fields.Date.today() + relativedelta(day=1))
    date_to = fields.Date('To Date', default=fields.Date.today())
    fee_head_id = fields.Many2one('odoocms.fee.head.merge', 'Fee Head')
    is_hostel_fee = fields.Boolean('Is Hostel Fee', default=False)

    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'head.wise.fee.received.summary.rep.wiz',
            'form': data
        }

        return self.env.ref('odoocms_fee.action_head_wise_fee_received_summary_report').with_context(landscape=False).report_action(self, data=datas, config=False)

    def make_excel(self):
        workbook = xlwt.Workbook(encoding="utf-8")
        worksheet = workbook.add_sheet("Head Wise Fee Received Summary Report")
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
            "font:height 200; font: name Liberation Sans,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour white;")
        style_table_totals2 = xlwt.easyxf(
            "font:height 200; font: name Liberation Sans, bold on,color black; align: horiz right;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour ivory;")
        style_table_totals3 = xlwt.easyxf(
            "font:height 200; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour ivory;")

        # col width
        col0 = worksheet.col(0)
        col0.width = 256 * 10
        col1 = worksheet.col(1)
        col1.width = 256 * 50
        col2 = worksheet.col(2)
        col2.width = 256 * 15
        col3 = worksheet.col(3)
        col3.width = 256 * 15

        worksheet.write_merge(0, 1, 0, 4, 'Head Wise Fee Received Summary Report', style=style_table_header2)
        worksheet.write_merge(2, 2, 0, 4, 'From ' + self.date_from.strftime('%d-%b-%Y') + " to " + self.date_to.strftime('%d-%b-%Y'), style=style_table_header2)

        row = 3
        col = 0
        table_header = ['SR# No.', 'School Name', 'School Code', 'Student Count', 'Amount']
        for i in range(5):
            worksheet.write(row, col, table_header[i], style=style_table_header)
            col += 1

        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'head.wise.fee.received.summary.rep.wiz',
            'form': data
        }
        dta = self.env['report.odoocms_fee.head_wise_fee_received_summary_report']._get_report_values(self, data=datas)
        if dta['res']:
            sr = 1
            for r in dta['res']:
                row += 1
                col = 0
                worksheet.write(row, col, sr, style=style_date_col2)
                col += 1
                worksheet.write(row, col, r['School'], style=style_date_col2)
                col += 1
                worksheet.write(row, col, r['institute_code'], style=style_date_col2)
                col += 1
                worksheet.write(row, col, r['student_count'], style=style_date_col2)
                col += 1
                worksheet.write(row, col, r['amount'], style=style_date_col)
                col += 1
                sr += 1

            row += 1
            col = 0
            worksheet.write(row, col, '', style=style_table_totals2)
            col += 1
            worksheet.write(row, col, '', style=style_table_totals2)
            col += 1
            worksheet.write(row, col, '', style=style_table_totals2)
            col += 1
            worksheet.write(row, col, '', style=style_table_totals2)
            col += 1
            worksheet.write(row, col, dta['total_amount'], style=style_table_totals2)
            col += 1

            row += 1
            col = 0
            ttime = fields.datetime.now() + relativedelta(hours=5)
            worksheet.write_merge(row, row, 0, 4, "Print Date: " + ttime.strftime("%d-%m-%Y %H:%M:%S"), style=style_table_totals3)
            col += 1

        file_data = io.BytesIO()
        workbook.save(file_data)
        wiz_id = self.env['odoocms.fee.report.save.wizard'].create({
            'data': base64.encodebytes(file_data.getvalue()),
            'name': 'Head Wise Fee Received Summary Report.xls'
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Head Wise Fee Received Summary Report',
            'res_model': 'odoocms.fee.report.save.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': wiz_id.id,
            'target': 'new'
        }
