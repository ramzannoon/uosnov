# -*- coding: utf-8 -*-

from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.department'

    dest_location_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
    )
    manager_id = fields.Many2one('hr.employee', string='Manager overriden', tracking=True,
                                 domain="['|', '&', ('company_id', '=', False), ('company_id', '=', company_id), ('user_id', '!=', False)]")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
