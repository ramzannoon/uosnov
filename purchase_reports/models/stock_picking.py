from odoo import fields, models, api


class StockPickings(models.Model):
    _inherit = "stock.picking"

    name_vr = fields.Char('Name')
    date = fields.Date('Date')
    igp = fields.Char('IGP')
    vourier_no = fields.Char('Vourier')
    vehicle_number = fields.Char('Vehicle number')
    department_id = fields.Many2one('hr.department', string='Department')
    out_date = fields.Datetime('Out Time')
    intime_date = fields.Datetime('In Time')
