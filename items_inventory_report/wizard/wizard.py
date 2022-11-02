# -*- coding: utf-8 -*-

from odoo import models, fields, api


class WizardItemsInventory(models.TransientModel):
    _name = 'items.inventory.wizard'

    categ_id = fields.Many2one('product.category', required=True, string='Product Category')
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', reqired=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)


    def print_report(self):
        if self.categ_id:
            print("categ_id", self.categ_id)
            print("date from", self.date_from)
            print("date to", self.date_to)
        datas = {
            'wizard_data': self.read()
        }
        return self.env.ref('items_inventory_report.items_inventory_report').report_action(self, data=datas)
        # return {'type': 'ir.actions.report', 'report_name': 'items_inventory_report.items_inventory_template',
        #         'report_type': "qweb-pdf", 'data': data, }
