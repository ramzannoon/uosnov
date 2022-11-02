from num2words import num2words
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)


class CheckPrint(models.AbstractModel):
    _name = 'report.check_generation.check_print_report'
    _description = 'Check Print Report'

    def _get_report_values(self, docids, data=None):
        docs = self.env['account.payment'].browse(docids)
        amount_in_words = num2words(int(docs.amount), to='ordinal')
        company = self.env.company

        return {
            'doc_ids': docids,
            'docs': docs,
            'doc_model': 'account.payment',
            'company': company,
            'data': {'amount_in_words':amount_in_words},
        }

