from odoo import api, models
import time
from odoo import api, models, fields, _
from dateutil.parser import parse
from odoo.exceptions import UserError


class ProductCatalogueReport(models.AbstractModel):
    _name = "report.odoocms_employee_portal.report_payslip"
    _description = "Portal Payslip Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        print(11111111111111111111, docids)
        pay = self.env['hr.payslip'].browse(docids)
        print(pay, "emplyeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
        return {
            'docs': pay,
            'data': data,
        }














        # 'issue_date': fields.date.today(),
        # 'certificate_list': certificate_list,
        # 'gross_total': gross_total,
        # certificate_list = []
        # gross_total = 0
        # payslips = self.env['hr.payslip'].search(
        #     [('employee_id', '=', docs.employee_id.id), ('date_to', '>=', docs.date_from),
        #      ('date_to', '<=', docs.date_to)])
        # for slip in payslips:
        #     for rule in slip.line_ids:
        #         if rule.code == 'GROSS':
        #             gross_total += rule.amount
        # for line in docs.certificate_line_ids:
        #     certificate_list.append({
        #         'period': line.period,
        #         'bank': line.bank,
        #         'branch': line.branch,
        #         'amount': line.amount,
        #     })

    # @api.model
    # def _get_report_values(self, docids, data=None):
    #     # product = self.env['hr.payslip'].browse(docids)
    #     product = self.env['hr.payslip'].browse(self.env.context.get('active_id'))
    #     return {
    #         'data': data,
    #         'docs': product,
    #     }

    # data = None
    @api.model
    def _get_default_report_id(self):
        return self.env.ref('odoocms_employee_portal.employee_action_report', False)

        # product = self.env['product.template'].browse(docids)
        # return {
        #     'data': data,
        #     'docs': product,
        # }


class TestingPayslip(models.Model):
    _inherit = "hr.payslip"
