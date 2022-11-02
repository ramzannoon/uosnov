# -*- coding:utf-8 -*-
########################################################################################

#           Create Excel Report for Sales Order Validation Wizard                      #

########################################################################################
from odoo import api, models, fields
from urllib.request import urlopen
import io
import datetime
import os

dirname = os.path.dirname(__file__)


class SaleOrderValidationXlsx(models.AbstractModel):
    _name = 'report.sales_order_validation_report.s_o_valid_s_xls_temp_id'
    _description = 'Sales Order Validation Xlsx Reports'
    _inherit = 'report.report_xlsx.abstract'

    @api.model
    def generate_xlsx_report(self, workbook, data, partners):
        self.model = self.env.context.get('active_model')
        record_wizard = self.env[self.model].browse(self.env.context.get('active_id'))

        # Basic Info
        date_from = record_wizard.date_from
        date_to = record_wizard.date_to
        with_detail = record_wizard.with_detail
        user = self.env.user
        company = self.env.company
        current_date = datetime.date.today()

        sale_order_record = self.env['sale.order'].search([('date_order', '>=', date_from),
                                                           ('date_order', '<=', date_to)])

        # Create Designs
        company_header_title = workbook.add_format({
            'bold': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': '16',
        })
        header_title1 = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            "font_size": '11',
        })
        header_title = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            "font_size": '11',
        })
        date_format = workbook.add_format({
            'num_format': 'dd/mm/yy',
            'align': 'left',
            "valign": 'vcenter',
            'font_size': '11',
        })
        header_format1 = workbook.add_format({
            'bold': 1,
            "font_size": '11',
            'top': 2,
            'left': 1,
            'right': 1,
            'bottom': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#8EA9DB'
        })
        header_format = workbook.add_format({
            'bold': 1,
            "font_size": '11',
            'top': 1,
            'left': 1,
            'right': 1,
            'bottom': 2,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#8EA9DB'
        })
        data = workbook.add_format({
            "align": 'left',
            "valign": 'vcenter',
            'font_size': '11',
            'left': 1,
            'right': 1,
            "border_color": "#ABABAB"
        })
        amount_right = workbook.add_format({
            "align": 'right',
            "valign": 'vcenter',
            'font_size': '11',
            "num_format": "#,##0.00",
            'left': 1,
            'right': 1,
            "border_color": "#ABABAB"
        })
        line_total = workbook.add_format({
            "align": 'right',
            "valign": 'vcenter',
            'font_size': '11',
            "num_format": "#,##0.00",
            'bold': 1,
            'top': 1,
            'bottom': 2,
        })
        line_total_heading_bold = workbook.add_format({
            'bold': 1,
            "align": 'center',
            "valign": 'vcenter',
            'font_size': '11',
        })
        if with_detail:

            # Add Worksheet
            worksheet = workbook.add_worksheet("SO Validation Detailed")
            # Sale
            worksheet.set_column('A:A', 12)
            worksheet.set_column('B:B', 25)
            worksheet.set_column('C:C', 8)
            worksheet.set_column('D:D', 20)
            worksheet.set_column('E:E', 10)
            worksheet.set_column('F:F', 15)
            worksheet.set_column('G:G', 23)
            # Delivery
            worksheet.set_column('H:H', 23)
            worksheet.set_column('I:I', 10)
            worksheet.set_column('J:J', 20)
            worksheet.set_column('K:K', 8)
            worksheet.set_column('K:M', 10)
            # Invoice
            worksheet.set_column('N:N', 17)
            worksheet.set_column('O:O', 10)
            worksheet.set_column('P:P', 20)
            worksheet.set_column('Q:Q', 8)
            worksheet.set_column('R:R', 18)
            worksheet.set_column('S:U', 10)
            # Total
            worksheet.set_column('Q:R', 10)

            # CompanyLogo
            worksheet.merge_range('A1:B5', " ")

            # Image get from company logo
            web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url = web_base_url + '/logo.png?company=%d' % company.id
            image_data = io.BytesIO(urlopen(url).read())
            worksheet.insert_image('A1:B5', url,
                                   {'image_data': image_data, 'x_scale': 1.2, 'y_scale': 0.8, "align": 'center'})

            # Title
            worksheet.merge_range('C1:P2', company.name, company_header_title)
            worksheet.merge_range('C4:P5', 'Sales Order Validation Detailed Report', header_title)
            worksheet.write('A7', "From :", header_title1)
            worksheet.write('B7', date_from, date_format)
            worksheet.write('A8', "To :", header_title1)
            worksheet.write('B8', date_to, date_format)
            worksheet.write('T1', "Report Date", header_title)
            worksheet.write('U1', current_date, date_format)

            # Table parent heading
            worksheet.merge_range('A9:G9', 'SALE ORDER', header_format1)
            worksheet.merge_range('H9:M9', 'DELIVERY ORDER', header_format1)
            worksheet.merge_range('N9:U9', 'CUSTOMER INVOICE', header_format1)
            # Table Headings
            worksheet.write('A10', 'ORDER #', header_format)
            worksheet.write('B10', 'CUSTOMER NAME', header_format)
            worksheet.write('C10', 'DATE', header_format)
            worksheet.write('D10', 'PRODUCT', header_format)
            worksheet.write('E10', 'QTY', header_format)
            worksheet.write('F10', 'AMOUNT', header_format)
            worksheet.write('G10', 'STATUS', header_format)
            worksheet.write('H10', 'PICK#', header_format)
            worksheet.write('I10', 'DATE', header_format)
            worksheet.write('J10', 'PRODUCT', header_format)
            worksheet.write('K10', 'QTY', header_format)
            worksheet.write('L10', 'AMOUNT', header_format)
            worksheet.write('M10', 'STATUS', header_format)
            worksheet.write('N10', 'INV #', header_format)
            worksheet.write('O10', 'DATE', header_format)
            worksheet.write('P10', 'PRODUCT', header_format)
            worksheet.write('Q10', 'QTY', header_format)
            worksheet.write('R10', 'TAX EXCLUDED', header_format)
            worksheet.write('S10', 'VAT', header_format)
            worksheet.write('T10', 'TOTAL', header_format)
            worksheet.write('U10', 'STATUS', header_format)
            head = 10
            s_o = 0
            for order in sale_order_record:
                """
                    Loop for order data
                """
                row_o = head
                worksheet.write(row_o, 0, order.name, data)
                worksheet.write(row_o, 1, order.partner_id.name, data)
                worksheet.write(row_o, 2, order.date_order, date_format)
                worksheet.write(row_o, 6, dict(order._fields['doc_state'].selection).get(order.doc_state), data)
                s_o += order.amount_total
                for lines in order.order_line:
                    """
                        Loop for order line tree data
                    """
                    worksheet.write(row_o, 3, lines.product_id.name, data)
                    worksheet.write(row_o, 4, lines.product_uom_qty, header_title)
                    worksheet.write(row_o, 5, lines.price_total, amount_right)
                    row_o += 1

                delivery_order_record = self.env['stock.picking'].search([('group_id', '=', order.name)])
                row_d = head
                dl = 0
                for delivery in delivery_order_record:
                    """
                        Loop for delivery data
                    """
                    if 'Return' in delivery.origin:
                        worksheet.write(row_d, 7, delivery.name + " - Return", data)
                    else:
                        worksheet.write(row_d, 7, delivery.name, data)
                    worksheet.write(row_d, 8, delivery.scheduled_date, date_format)
                    worksheet.write(row_d, 12, dict(delivery._fields['state'].selection).get(delivery.state), data)

                    unique_lines = []
                    for line in delivery.move_ids_without_package:
                        if line.product_id not in unique_lines:
                            unique_lines.append(line.product_id)
                    for delivery_line in unique_lines:
                        """
                            Loop for delivery lines data
                        """

                        # Search on journal entries for get the manufacturing cost
                        product_cost = self.env['account.move.line'].search(
                            [('name', 'ilike', delivery.name), ('debit', '>', 0), ('product_id', '=', delivery_line.id)], order='id asc')
                        for pc in product_cost:
                            worksheet.write(row_d, 9, delivery_line.name, data)
                            if 'Return' in delivery.origin:
                                dl = dl - pc.debit
                                worksheet.write_string(row_d, 11, "(" + str(pc.debit) + ")", amount_right)
                            else:
                                dl = dl + pc.debit
                                worksheet.write(row_d, 11, pc.debit
                                                , amount_right)
                            worksheet.write(row_d, 10, abs(pc.quantity), amount_right)
                            row_d += 1

                invoice_order_record = self.env['account.move'].search([('invoice_origin', '=', order.name)])
                row_i = head
                inv = 0.0
                vat_total = 0.0
                tax_exclu = 0.0
                for invoice in invoice_order_record:
                    """
                        loop for invoices
                    """
                    worksheet.write(row_i, 13, invoice.name, data)
                    worksheet.write(row_i, 14, invoice.invoice_date, date_format)
                    worksheet.write(row_i, 20, dict(invoice._fields['state'].selection).get(invoice.state), data)
                    inv += invoice.amount_total
                    tax_exclu += invoice.amount_untaxed
                    for invoice_line in invoice.invoice_line_ids:
                        """
                            Loop for Invoice tree lines 
                        """
                        worksheet.write(row_i, 15, invoice_line.product_id.name, data)
                        worksheet.write(row_i, 16, invoice_line.quantity, header_title)
                        worksheet.write(row_i, 17, invoice_line.price_subtotal, amount_right)
                        if invoice_line.tax_ids:
                            # if lines have tax then
                            total_tax = 0
                            for tax in invoice_line.tax_ids:
                                """
                                    For loop for invoice tree to calculate total taxes amount
                                """
                                total_tax += tax.amount
                                calculated_tax = (total_tax * invoice_line.price_subtotal) / 100
                                worksheet.write(row_i, 18, round(calculated_tax, 1), amount_right)
                                worksheet.write(row_i, 19, invoice_line.price_total, amount_right)
                                vat_total += calculated_tax
                                row_i += 1
                head = max(row_o, row_d, row_i)
                # Total end the end of table
                worksheet.write(head, 1, "TOTAL", line_total_heading_bold)
                worksheet.write(head, 17, tax_exclu, line_total)
                worksheet.write(head, 18, vat_total, line_total)
                worksheet.write(head, 19, inv, line_total)
                worksheet.write(head, 5, s_o, line_total)
                worksheet.write(head, 11, dl, line_total)
                s_o = 0
                dl = 0
                head = head + 2
            # printed by information
            worksheet.write(head + 2, 0, "Printed by: ", data)
            worksheet.write(head + 2, 1, user.name, data)
        else:
            # Add Worksheet
            worksheet = workbook.add_worksheet("SO Validation Summary")

            # Sale
            worksheet.set_column('A:A', 12)
            worksheet.set_column('B:B', 25)
            worksheet.set_column('C:C', 8)
            worksheet.set_column('D:D', 20)
            worksheet.set_column('E:E', 10)
            worksheet.set_column('F:F', 15)
            worksheet.set_column('G:G', 23)
            # Delivery)
            worksheet.set_column('H:K', 10)
            # Invoice
            worksheet.set_column('L:L', 17)
            worksheet.set_column('M:R', 10)

            # CompanyLogo
            worksheet.merge_range('A1:B5', " ")

            # Image get from company logo
            web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url = web_base_url + '/logo.png?company=%d' % company.id
            image_data = io.BytesIO(urlopen(url).read())
            worksheet.insert_image('A1:B5', url,
                                   {'image_data': image_data, 'x_scale': 1.2, 'y_scale': 0.8, "align": 'center'})

            # Title
            worksheet.merge_range('C1:P2', company.name, company_header_title)
            worksheet.merge_range('C4:P5', 'Sales Order Validation Summary Report', header_title)
            worksheet.write('A7', "From :", header_title1)
            worksheet.write('B7', date_from, date_format)
            worksheet.write('A8', "To :", header_title1)
            worksheet.write('B8', date_to, date_format)
            worksheet.write('Q1', "Report Date", header_title)
            worksheet.write('R1', current_date, date_format)

            # Table parent heading
            worksheet.merge_range('A9:F9', 'SALE ORDER', header_format1)
            worksheet.merge_range('G9:K9', 'DELIVERY ORDER', header_format1)
            worksheet.merge_range('L9:R9', 'CUSTOMER INVOICE', header_format1)
            # Table Headings
            worksheet.write('A10', 'ORDER #', header_format)
            worksheet.write('B10', 'CUSTOMER NAME', header_format)
            worksheet.write('C10', 'DATE', header_format)
            worksheet.write('D10', '#ITEMS', header_format)
            worksheet.write('E10', 'AMOUNT', header_format)
            worksheet.write('F10', 'STATUS', header_format)
            worksheet.write('G10', 'PICK#', header_format)
            worksheet.write('H10', 'DATE', header_format)
            worksheet.write('I10', '#ITEMS', header_format)
            worksheet.write('J10', 'AMOUNT', header_format)
            worksheet.write('K10', 'STATUS', header_format)
            worksheet.write('L10', 'INV #', header_format)
            worksheet.write('M10', 'DATE', header_format)
            worksheet.write('N10', '#ITEMS', header_format)
            worksheet.write('O10', 'TAX EXCLUDED', header_format)
            worksheet.write('P10', 'VAT', header_format)
            worksheet.write('Q10', 'TOTAL', header_format)
            worksheet.write('R10', 'STATUS', header_format)
            head = 10
            s_o_total = 0.0
            total_inv_vat = 0.0
            total_tax_exclu = 0.0
            total_inv = 0.0
            total_delivery = 0.0
            for order in sale_order_record:
                """
                    Loop for orders data
                """
                row_o = head
                worksheet.write(row_o, 0, order.name, data)
                worksheet.write(row_o, 1, order.partner_id.name, data)
                worksheet.write(row_o, 2, order.date_order, date_format)
                worksheet.write(row_o, 3, "", date_format)
                worksheet.write(row_o, 5, dict(order._fields['doc_state'].selection).get(order.doc_state), data)
                # s_o += order.amount_total
                worksheet.write(row_o, 4, order.amount_total, line_total)
                s_o_total += order.amount_total
                row_o += 1

                delivery_order_record = self.env['stock.picking'].search([('group_id', '=', order.name)])
                row_d = head
                for delivery in delivery_order_record:
                    """
                        Loop for delivery data
                    """
                    if 'Return' in delivery.origin:
                        worksheet.write(row_d, 6, delivery.name + " - Return", data)
                    else:
                        worksheet.write(row_d, 6, delivery.name, data)
                    worksheet.write(row_d, 7, delivery.scheduled_date, date_format)
                    worksheet.write(row_d, 10, dict(delivery._fields['state'].selection).get(delivery.state), data)
                    product_cost = self.env['account.move.line'].search(
                        [('name', 'ilike', delivery.name)])
                    credit_sum = 0.0
                    for rec in product_cost:
                        if rec.credit > 0:
                            credit_sum = credit_sum + rec.credit
                    if 'Return' in delivery.origin:
                        total_delivery -= credit_sum
                        worksheet.write_string(row_d, 9, "(" + str(credit_sum) + ")", line_total)
                    else:
                        total_delivery += credit_sum
                        worksheet.write(row_d, 9, credit_sum, line_total)

                    row_d += 1

                invoice_order_record = self.env['account.move'].search([('invoice_origin', '=', order.name)])
                row_i = head
                inv = 0.0
                vat_total = 0.0
                tax_exclu = 0.0
                for invoice in invoice_order_record:
                    """
                        Loop for invoice data
                    """
                    worksheet.write(row_i, 11, invoice.name, data)
                    worksheet.write(row_i, 12, invoice.invoice_date, date_format)
                    worksheet.write(row_i, 17, dict(invoice._fields['state'].selection).get(invoice.state), data)
                    inv += invoice.amount_total
                    tax_exclu += invoice.amount_untaxed
                    for invoice_line in invoice.invoice_line_ids:
                        """
                            For loop for invoice tree to calculate total taxes amount
                        """
                        if invoice_line.tax_ids:
                            # if tax then calculate
                            total_tax = 0
                            for tax in invoice_line.tax_ids:
                                total_tax += tax.amount
                                calculated_tax = (total_tax * invoice_line.price_subtotal) / 100
                                vat_total += calculated_tax
                    worksheet.write(row_i, 14, tax_exclu, line_total)
                    worksheet.write(row_i, 15, vat_total, line_total)
                    worksheet.write(row_i, 16, inv, line_total)
                    total_tax_exclu += tax_exclu
                    total_inv_vat += vat_total
                    total_inv += inv
                    tax_exclu = 0
                    vat_total = 0
                    inv = 0
                    row_i += 1
                head = max(row_o, row_d, row_i)

                head = head + 1
            worksheet.write(head, 1, "TOTAL", line_total_heading_bold)
            worksheet.write(head, 4, s_o_total, line_total)
            worksheet.write(head, 14, total_tax_exclu, line_total)
            worksheet.write(head, 15, total_inv_vat, line_total)
            worksheet.write(head, 16, total_inv, line_total)
            worksheet.write(head, 9, total_delivery, line_total)
            worksheet.write(head + 2, 0, "Printed by: ", data)
            worksheet.write(head + 2, 1, user.name, data)