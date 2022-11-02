# -*- coding: utf-8 -*-
from odoo import models
from urllib.request import urlopen
import io
import os
from datetime import datetime

dirname = os.path.dirname(__file__)


class BatchPayslipXlsx(models.TransientModel):
    _name = 'report.purchase_history_report.purchase_history_report_id'
    _description = 'Batch Payslip Xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, input_records, data):

        company = self.env.company

        main_heading = workbook.add_format({
            "bold": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'black',
            'font_size': '11',
            'num_format': '#,##0.00',
        })
        main_heading2 = workbook.add_format({
            "bold": 1,
            "left": 1,
            "right": 1,
            "top": 1,
            "bottom": 2,
            "bg_color": '#8EA9DB',
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'black',
            'font_size': '11',
            'num_format': '#,##0.00',
        })
        merge_format = workbook.add_format({
            'bold': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': '11',
            "font_color": 'black',
            'num_format': '#,##0.00',
        })
        main_data = workbook.add_format({
            "align": 'center',
            "valign": 'vcenter',
            'font_size': '11',
            'num_format': '#,##0.00',
        })
        data_right_bold = workbook.add_format({
            "bold": 1,
            "align": 'right',
            "valign": 'vcenter',
            'font_size': '11',
        })
        date_format = workbook.add_format({
            'num_format': 'dd/mm/yy',
            'align': 'center',
            "valign": 'vcenter',
            'font_size': '11',
        })

        merge_format.set_shrink()
        main_heading.set_text_justlast(1)
        worksheet = workbook.add_worksheet('Purchase History Report')

        # CompanyLogo
        worksheet.merge_range('A1:A6', " ")

        # Image get from company logo
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = web_base_url + '/logo.png?company=%d' % company.id
        image_data = io.BytesIO(urlopen(url).read())
        worksheet.insert_image('A1:B5', url,
                               {'image_data': image_data, 'x_scale': 1.2, 'y_scale': 0.8, "align": 'center'})

        worksheet.merge_range('B1:F2', company.name, merge_format)
        worksheet.write_string('G1', "Report Date: ", data_right_bold)
        worksheet.write_string('H1', str(datetime.now().date()), date_format)
        worksheet.merge_range('B4:F5', "Purchase History Report", merge_format)
        worksheet.merge_range('B7:F7', str(data.name), merge_format)

        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:C', 25)
        worksheet.set_column('D:D', 40)
        worksheet.set_column('E:H', 15)
        row = 8

        worksheet.write_string(row, 0, "Order Number", main_heading2)
        worksheet.write_string(row, 1, "Description", main_heading2)
        worksheet.write_string(row, 2, "Vendor", main_heading2)
        worksheet.write_string(row, 3, "Product", main_heading2)
        worksheet.write_string(row, 4, "Unit Price", main_heading2)
        worksheet.write_string(row, 5, "Quantity", main_heading2)
        worksheet.write_string(row, 6, "Subtotal", main_heading2)
        worksheet.write_string(row, 7, "Scheduled Date", main_heading2)
        row += 1
        for line in data.purchase_line_ids:
            worksheet.write(row, 0, line.order_id.name, main_data)
            worksheet.write(row, 1, line.name, main_data)
            worksheet.write(row, 2, line.partner_id.name, main_data)
            worksheet.write(row, 3, line.product_id.name, main_data)
            worksheet.write(row, 4, line.price_unit, main_data)
            worksheet.write(row, 5, line.product_qty, main_data)
            worksheet.write(row, 6, line.price_subtotal, main_data)
            worksheet.write(row, 7, line.date_planned, date_format)
            row += 1
        row += 1

        worksheet.write_string(row, 0,  "Printed By: ", data_right_bold)
        worksheet.write_string(row, 1,  str(self.env.user.name), main_data)
