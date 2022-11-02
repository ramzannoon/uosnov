from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError, Warning


class AccountCheckPrint(models.Model):
    _inherit = "account.payment"

    check_number = fields.Char('Check Number')

    @api.onchange('check_number')
    def same_check_number(self):
        for rec in self:
            if rec.check_number:
                existing_number = self.env['account.payment'].search([('check_number', '=', rec.check_number)])
                if existing_number:
                    raise ValidationError(">>>> Same Check number can't be added >>>>")


