from odoo import api, models


class StudentApplication(models.AbstractModel):
    _name = 'report.odoocms_admission_portal.purchase_requisition_new'
    _description = 'Student Application Report'

    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('odoocms_admission_portal.student_admission_application_mine')

        docs = self.env[report.model].browse(docids)
        company = self.env.company

        return {
            'doc_model': 'odoocms.application',
            'doc_ids': docids,
            'docs': docs,
            'company': company,
        }
