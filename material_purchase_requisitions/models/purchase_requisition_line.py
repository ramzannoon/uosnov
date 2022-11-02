# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class MaterialPurchaseRequisitionLine(models.Model):
    _name = "material.purchase.requisition.line"
    _description = 'Material Purchase Requisition Lines'


    requisition_id = fields.Many2one(
        'material.purchase.requisition',
        string='Requisitions',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )
    #     layout_category_id = fields.Many2one(
    #         'sale.layout_category',
    #         string='Section',
    #     )
    description = fields.Char(
        string='Description',
        required=True,
    )
    qty = fields.Float(
        string='Quantity',
        default=1,
        required=True,
    )
    cost_price = fields.Float(string='Cost', required=True)
    uom = fields.Many2one(
        'uom.uom',#product.uom in odoo11
        string='Unit of Measure',
        required=True,
    )
    terms_and_conditions = fields.Char(string='Terms and Conditions', required=True)
    partner_id = fields.Many2one(
        'res.partner',
        string='Vendors',
    )
    specifications = fields.Char(string='Specification')
    requisition_type = fields.Selection(
        selection=[
            ('internal','Internal Picking'),
            ('purchase','Purchase Order'),
        ],
        string='Requisition Action',
        default='purchase',
        required=True,
    )

    warranty = fields.Char(string="Warranty")

    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            rec.description = rec.product_id.name
            rec.uom = rec.product_id.uom_id.id
            if self.requisition_id.purchase_approval_id.purchase_request_line_ids:
                product_ids = []
                for lines in self.requisition_id.purchase_approval_id.purchase_request_line_ids:
                    product_ids.append(lines.product_id.id)
                if product_ids:
                    return {'domain': {'product_id': [('id', 'in', product_ids)]}}
