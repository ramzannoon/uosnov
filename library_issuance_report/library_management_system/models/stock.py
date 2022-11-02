
from odoo import models, fields, api, _


class StockLibrary(models.Model):
    _name = "stock.library"
    _description = "Stock Library"

    media_id = fields.Many2one('op.media', string='Reference')
    company_id = fields.Many2one(related='location_id.company_id', string='Company', store=True, readonly=True)
    location_id = fields.Many2one('stock.location', string='Location')
    inventory_quantity = fields.Float(string='On Hand Quantity')
    in_date = fields.Datetime('Incoming Date', readonly=True)
