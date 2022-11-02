# #-*- coding:utf-8 -*-


from datetime import date
from odoo import api, models, fields


class issuanceReport(models.TransientModel):
    _name = "issuance.report"
    _description = 'Issuance Report'

    date_from = fields.Date(string="From ", default=date.today())
    date_to = fields.Date(string="To", default=date.today())

    # Define PDF Report Button Function
    def print_pdf_report(self):
        """
            This function can pass the data of wizard and print the report of PDF
        """
        datas = {
            'wizard_data': self.read()
        }
        return self.env.ref('library_management_system.action_issuance_report').report_action(self, data=datas)
