
from datetime import date
from odoo import models, api


class ReportStockReport(models.AbstractModel):
    _name = "report.library_management_system.stock_report_template"
    _description = "Stock Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        record_wizard = self.env[self.model].browse(self.env.context.get('active_id'))
        company_id = self.env['res.company'].search([],limit=1)

        date_from = record_wizard.date_from
        date_to = record_wizard.date_to

        reference_unit_record = self.env["op.media.unit"].search([('create_date', '>=', date_from),
                                                                  ('create_date', '<=', date_to)])

        current_date = date.today()

        def date_format(date):
            return date.strftime("%d-%m-%Y")

        def book_author(reference):
            if reference:
                authors = []
                for book in reference.author_ids:
                    if book:
                        authors.append(book.name)
                print(11111111111, authors)
                return str(authors).replace("'", "").replace("[", "").replace("]", "")

        def quantity_lines(lines):
            if lines:
                count = 0
                for rec in lines:
                    count += 1
                return count
        return {
            'docs': record_wizard,
            'current_date': current_date,
            'date_format': date_format,
            'reference_unit': reference_unit_record,
            'book_author': book_author,
            'quantity_lines': quantity_lines,
            'company': company_id,
        }
