# -*- coding: utf-8 -*-

from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    custom_requisition_id = fields.Many2one(
        'material.purchase.requisition',
        string='Requisitions',
        copy=False
    )


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    warranty = fields.Char(string="Warranty")

    custom_requisition_line_id = fields.Many2one(
        'material.purchase.requisition.line',
        string='Requisitions Line',
        copy=False
    )
    terms_and_conditions = fields.Char(string='Terms and Conditions')
