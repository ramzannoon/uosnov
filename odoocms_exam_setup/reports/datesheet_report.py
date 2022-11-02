import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta

import logging
_logger = logging.getLogger(__name__)


class DateSheetReport(models.AbstractModel):
    _name = 'report.odoocms_exam_setup.exam_setup_datesheet_report'
    _description = 'Date Sheet Report'


    @api.model
    def _get_report_values(self, docsid, data=None):
        program_list = []
        company_id = self.env.user.company_id
        batches = self.env['odoocms.batch'].search([('id','in',data['form']['batch_ids'])])
        datesheet_lines = self.env['odoocms.datesheet.line'].search([('batch_id', 'in', batches.ids)])
        dates_list = []
        for rec in batches:
            program_list.append(rec.program_id.id)
        programs = self.env['odoocms.program'].search([('id','in',program_list)])

        for rec in datesheet_lines:
            dates_list.append(rec.date)
        dates_filterd_list = list(set(dates_list))
        dates_filterd_list.sort()
        final_list = []
        for dt in dates_filterd_list:
            list1 = []
            for batch in batches:
                records = datesheet_lines.filtered(lambda x: x.date == dt and x.batch_id.id == batch.id)
                if records:
                    for rec in records:
                        if rec.course_id.name:
                            line = {
                                'date':rec.date,
                                'subject':rec.course_id.name
                            }
                            list1.append(line)
                        else:
                            line = {
                                'date': rec.date,
                                'subject': '-'
                            }
                            list1.append(line)
                else:
                    line = {
                        'date': dt,
                        'subject': '-'
                    }
                    list1.append(line)
            final_list.append(list1)

        docargs = {
            'doc_ids': [],
            'data': data['form'],
            'company_id':company_id or False,
            'programs':programs or False,
            'final_list':final_list or False,
            'batches':batches or False,
        }
        return docargs



