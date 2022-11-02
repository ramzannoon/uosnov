from odoo import models, fields, api, _
from . import aarsol_unitime
import pdb
from odoo.exceptions import ValidationError, UserError

class OdooCMSTimePattern(models.Model):
    _name = 'odoocms.time.pattern'
    _description = 'Time Pattern'

    name = fields.Char(string="Name", required=True, )
    # uniId = fields.Integer('Unitime ID')
    nbrMeetings = fields.Integer("No. of Meetings")


    minsPerMeeting = fields.Integer("Minutes Per Meeting")
    type = fields.Selection(
        [('Standard', 'Standard'), ('Morning', 'Morning'), ('Evening', 'Evening'), ('Extended', 'Extended'),
         ('Saturday', 'Saturday'), ('Exact Time', 'Exact Time')], 'Type', default='Standard')
    visible = fields.Boolean('Visible')
    nbrSlotsPerMeeting = fields.Integer('Slots per Meeting')
    breakTime = fields.Integer('Break Time')
    pattern_days = fields.One2many('odoocms.time.pattern.days', 'pattern_id', 'Pattern Days')
    pattern_times = fields.One2many('odoocms.time.pattern.time', 'pattern_id', 'Pattern Times')


# session_id = constraint `fk_time_pattern_session` foreign key (`session_id`) references `sessions` (`uniqueid`) on delete cascade

def sync_unitime_odoo(self, timePatterns):
    for timePattern in timePatterns:
        data = {
            'name': timePattern['name'],
            'nbrMeetings': timePattern['nbrMeetings'],
            'minsPerMeeting': timePattern['minsPerMeeting'],
            'type': timePattern['type'],
            'visible': timePattern['visible'],
            'nbrSlotsPerMeeting': timePattern['nbrSlotsPerMeeting'],
            'breakTime': timePattern['breakTime'],
        }
        pattern = self.env['odoocms.time.pattern'].search([('name', '=', timePattern['name'])])
        if pattern:
            pattern.write(data)
        else:
            pattern = self.env['odoocms.time.pattern'].create(data)

        # Days
        for days in timePattern['days']:
            daydata = {
                'code': days['code'],
                'pattern_id': pattern.id,
            }
            patternDay = self.env['odoocms.time.pattern.days'].search(
                [('pattern_id', '=', pattern.id), ('code', '=', days['code'])])
            if patternDay:
                patternDay.write(daydata)
            else:
                patternDay = self.env['odoocms.time.pattern.days'].create(daydata)

        # Slots
        for slot in timePattern['time']:
            timedata = {
                'start': slot['start'],
                'pattern_id': pattern.id,
            }
            patternSlot = self.env['odoocms.time.pattern.time'].search(
                [('pattern_id', '=', pattern.id), ('start', '=', slot['start'])])
            if patternSlot:
                patternSlot.write(timedata)
            else:
                patternSlot = self.env['odoocms.time.pattern.time'].create(timedata)


class OdooCMSTimePatternDays(models.Model):
    _name = 'odoocms.time.pattern.days'
    _description = 'Time Pattern Days'

    code = fields.Char('Day Code')
    pattern_id = fields.Many2one('odoocms.time.pattern', 'Pattern', ondelete='cascade')
    # uniId = fields.Integer('Unitime ID')
    # uni_pattern_id = fields.Integer('Unitime Pattern')


class OdooCMSTimePatternTime(models.Model):
    _name = 'odoocms.time.pattern.time'
    _description = 'Time Pattern Time'

    start = fields.Char('Slot Start')
    pattern_id = fields.Many2one('odoocms.time.pattern', 'Pattern', ondelete='cascade')
    # uniId = fields.Integer('Unitime ID')
    # uni_pattern_id = fields.Integer('Unitime Pattern')


