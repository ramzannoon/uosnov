import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date , datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
from odoo.http import request
import math

import logging
_logger = logging.getLogger(__name__)

from io import StringIO
import io

def round_half_up(n, decimals=0):
	multiplier = 10 ** decimals
	return math.floor(n*multiplier + 0.5) / multiplier

try:
	import xlwt
except ImportError:
	_logger.debug('Cannot `import xlwt`.')

try:
	import cStringIO
except ImportError:
	_logger.debug('Cannot `import cStringIO`.')

try:
	import base64
except ImportError:
	_logger.debug('Cannot `import base64`.')
	

def str_to_datetime(strdate):
	return datetime.datetime.strptime(strdate, tools.DEFAULT_SERVER_DATE_FORMAT)


class SemesterResult(models.TransientModel):
	_name = 'odoocms.semester.result.wizard'
	_description = 'Semester Result Wizard'

	term_id = fields.Many2one('odoocms.academic.term', 'Academic Term', required=True)
	department_id = fields.Many2one('odoocms.department', 'Department', required=True)
	batch_id = fields.Many2one('odoocms.batch', 'Batch', required=True)
	section_id = fields.Many2one('odoocms.batch.section', 'Section', required=True)


	def make_excel(self):
		workbook = xlwt.Workbook(encoding="utf-8")
		worksheet = workbook.add_sheet("Semester Result Report")
		style_title = xlwt.easyxf("font:height 300; font: name Liberation Sans, bold on,color black; align: horiz center;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour cyan_ega;")
		style_table_header = xlwt.easyxf("font:height 300; font: name Liberation Sans, bold on,color black; align: horiz center;borders: left thin, right thin, top thin, bottom thin;")
		style_table_header11 = xlwt.easyxf("font:height 260; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")

		style_table_header2 = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center;borders: left thin, right thin, top thin, bottom thin;  pattern: pattern solid, fore_colour cyan_ega;")
		style_table_header22 = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")


		style_table_header3 = xlwt.easyxf("font:height 150; font: name Liberation Sans, bold on,color black; align: horiz center;borders: left thin, right thin, top thin, bottom thin;  pattern: pattern solid, fore_colour cyan_ega;")

		style_table_totals = xlwt.easyxf("font:height 150; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour cyan_ega;")
		style_date_col = xlwt.easyxf("font:height 180; font: name Liberation Sans,color black; align: horiz center;borders: left thin, right thin, top thin, bottom thin;")
		style_product_header = xlwt.easyxf("font:height 200; font: name Liberation Sans,bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour silver_ega;")
		style_table_totals2 = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")
		style_clo_col1 = xlwt.easyxf("font:height 180; font: name Liberation Sans,color black; align:horiz center;borders: left thin, right thin, top thin, bottom thin;")
		style_clo_col2 = xlwt.easyxf("font:height 150; font: name Liberation Sans,color black; align:horiz center;borders: left thin, right thin, top thin, bottom thin;")
		style_clo_col_rotation = xlwt.easyxf("font:height 160; font: name Liberation Sans,bold on,color black; align:rotation 90,horiz center,vertical center;borders: left thin, right thin, top thin, bottom thin;")
		style_clo_col_rotation1 = xlwt.easyxf("font:height 150; font: name Liberation Sans,bold on,color black; align:rotation 90,horiz center;borders: left thin, right thin, top thin, bottom thin;")

		worksheet.write_merge(4, 4, 0, 0,"Sr.No", style= style_table_header2)
		worksheet.write_merge(4, 4, 1, 1,"Student Name", style= style_table_header2)
		worksheet.write_merge(4, 4, 2, 2, "Registration No", style=style_table_header2)

		row = 0
		# worksheet.col(0).width = 256 * 20
		worksheet.col(1).width = 256 * 20
		worksheet.col(2).width = 256 * 20

		section = self.batch_id.section_ids.filtered(lambda l: l.id == self.section_id.id)
		current_classes = section.class_ids.filtered(lambda l: l.term_id.id == self.term_id.id)

		weightage_sum = 0
		col = 3
		courses_list = []
		for cl in current_classes:
			worksheet.col(col).width = 256 * 6
			worksheet.write_merge(1, 1, col, col + 1, cl.study_scheme_line_id.subject_id.name, style=style_table_header2)
			worksheet.write_merge(2, 2, col, col + 1, cl.study_scheme_line_id.subject_id.code, style=style_table_header2)
			worksheet.write_merge(3, 3, col, col + 1, cl.study_scheme_line_id.subject_id.weightage, style=style_table_header2)
			worksheet.write(4, col, 'G', style=style_table_header2)
			worksheet.write(4, col + 1, 'GP', style=style_table_header2)
			courses_list.append(cl.study_scheme_line_id.id)
			col += 2
			weightage_sum += cl.study_scheme_line_id.subject_id.weightage

		worksheet.write_merge(1, 1, col, col + 1, 'Semester', style=style_table_header2)
		worksheet.write_merge(2, 3, col, col + 1, 'Total Crs Hr '+ str(weightage_sum), style=style_table_header3)
		worksheet.write(4, col, 'Total GPs', style=style_table_header3)
		worksheet.write(4, col+1, 'SGPA', style=style_table_header3)
		worksheet.write_merge(1, 4, col + 2, col + 2, 'Remarks', style=style_table_header2)
		worksheet.col(col + 2).width = 256 * 20

		r = 5
		st_g_list = []
		sr_no = 1
		for st in section.student_ids:
			SGPA = '-'
			GPs = '-'
			remarks = '-'
			col = 3
			st_g_list = []
			st_gp_list = []
			for course in courses_list:
				st_g_list.append("-")
				st_gp_list.append("-")
			worksheet.write(r, 0, sr_no, style=style_date_col)
			worksheet.write(r, 1, st.name, style=style_date_col)
			worksheet.write(r, 2, st.code, style=style_date_col)
			# worksheet.write(r, 3, st.cgpa, style=style_date_col)
			# worksheet.write(r, 4, st.cgpa, style=style_date_col)

			student_semesters = st.current_semester_ids + st.semester_ids
			semester = student_semesters.filtered(lambda l: l.academic_semester_id.id == self.academic_semester_id.id)
			if semester:
				SGPA = str(round_half_up(semester.sgpa,2))
				GPs = str(round_half_up(semester.grade_points,2))
				remarks = str(semester.remarks)

			# student_sub = self.env['odoocms.student.course'].search([('academic_semester_id', '=', self.academic_semester_id.id), ('student_id', '=', st.id)])
			for sub in semester.student_subject_ids2:
			# for sub in student_sub:
				for c in range(0,len(courses_list)):
					if sub.subject_id.id == courses_list[c]:
						st_g_list[c] = sub.grade
						st_gp_list[c] = sub.grade_points
			for l in range(0,len(st_g_list)):
				worksheet.write(r, col, st_g_list[l], style=style_date_col)
				worksheet.write(r, col+1, st_gp_list[l], style=style_date_col)
				col += 2

			worksheet.write(r, col, GPs, style=style_date_col)
			worksheet.write(r, col + 1, SGPA, style=style_date_col)
			worksheet.write(r, col + 2, remarks, style=style_date_col)
			r += 1
			sr_no += 1
		company_id = self.env.user.company_id
		worksheet.write_merge(0, 0, 0, len(st_g_list)*3, company_id.name, style=style_table_header)
		worksheet.row(0).height = 256 * 2

		worksheet.write_merge(1, 2, 0, 2, "Batch: " + self.batch_id.name or "---", style=style_table_header11)

		worksheet.write_merge(3, 3, 0, 2, "Term: "+self.academic_semester_id.name or "---", style=style_table_header22)


		r = r+5
		worksheet.write_merge(r, r, 0, 2, 'Errors and Omissions are expected', style=style_date_col)
		worksheet.write_merge(r, r, 4, 9, 'Result may be declared please', style=style_date_col)

		r = r+5
		worksheet.write_merge(r, r , 0, 3, '________________________', style=style_date_col)
		worksheet.write_merge(r, r, 6, 9, '________________________', style=style_date_col)
		worksheet.write_merge(r, r , 12, 15, '________________________', style=style_date_col)
		r += 1

		worksheet.write_merge(r, r, 0, 3, 'Department Chairmain', style=style_date_col)
		worksheet.write_merge(r, r, 6, 9, 'Dean', style=style_date_col)
		worksheet.write_merge(r, r, 12, 15, 'Voice Chancellor', style=style_date_col)

		r = r + 5
		worksheet.write_merge(r, r, 0, 3, '________________________', style=style_date_col)
		worksheet.write_merge(r, r, 6, 9, '________________________', style=style_date_col)
		worksheet.write_merge(r, r, 12, 15, '________________________', style=style_date_col)

		r = r + 2
		worksheet.write_merge(r, r, 0, 3, 'Computer porgrammer Examination', style=style_date_col)
		worksheet.write_merge(r, r, 6, 9, 'Controller of Examinations', style=style_date_col)
		worksheet.write_merge(r, r, 12, 15, 'Manager IT', style=style_date_col)
		r += 1

		workbook.footer_str = 'Department Chairmain'

		file_data = io.BytesIO()
		workbook.save(file_data)
		wiz_id = self.env['semester.result.save.wizard'].create({
			'data': base64.encodestring(file_data.getvalue()),
			'name': 'SemesterResult.xls'
		})

		return {
			'type': 'ir.actions.act_window',
			'name': 'Semester Result Report Form',
			'res_model': 'semester.result.save.wizard',
			'view_mode': 'form',
			'view_type': 'form',
			'res_id': wiz_id.id,
			'target': 'new'
		}


class Semester_Result_save_wizard(models.TransientModel):
	_name = "semester.result.save.wizard"
	_description = 'Semester Result Save Wizard'
	
	name = fields.Char('filename', readonly=True)
	data = fields.Binary('file', readonly=True)


		








