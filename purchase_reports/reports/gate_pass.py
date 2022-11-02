from odoo import api, models


class GatePass(models.AbstractModel):
    _name = 'report.purchase_reports.gate_pass_template'
    _description = 'Outward Gate Report'

    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('purchase_reports.gate_pass_template')

        doc = self.env[report.model].browse(docids)
        company = self.env.company

        return {
            'doc_model': 'stock.picking',
            'doc_ids': docids,
            'docs': doc,
            'company': company,
        }


class GatePass(models.AbstractModel):
    _name = 'report.purchase_reports.returnable_gate_pass_template'
    _description = 'Returnable Gate Report'

    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('purchase_reports.returnable_gate_pass_template')

        doc = self.env[report.model].browse(docids)
        company = self.env.company
        return {
            'doc_model': 'stock.picking',
            'doc_ids': docids,
            'docs': doc,
            'company': company,
        }



class OutGatePass(models.AbstractModel):
    _name = 'report.purchase_reports.out_gate_pass_template'
    _description = 'Returnable Gate Report'

    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('purchase_reports.out_gate_pass_template')

        doc = self.env[report.model].browse(docids)
        company = self.env.company
        return {
            'doc_model': 'stock.picking',
            'doc_ids': docids,
            'docs': doc,
            'company': company,
        }