class OdooCMSDatePattern(models.Model):
    _name = 'odoocms.date.pattern'
    _description = 'Date Pattern'

    name = fields.Char(string="Name", required=True, )
    type = fields.Selection([('Standard', 'Standard'), ('Non-standard', 'Non-standard'), ('Extended', 'Extended'),
                             ('Alternate Weeks', 'Alternate Weeks'),
                             ('Saturday', 'Saturday'), ('Exact Time', 'Exact Time')], 'Type', default='Standard')
    visible = fields.Boolean('Visible')
    default = fields.Boolean('Default')
    pattern_dates = fields.One2many('odoocms.date.pattern.dates', 'pattern_id', 'Pattern Dates')

    # pattern, offset

    def sync_unitime_odoo(self, datePatterns):
        for datePattern in datePatterns:
            data = {
                'name': datePattern['name'],
                'type': datePattern['type'],
                'visible': datePattern['visible'],
                'default': datePattern['default'],
            }
            pattern = self.env['odoocms.date.pattern'].search([('name', '=', datePattern['name'])])
            if pattern:
                pattern.write(data)
            else:
                pattern = self.env['odoocms.date.pattern'].create(data)

            # Dates
            for date in datePattern['dates']:
                datedata = {
                    'fromDate': date['fromDate'],
                    'toDate': date['toDate'],
                    'pattern_id': pattern.id,
                }
                patternDate = self.env['odoocms.date.pattern.dates'].search(
                    [('pattern_id', '=', pattern.id), ('fromDate', '=', date['fromDate']),
                     ('toDate', '=', date['toDate'])])
                if patternDate:
                    patternDate.write(datedata)
                else:
                    patternDate = self.env['odoocms.date.pattern.dates'].create(datedata)


class OdooCMSDatePatternDates(models.Model):
    _name = 'odoocms.date.pattern.dates'
    _description = 'Date Pattern Dates'

    fromDate = fields.Date('From Date')
    toDate = fields.Date('To Date')
    pattern_id = fields.Many2one('odoocms.date.pattern', 'Pattern', ondelete='cascade')


class OdooCmsDepartment(models.Model):
    _inherit = 'odoocms.department'

    externalId = fields.Char('External ID')
    abbreviation = fields.Char('Abbreviation')
    event_mgmt = fields.Boolean('Event Management')
    external_manager = fields.Boolean('External Manager')
    external_manager_name = fields.Char('External Manager Name')
    external_manager_abbreviation = fields.Char('External Manager Abbreviation')

    def sync_unitime_odoo(self, departments):
        for department in departments:
            data = {
                'name': department['name'],
                'code': department['code'],
                'externalId': department['externalId'],
                'abbreviation': department['abbreviation'],
                'event_mgmt': department.get('event_mgmt', False),
                'external_manager': department.get('external_manager', False),
                'external_manager_name': department.get('external_manager_name', ''),
                'external_manager_abbreviation': department.get('external_manager_abbreviation', '')
            }
            pattern = self.env['odoocms.department'].search([('code', '=', department['code'])])
            if pattern:
                pattern.write(data)
            else:
                pattern = self.env['odoocms.department'].create(data)

