from odoo import api, models


class PurchaseRequisition(models.AbstractModel):
    _name = 'report.material_purchase_requisitions.purchase_requisition'
    _description = 'Purchase Requisition Report'

    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('material_purchase_requisitions.purchase_requisition')
        docs = self.env[report.model].browse(docids)
        company = self.env.company
        return {
            'company': company,
            'docs': docs,
        }
