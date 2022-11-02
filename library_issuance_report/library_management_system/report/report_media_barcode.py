# -*- coding: utf-8 -*-
import time
from odoo import models, api


class ReportMediaBarcode(models.AbstractModel):
    _name = "report.library_management_system.report_media_barcode"
    _description = "Media Barcode Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['op.media'].browse(docids)

        def author_name(record):
            if record:
                author_name = []
                for rec in record.author_ids:
                    author_name.append(rec.name)
                return str(author_name).replace("'", "").replace("[", "").replace("]", "")

        docargs = {
            'doc_model': 'op.media',
            'author_name': author_name,
            'docs': docs,
            'time': time,
        }
        return docargs
