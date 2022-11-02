from odoo import fields, models, api
import datetime
from datetime import date
from datetime import datetime
from odoo.exceptions import UserError, ValidationError, Warning


class SeqAccNew(models.Model):
    _inherit = "account.move"

    name = fields.Char(readonly=True, required=True, copy=False, default='New')

    @api.model
    def create(self, vals):
        result = super(SeqAccNew, self).create(vals)
        if result['type'] == 'in_invoice':
            bill_record = self.env['account.move'].search([('type', '=', 'in_invoice')])
            if bill_record is not None:
                rec_fill = bill_record.filtered(lambda e: e.invoice_date.year == result['invoice_date'].year)
                all_sequence = [int(rec.name.split('/')[-1]) for rec in rec_fill if
                                not rec.name == 'New' and int(rec.name.split('/')[-1])]
                if all_sequence:
                    if len(all_sequence) > 0:
                        max_sequence = max(all_sequence)
                        self.env['ir.sequence'].search([('code', '=', 'self.service')]).write(
                            {'number_next': max_sequence + 1})
                    default_seq = self.env['ir.sequence'].next_by_code('self.service') or 1
                    ct_month = '0' + str(result['invoice_date'].month) if result['invoice_date'].month < 10 else str(
                        result['invoice_date'].month)
                    ct_date_year = result['invoice_date'].year
                    result['name'] = 'BILL/' + ct_month + '/' + str(ct_date_year) + '/' + default_seq
                else:
                    self.env['ir.sequence'].search([('code', '=', 'self.service')]).write({'number_next': 1})
                    default_seq = self.env['ir.sequence'].next_by_code('self.service') or 'New'
                    ct_month = '0' + str(result['invoice_date'].month) if result['invoice_date'].month < 10 else str(
                        result['invoice_date'].month)
                    ct_date_year = result['invoice_date'].year
                    result['name'] = 'BILL/' + ct_month + '/' + str(ct_date_year) + '/' + default_seq

            else:
                self.env['ir.sequence'].search([('code', '=', 'self.service')]).write({'number_next': 1})
                default_seq = self.env['ir.sequence'].next_by_code('self.service') or 'New'
                ct_month = '0' + str(result['invoice_date'].month) if result['invoice_date'].month < 10 else str(
                    result['invoice_date'].month)
                ct_date_year = result['invoice_date'].year
                result['name'] = 'BILL/' + ct_month + '/' + str(ct_date_year) + '/' + default_seq

        if result['type'] == 'out_invoice':
            bill_record = self.env['account.move'].search([('type', '=', 'out_invoice')])
            if bill_record:
                rec_fill = bill_record.filtered(
                    lambda e: e.invoice_date.year == result['invoice_date'].year)
                all_sequence = [int(rec.name.split('/')[-1]) for rec in rec_fill if
                                not rec.name == 'New' and int(rec.name.split('/')[-1])]
                if all_sequence:
                    max_sequence = max(all_sequence)
                    self.env['ir.sequence'].search([('code', '=', 'self.service')]).write(
                        {'number_next': max_sequence + 1})
                    default_seq = self.env['ir.sequence'].next_by_code('self.service') or 'New'
                    ct_month = '0' + str(result['invoice_date'].month) if result['invoice_date'].month < 10 else str(
                        result['invoice_date'].month)
                    ct_date_year = result['invoice_date'].year
                    result['name'] = 'INV/' + ct_month + '/' + str(ct_date_year) + '/' + default_seq
                else:
                    self.env['ir.sequence'].search([('code', '=', 'self.service')]).write({'number_next': 1})
                    default_seq = self.env['ir.sequence'].next_by_code('self.service') or 'New'
                    ct_month = '0' + str(result['invoice_date'].month) if result['invoice_date'].month < 10 else str(
                        result['invoice_date'].month)
                    ct_date_year = result['invoice_date'].year
                    result['name'] = 'INV/' + ct_month + '/' + str(ct_date_year) + '/' + default_seq

            else:
                self.env['ir.sequence'].search([('code', '=', 'self.service')]).write({'number_next': 1})
                default_seq = self.env['ir.sequence'].next_by_code('self.service') or 'New'
                ct_month = '0' + str(result['invoice_date'].month) if result['invoice_date'].month < 10 else str(
                    result['invoice_date'].month)
                ct_date_year = result['invoice_date'].year
                result['name'] = 'INV/' + ct_month + '/' + str(ct_date_year) + '/' + default_seq

        return result
