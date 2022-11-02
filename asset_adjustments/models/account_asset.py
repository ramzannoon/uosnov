# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    bill_quantity = fields.Integer(string="Bill QTY", compute='_get_bill_quantity')
    quantity_issue = fields.Integer(string="Quantity Issue", compute='_get_quantity_issue')

    asset_qty_issued_ids = fields.One2many('asset.qty.issued', 'account_asset_id', string='Asset Qty Issue')

    def _get_bill_quantity(self):
        for rec in self:
            order_bill_qty = 0
            for bill_lines in self.original_move_line_ids:
                order_bill_qty += bill_lines.quantity
            rec.bill_quantity = order_bill_qty

    def _get_quantity_issue(self):
        for rec in self:
            total_issue = 0
            for issues in rec.asset_qty_issued_ids:
                total_issue += issues.reserved_qty
            rec.quantity_issue = total_issue


class AssetQTYIssued(models.Model):
    _name = 'asset.qty.issued'

    reserved_qty = fields.Integer(string="Bill QTY")
    account_asset_id = fields.Many2one('account.asset', string="Account Asset")
