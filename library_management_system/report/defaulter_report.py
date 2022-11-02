
from datetime import date
from odoo import models, api


class ReportLibraryDefaulter(models.AbstractModel):
    _name = "report.library_management_system.defaulter_report_template"
    _description = "defaulter Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        record_wizard = self.env[self.model].browse(self.env.context.get('active_id'))
        company_id = self.env['res.company'].search([],limit=1)

        date_from = record_wizard.date_from
        date_to = record_wizard.date_to

        issuance_record = self.env["op.media.movement"].search([('issued_date', '>=', date_from),
                                                                   ('issued_date', '<=', date_to)])

        reference_issuance = []
        for rec in issuance_record:
            if rec.actual_return_date and rec.return_date:
                if rec.actual_return_date > rec.return_date:
                    reference_issuance.append(rec)

        current_date = date.today()

        def date_format(date):
            return date.strftime("%d-%m-%Y")

        return {
            'docs': record_wizard,
            'current_date': current_date,
            'date_format': date_format,
            'reference_defaulter': reference_issuance,
            'company': company_id,
        }
