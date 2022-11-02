from odoo import api, models


class PurchaseRequisitionReport(models.AbstractModel):
    _name = 'report.material_purchase_requisitions.purchase_requisition'
    _description = 'Material Purchase Requisitions Report'

    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('material_purchase_requisitions.purchase_requisition')

        doc = self.env[report.model].browse(docids)

        # Getting current company
        company = self.env.company

        def get_date_format(date):
            return date.strftime("%d/%m/%Y")

        return {
            'doc_model': 'material.purchase.requisition',
            'doc_ids': docids,
            'docs': doc,
            'company': company,
            'get_date_format': get_date_format,
        }
