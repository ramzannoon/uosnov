from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError
import logging
import random

from numpy import *

_logger = logging.getLogger(__name__)


class sittingTypeWiz(models.TransientModel):
    _name = 'sitting.type.wiz'
    _description = 'Sitting Type'

    @api.model
    def get_examination_center(self):
        if self.env.context.get('active_model', False) == 'odoocms.exam.center.assignment' and self.env.context.get(
                'active_id', False):
            return self.env.context['active_id']

    type = fields.Selection(string='Type', selection=[('registration', 'Reg Wise'), ('shuffle', 'Shuffle'), ],
                            default="registration")
    examination_center_id = fields.Many2one('odoocms.exam.center.assignment', string="Examination Center",
                                            default=get_examination_center)

    def generate_sitting_plan(self):
        print(self)


        if self.type == 'registration':
            students = self.env['odoocms.student'].search([('id', 'in', self.examination_center_id.student_ids.ids)])
            datesheet = self.env['odoocms.datesheet'].search(
                [('department_id', 'in', self.examination_center_id.campus_id.institute_ids.department_ids.ids),
                 ('term_id', '=', self.examination_center_id.term_id.id)])

            datesheet_lines = self.env['odoocms.datesheet.line'].search(
                [('datesheet_id', 'in', datesheet.ids)])

            date_list = []
            filtered_date_list = []
            sorted_date_list = []
            sitting_plan_obj = self.env['odoocms.exam.sitting']
            sitting_plan_line_obj = self.env['odoocms.exam.sitting.line']
            for line in datesheet_lines:
                date_list.append(line.date)
            filtered_date_list = list(set(date_list))
            sorted_date_list = sorted(filtered_date_list)
            counter = 0

            for date in sorted_date_list:

                sitting_plan_data = {
                    'exam_center_id': self.examination_center_id.id,
                    'term_id': self.examination_center_id.term_id.id,
                    'date': date,
                }
                record = sitting_plan_obj.sudo().create(sitting_plan_data)

                datesheet_date_line = datesheet_lines.filtered(
                    lambda l: l.date == date)
                filtered_students = students.filtered(lambda l: l.batch_id.id == datesheet_date_line.batch_id.id)

                # here
                area = []
                if len(filtered_students) > 1:
                    total_sitting = 0

                    center_lines = self.examination_center_id.center_id.center_line
                    for line in center_lines:
                        type = line.type.name
                        row = line.row
                        col = line.col
                        sitting = row * col
                        total_sitting = total_sitting + sitting
                        # if total_sitting < len(filtered_students):
                        #     raise UserError("No enough Capacity Available in " + type)
                        # else:
                        # if total_sitting > len(filtered_students):
                        for c in range(col):
                            for r in range(row):
                                area.append(type + '-' + 'C' + str(c + 1) + '-' + 'R' + str(r + 1))

                counter = counter + len(filtered_students)
                for student, a in zip(filtered_students.sorted(key=lambda s: s.id, reverse=False), area):
                    if student:
                        datesheet_date_line1 = datesheet_lines.filtered(
                            lambda l: l.date == date and l.batch_id.program_id.id == student.program_id.id)
                        sitting_plan_line_data = {
                            'student_id': student.id,
                            'sitting_number': a,
                            # 'course': datesheet_date_line1.course_id_1.name,
                            'course': datesheet_date_line1.course_id.name,
                            'sitting_id': record.id
                        }
                        line_record = sitting_plan_line_obj.create(sitting_plan_line_data)

        # course_id

        elif self.type == 'shuffle':

            # raise UserError("Shuffle mechanism facility Will be Available Soon")

            students = self.env['odoocms.student'].search(

                [('id', 'in', self.examination_center_id.student_ids.ids)])

            datesheet = self.env['odoocms.datesheet'].search(

                [('campus_id', 'in',

                  self.examination_center_id.campus_id.ids),

                 ('term_id', '=', self.examination_center_id.term_id.id)])

            date_list = []

            filtered_date_list = []

            sorted_date_list = []

            student_order_list = []

            program_list = []

            for program in datesheet.program_id:
                program_list.append(program)

            datesheet_lines = self.env['odoocms.datesheet.line'].search(

                [('datesheet_id', 'in', datesheet.ids)])

            sitting_plan_obj = self.env['odoocms.exam.sitting']

            sitting_plan_line_obj = self.env['odoocms.exam.sitting.line']

            for line in datesheet_lines:
                date_list.append(line.date)

            filtered_date_list = list(set(date_list))

            sorted_date_list = sorted(filtered_date_list)

            counter = 0

            for date in sorted_date_list:

                sitting_plan_data = {

                    'exam_center_id': self.examination_center_id.id,

                    'term_id': self.examination_center_id.term_id.id,

                    'date': date,

                }

                record = sitting_plan_obj.sudo().create(sitting_plan_data)

                datesheet_date_line = datesheet_lines.filtered(

                    lambda l: l.date == date)

                filtered_students = students.filtered(

                    lambda l: l.batch_id.id in datesheet_date_line.batch_id.ids)

                # here

                area = []

                if len(filtered_students) > 1:

                    total_sitting = 0

                    sitting_area = []

                    center_lines = self.examination_center_id.center_id.center_line

                    for line in center_lines:

                        type = line.type.name

                        row = line.row

                        col = line.col

                        sitting = row * col

                        total_sitting = total_sitting + sitting

                        # if total_sitting < len(filtered_students):

                        #     raise UserError("No enough Capacity Available in " + type)

                        # else:

                        # if total_sitting > len(filtered_students):

                        for c in range(col):

                            for r in range(row):
                                area.append(type + '-' + 'C' + str(random.randint(1, 10)) + '-' + 'R' + str(
                                    random.randint(1, 10)))

                                # program = program_list[c]

                                # for student in filtered_students:

                                #     while student.program_id.id == program:

                                #         student_order_list.append(student)

                                # continue

                            # for program  in program_list:

                counter = counter + len(filtered_students)

                for student, area in zip(filtered_students.sorted(key=lambda s: s.id, reverse=False), area):

                    if student:
                        datesheet_date_line1 = datesheet_lines.filtered(
                            lambda l: l.date == date and l.batch_id.program_id.id == student.program_id.id)

                        sitting_plan_line_data = {

                            'student_id': student.id,

                            'sitting_number': area,

                            'course': datesheet_date_line1.course_id.name,

                            'sitting_id': record.id

                        }

                        line_record = sitting_plan_line_obj.create(sitting_plan_line_data)