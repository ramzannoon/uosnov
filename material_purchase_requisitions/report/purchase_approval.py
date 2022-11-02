from odoo import api, models


class PurchaseApprovalReport(models.AbstractModel):
    _name = 'report.material_purchase_requisitions.purchase_approval'
    _description = 'Material Purchase Approval Report'

    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('material_purchase_requisitions.purchase_approval')

        doc = self.env[report.model].browse(docids)

        # Getting current company
        company = self.env.company

        def get_date_format(date):
            return date.strftime("%d/%m/%Y")

        def get_vendor_details(partner, source, product):
            purchase_order_line = self.env['purchase.order.line'].search([("order_id.partner_id", '=', partner.id),
                                                                          ("order_id.origin", '=', source),
                                                                          ("product_id", '=', product.id)])
            return purchase_order_line

        def get_vendor_record(partner, source):
            purchase_order = self.env['purchase.order'].search([("partner_id", '=', partner.id),
                                                                ("origin", '=', source)])
            return purchase_order

        def total_vendors(lines):
            vendors = []
            for po in lines:
                for rec in po.partner_id:
                    if rec and rec not in vendors:
                        vendors.append(rec)
            return vendors

        def get_amount_total_vendor(lines, vendor):
            total = 0
            if lines and vendor:
                for rec in lines:
                    if vendor == rec.partner_id:
                        total += rec.qty * rec.cost_price
            return total

        def get_purchase_order_vendor(purchase):
            vendor_names = []
            for po in purchase:
                for rec in po.partner_id:
                    if rec and rec not in vendor_names:
                        vendor_names.append(rec.name)
            return str(vendor_names).replace("'", "").replace("[", "").replace("]", "")

        return {
            'doc_model': 'material.purchase.requisition',
            'doc_ids': docids,
            'docs': doc,
            'company': company,
            'get_date_format': get_date_format,
            'get_vendor_details': get_vendor_details,
            'get_vendor_record': get_vendor_record,
            'total_vendors': total_vendors,
            'get_amount_total_vendor': get_amount_total_vendor,
            'get_purchase_order_vendor': get_purchase_order_vendor,
        }
