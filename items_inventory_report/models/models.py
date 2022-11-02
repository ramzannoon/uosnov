# -*- coding: utf-8 -*-

import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta

class ReportItemsInventory(models.AbstractModel):
    _name = 'report.items_inventory_report.items_inventory_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        print("Data", data)
        # docs = self.env['account.payment'].browse(docids)

        self.model = self.env.context.get('active_model')
        active_record = self.env[self.model].browse(self.env.context.get('active_id'))

        categ_id = active_record.categ_id
        data = []
        products = self.env['product.product'].search([('categ_id', '=', categ_id.id)])
        sr = 0
        for prod in products:
            sr = sr + 1
            reorder = self.env['stock.warehouse.orderpoint'].search([('product_id', '=', prod.id)])
            vals = {
                'item_code': prod.default_code,
                'name': prod.name,
                'uom': prod.uom_name,
                'value': prod.standard_price,
                'min_value': reorder.product_min_qty if reorder else 0.0,
                'max_value': reorder.product_max_qty if reorder else 0.0,
                'on_hand': prod.qty_available,
                'amount': prod.qty_available * prod.standard_price,
                'sr': sr
            }
            data.append(vals)
        print("date", data)

        return {
            'doc_ids': docids,
            'date_from': active_record.date_from,
            'date_to': active_record.date_to,
            # 'docs': docs,
            'data': data,
            'company': active_record.company_id,
        }

