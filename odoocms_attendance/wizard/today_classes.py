import pdb
import time
from datetime import datetime, date, timedelta
from odoo import api, fields, models,_
from dateutil.relativedelta import relativedelta
date_format ='%Y-%m-%d'
from odoo.exceptions import UserError


class OdooCMSTimetableScheduleClass(models.TransientModel):
	_name ='odoocms.timetable.schedule.class'
	_description = 'Generate Todays Classes'

	batch_id = fields.Many2one('odoocms.batch', 'Program Batch')
	section_id = fields.Many2one('odoocms.batch.section', 'Class Section')
	date_class = fields.Date('Class Date From',default=lambda self: fields.Date.today())
	date_class_to = fields.Date('Class Date To', default=lambda self: fields.Date.today())

	def generate_timetable(self):
		att_classes = self.env['odoocms.class.attendance']
		dt= self.date_class
		
		pub_holiday = []
		pub_holiday_search = self.env['odoocms.holidays.public'].search([('term_id', '=', self.batch_id.term_id.id)])
		for ho in pub_holiday_search:
			pub_holiday.append(ho.date)
		
		#.with_progress(msg="Schedule Classes")
		while dt <= self.date_class_to:
			weekdays = self.env['odoocms.week.day'].search([('number','=',dt.weekday()+1)])
			schedules = self.env['odoocms.timetable.schedule'].search([
				('batch_id', '=', self.batch_id.id)]).filtered(
				lambda l: weekdays in l.week_day_ids)
			
			for schedule in schedules:
				if dt not in pub_holiday:
					data = {
						'class_id': schedule.class_id.id,
						'faculty_id': schedule.faculty_id.id,
						'date_schedule': dt,
						'date_class': dt,
						'time_from':schedule.time_from,
						'time_to':schedule.time_to,
					}
					att_class = self.env['odoocms.class.attendance'].create(data)
					if att_class:
						att_class.create_attendance_lines()
						att_classes += att_class
			dt = dt + relativedelta(days=1)
			
		if att_classes:
			class_list = att_classes.mapped('id')
			return {
				'domain': [('id', 'in', class_list)],
				'name': _('Scheduled Classes'),
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'odoocms.class.attendance',
				'view_id': False,
				'type': 'ir.actions.act_window'
			}
		else:
			return {'type': 'ir.actions.act_window_close'}



