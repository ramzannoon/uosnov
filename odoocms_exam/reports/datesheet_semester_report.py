import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class DateSheetSemesterReport(models.AbstractModel):
    _name = 'reports.odoocms_exam.datesheet_semester_report'
    _description = 'DateSheet Semester Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        semester_id = data['form']['semester_id'] and data['form']['semester_id'][0] or False
        exam_type_id = data['form']['exam_type_id'] and data['form']['exam_type_id'][0] or False
        term_id = data['form']['term_id'] and data['form']['term_id'][0] or False

        depart_list = []
        date_list = []
        rec_list = []
        time_list = []
        search_datsheet_id = self.env['odoocms.datesheet'].search([('exam_type_id', '=',exam_type_id),('term_id','=',term_id)])
        if search_datsheet_id:
            for rec in search_datsheet_id:
                depart_list.append(rec.department_id.name)
            for deprt in search_datsheet_id:
                raw_list=[]
                time_raw_list=[]
                for rec in deprt.datesheet_line_ids.filtered(lambda l : l.semester_id.id==semester_id):
                    raw_list.append(rec.date)
                    time_raw_list.append(rec.time_start.start_time)
                date_list = list(set(date_list+raw_list))
                time_list.append(time_raw_list)
            date_list.sort()
            for dt in date_list:
                date_rec_list=[]
                for deprt in search_datsheet_id:
                    line={
                        'date': dt,
                        'time':'',
                        'subject': '',
                        }
                    date_rec_list.append(line)
                for deprt in search_datsheet_id:
                    for rec in deprt.datesheet_line_ids.filtered(lambda l : l.semester_id.id==semester_id and l.date == dt):
                        line={
                        'date': dt,
        				'time':rec.time_start.start_time,
        				'subject': rec.subject_id.subject_id.name,
                        }
                        date_rec_list[depart_list.index(deprt.department_id.name)]=line
                rec_list.append(date_rec_list)
        	
                       
        report = self.env['ir.actions.report']._get_report_from_name('odoocms_exam.datesheet_semester_report')
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'date': str(fields.Datetime.now()),
            'depart_list' : depart_list or False,
            'rec_list': rec_list or False,
            'time_list': time_list or False,

            
        }
        return docargs