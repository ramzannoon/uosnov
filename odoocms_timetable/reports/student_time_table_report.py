import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class StudentTimeTable(models.AbstractModel):
    _name = 'report.odoocms_timetable.student_time_table_report'
    _description = 'Student Time Table Report'

#**************************Custom method for getting timetable of one day*************************
    def get_timetable(self, day_schedule_ids):
        empty_line = {
            'period': "",
            'course': "",
            'faculty': "",
            'time_from': "",
            'time_to': ",",
            'col_span': 1,
        }
        pre_line_ends = 0  # reference of previous time slot
        day_timetable = []
        for rec in day_schedule_ids:
            line = {
                'period': rec.period_id.name,
                'course': rec.subject_id.study_scheme_line_id.subject_id.name,
                'faculty': rec.subject_id.faculty_staff_id.name,
                'time_from': rec.time_from,
                'time_to': rec.time_to,
            }

            # this is to get col span
            time_line = [8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0]
            line_from = 0;
            line_to = 0;
            span = 0
            for i in range(0, len(time_line)):
                if (time_line[i]) == rec.time_from:
                    line_from = i
                elif (time_line[i]) == rec.time_to:
                    line_to = i

            # append black list where time slot doesn't exists
            new_start_from = pre_line_ends
            pre_line_ends = line_to
            for j in range(new_start_from, line_from):
                day_timetable.append(empty_line)

            span = line_to - line_from
            line['col_span'] = span
            day_timetable.append(line)
        return day_timetable

    # **************************End Custom method for getting timetable of one day*************************



    @api.model
    def _get_report_values(self, docsid, data=None):

        days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        time_slots = ['08:00-09:00', '09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-01:00','01:00-02:00','02:00-03:00','03:00-04:00','04:00-05:00']

        program_id = data['form']['program_id'] and data['form']['program_id'][0] or False
        batch_id = data['form']['batch_id'] and data['form']['batch_id'][0] or False
        batch_section_id = data['form']['batch_section_id'] and data['form']['batch_section_id'][0] or False
        semester_id = data['form']['semester_id'] and data['form']['semester_id'][0] or False

        program = self.env['odoocms.program'].search([('id','=',program_id)])
        batch = self.env['odoocms.batch'].search([('id','=',batch_id)])
        section = self.env['odoocms.batch.section'].search([('id','=',batch_section_id)])
        semester = self.env['odoocms.academic.semester'].search([('id','=',semester_id)])

        rec = {
            "monday": [],
            'tuesday': [],
            'wed': [],
            'thr': [],
            'fri': [],
            'sat': [],
            'sun': []
        }

        # if program_id and batch_id and batch_section_id and semester_id:
        #     timetable = self.env['odoocms.timetable'].search(
        #         [('program_id', '=', program_id),('batch_id', '=', batch_id),('academic_semester_id', '=', semester_id),('section_id', '=', batch_section_id)])
        #     if timetable:
        #         monday_schedule_ids = timetable[0].timetable_mon
        #         tuesday_schedule_ids = timetable[0].timetable_tue
        #         wednesday_schedule_ids = timetable[0].timetable_wed
        #         thursday_schedule_ids = timetable[0].timetable_thu
        #         friday_schedule_ids = timetable[0].timetable_fri
        #         saturday_schedule_ids = timetable[0].timetable_sat
        #         sun_schedule_ids = timetable[0].timetable_sun
        #         rec = {
        #             "monday": self.get_timetable(monday_schedule_ids),
        #             'tuesday': self.get_timetable(tuesday_schedule_ids),
        #             'wed': self.get_timetable(wednesday_schedule_ids),
        #             'thr': self.get_timetable(thursday_schedule_ids),
        #             'fri': self.get_timetable(friday_schedule_ids),
        #             'sat': self.get_timetable(saturday_schedule_ids),
        #             'sun': self.get_timetable(sun_schedule_ids),
        #         }


        report = self.env['ir.actions.report']._get_report_from_name('odoocms_timetable.student_time_table_report')
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'program': program or False,
            'batch': batch or False,
            'section': section or False,
            'semester': semester or False,
            'header1': semester.name +" "+ program.department_id.name +" "+program.department_id.campus_id.name or False,
            'header2': batch.name +"\n"+ section.name or False,
            'days': days or False,
            'time_slots': time_slots or False,
            'timetable': rec or False,
        }
        return docargs