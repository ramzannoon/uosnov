import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
from odoo import http
import logging
_logger = logging.getLogger(__name__)


class DateSheetReport(models.AbstractModel):
    _name = 'reports.odoocms_exam.datesheet_report'
    _description = 'DateSheet Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        department_id = data['form']['department_id'] and data['form']['department_id'][0] or False
        exam_type_id = data['form']['exam_type_id'] and data['form']['exam_type_id'][0] or False
        term_id = data['form']['term_id'] and data['form']['term_id'][0] or False

        time_list = []
        date_list = []
        rec_list = []
        company = http.request.env.user.company_id
        search_datsheet_id = self.env['odoocms.datesheet'].search([('department_id','=',department_id),('exam_type_id', '=',exam_type_id),('term_id','=',term_id)])
        if search_datsheet_id:
            search_datsheet = self.env['odoocms.datesheet.line'].search([('datesheet_id','=',search_datsheet_id.id)])
            values=""
            for rec in search_datsheet:
                if len(time_list)==0 :
                    time_list.append(rec.time_start.start_time)

                else:
                    count =0
                    for tm in time_list:
                        if tm==rec.time_start.start_time:
                            count+=1
                    if count==0 :
                        time_list.append(rec.time_start.start_time)

            for rec in search_datsheet:
                if len(date_list)==0:
                    date_list.append(rec.date)
                else:
                    count =0
                    for dt in date_list:
                        if dt==rec.date:
                            count+=1
                    if count==0:
                        date_list.append(rec.date)
            for dt in date_list:
                row_list = []
                record = search_datsheet.filtered(lambda l : l.date == dt)
                for rec in record:
                    itme_index= time_list.index(rec.time_start.start_time)
                    if itme_index == 0:
                        line ={
                        "date":rec.date,
                        "day" :  rec.date_day,
                        "time": rec.time_start.start_time,
                        "subject": rec.subject_id.subject_id.name,
                        }
                        row_list.append(line)
                    else:
                        lenth = len(row_list)
                        if lenth != itme_index:
                            for i in range(lenth,itme_index):
                                line ={
                                    "date":rec.date,
                                    "day" :  rec.date_day,
                                    "time": '',
                                    "subject": '',
                                }
                                row_list.append(line)

                        line ={
                        "date":rec.date,
                        "day" :  rec.date_day,
                        "time": rec.time_start.start_time,
                        "subject": rec.subject_id.subject_id.name,
                        }
                        row_list.append(line)

                rec_list.append(row_list)

                       
        report = self.env['ir.actions.report']._get_report_from_name('odoocms_exam.datesheet_report')
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'date': str(fields.Datetime.now()),
            'time_list' : time_list or False,
            'rec_list' : rec_list or False,
            'company': company or False,

            
        }
        return docargs