# class OdooCMSTimeTable(models.Model):
#     _name = 'odoocms.timetable'
#     _description = 'Timetable'
#
#     program_id = fields.Many2one('odoocms.program', string='Program', required=True)
#     batch_id = fields.Many2one('odoocms.batch','Batch',required=True)
#     section_id = fields.Many2one('odoocms.batch.section','Section',required=True)
#     academic_semester_id = fields.Many2one('odoocms.academic.term', string='Academic Term', required=True)
#
#     active = fields.Boolean('Active', default=True)
#     name = fields.Char(compute='_get_name',store=True)
#     company_id = fields.Many2one('res.company', string='Company',
#                                  default=lambda self: self.env['res.company']._company_default_get())
#
#
#     timetable_mon = fields.One2many('odoocms.timetable.schedule', 'timetable_id', domain=[('week_day', '=', '0')])
#     timetable_tue = fields.One2many('odoocms.timetable.schedule', 'timetable_id', domain=[('week_day', '=', '1')])
#     timetable_wed = fields.One2many('odoocms.timetable.schedule', 'timetable_id', domain=[('week_day', '=', '2')])
#     timetable_thu = fields.One2many('odoocms.timetable.schedule', 'timetable_id', domain=[('week_day', '=', '3')])
#     timetable_fri = fields.One2many('odoocms.timetable.schedule', 'timetable_id', domain=[('week_day', '=', '4')])
#     timetable_sat = fields.One2many('odoocms.timetable.schedule', 'timetable_id', domain=[('week_day', '=', '5')])
#     timetable_sun = fields.One2many('odoocms.timetable.schedule', 'timetable_id', domain=[('week_day', '=', '6')])
#     timetable = fields.One2many('odoocms.timetable.schedule', 'timetable_id',)
#
#     @api.depends('batch_id','section_id','academic_semester_id')
#     def _get_name(self):
#         for rec in self:
#              if rec.batch_id and rec.section_id and rec.academic_semester_id:
#                 rec.name = rec.batch_id.name + " (" + rec.section_id.name  + ")" + " /" + rec.academic_semester_id.name
#
#     @api.model
#     def get_timetable(self, student = False):
#         time_table = []
#
#         days_line = {
#             'monday':[],
#             'tuesday':[],
#             'wednesday':[],
#             'thrusday':[],
#             'friday':[],
#             'saturday':[],
#             'sunday':[],
#         }
#         if student:
#             student_id = self.env['odoocms.student'].search([('id','=',student)])
#             # for rec in self.filtered(lambda l: l.program_id == student_id.program_id.id and l.batch_id == student_id.batch_id.id
#             #                         and l.academic_semester_id == student_id.academic_semester_id.id and l.section_id == student_id.section_id.id
#             #                          and self.active):
#
#             time_table = self.search([('program_id','=',student_id.program_id.id),('batch_id','=',student_id.batch_id.id),('academic_semester_id','=',student_id.academic_semester_id.id)
#                               ,('section_id','=',student_id.section_id.id)])
#
#             day_list =[]
#             for mon in time_table.timetable_mon:
#                 day_line = {
#                     'time_from':str(mon.time_from),
#                     'time_to':str(mon.time_to),
#                     'subject':mon.class_id.study_scheme_line_id.subject_id.name,
#                     'faculty':mon.faculty_id.name,
#                     'room':mon.room_id.name,
#                 }
#                 day_list.append(day_line)
#             days_line['monday'] = day_list
#
#             day_list =[]
#             for tue in time_table.timetable_tue:
#                 day_line = {
#                     'time_from':str(tue.time_from),
#                     'time_to':str(tue.time_to),
#                     'subject':tue.class_id.study_scheme_line_id.subject_id.name,
#                     'faculty':tue.faculty_id.name,
#                     'room':tue.room_id.name,
#                 }
#                 day_list.append(day_line)
#             days_line['tuesday'] = day_list
#
#             day_list =[]
#             for wed in time_table.timetable_wed:
#                 day_line = {
#                     'time_from':str(wed.time_from),
#                     'time_to':str(wed.time_to),
#                     'subject':wed.class_id.study_scheme_line_id.subject_id.name,
#                     'faculty':wed.faculty_id.name,
#                     'room':wed.room_id.name,
#                 }
#                 day_list.append(day_line)
#             days_line['wednesday'] = day_list
#
#             day_list =[]
#             for thu in time_table.timetable_thu:
#                 day_line = {
#                     'time_from':str(thu.time_from),
#                     'time_to':str(thu.time_to),
#                     'subject':thu.class_id.study_scheme_line_id.subject_id.name,
#                     'faculty':thu.faculty_id.name,
#                     'room':thu.room_id.name,
#                 }
#                 day_list.append(day_line)
#             days_line['thrusday'] = day_list
#
#             day_list =[]
#             for fri in time_table.timetable_fri:
#                 day_line = {
#                     'time_from':str(fri.time_from),
#                     'time_to':str(fri.time_to),
#                     'subject':fri.class_id.study_scheme_line_id.subject_id.name,
#                     'faculty':fri.faculty_id.name,
#                     'room':fri.room_id.name,
#                 }
#                 day_list.append(day_line)
#             days_line['friday'] = day_list
#
#             day_list =[]
#             for sat in time_table.timetable_sat:
#                 day_line = {
#                     'time_from':str(sat.time_from),
#                     'time_to':str(sat.time_to),
#                     'subject':sat.class_id.study_scheme_line_id.subject_id.name,
#                     'faculty':sat.faculty_id.name,
#                     'room':sat.room_id.name,
#                 }
#                 day_list.append(day_line)
#             days_line['saturday'] = day_list
#
#             day_list =[]
#             for sun in time_table.timetable_sun:
#                 day_line = {
#                     'time_from':str(sun.time_from),
#                     'time_to':str(sun.time_to),
#                     'subject':sun.class_id.study_scheme_line_id.subject_id.name,
#                     'faculty':sun.faculty_id.name,
#                     'room':sun.room_id.name,
#                 }
#                 day_list.append(day_line)
#             days_line['sunday'] = day_list
#
#             time_table.append(days_line)
#
#         return time_table
#



