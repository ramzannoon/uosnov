from odoo import models, fields, api, _
import pdb


class OdooCMSDepartment(models.Model):
    _inherit = 'odoocms.department'

    account_payable = fields.Char("Fee Payable At")
    account_title = fields.Char('Account Title')
    account_no = fields.Char('Account Number')
    

class OdooCMSCampus(models.Model):
    _inherit = 'odoocms.campus'

    analytic_tag_id = fields.Many2one('account.analytic.tag', 'Analytic Tag')
    late_fee_per_day_fine = fields.Char(string='Late fee Fine/day', default=100, help='Write percentage sign if you want to add percentage, add value otherwise. i.e. 100 or 0.20%')
    late_fee_max_fine = fields.Integer(string='Late Fee Max Fine', default=1800)


class OdooCMSBatch(models.Model):
    _inherit = 'odoocms.batch'

    late_fee_per_day_fine = fields.Char(string='Late fee Fine/day', default=100, help='Write percentage sign if you want to add percentage, add value otherwise. i.e. 100 or 0.20%')
    late_fee_max_fine = fields.Integer(string='Late Fee Max Fine',default=1800)
