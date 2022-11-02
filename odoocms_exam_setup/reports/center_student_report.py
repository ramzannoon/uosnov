import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta

import logging
_logger = logging.getLogger(__name__)


class CenterStudentCountReport(models.AbstractModel):
    _name = 'report.odoocms_exam_setup.exam_center_student_report'
    _description = 'Center Student Count Report'


    @api.model
    def _get_report_values(self, docsid, data=None):
        company_id = self.env.user.company_id
        center_assigned = self.env['odoocms.exam.center.assignment'].search([('center_id','in',data['form']['center_ids'])])

        final_list = []
        exam_dates = []
        for center in center_assigned:
            program_list = []
            dates_filterd_list = []
            program_filterd_list= []
            student_count = 0
            row_student_total = 0

            exam_sitting = self.env['odoocms.exam.sitting'].search([('exam_center_id', '=', center.id)])
            exam_sitting_line = self.env['odoocms.exam.sitting.line'].search([('sitting_id', 'in', exam_sitting.ids)])
            for sitting in exam_sitting:
                exam_dates.append(sitting.date)
            for line in exam_sitting_line:
                program_list.append(line.student_id.program_id.id)
                # student_count = student_count + 1
            dates_filterd_list = list(set(exam_dates))
            program_filterd_list = list(set(program_list))
            dates_filterd_list.sort()
            programs = self.env['odoocms.program'].search([('id', 'in', program_filterd_list)])

            for program  in programs:
                list_data =[]
                for date in dates_filterd_list:
                    student_exam_sitting = self.env['odoocms.exam.sitting'].search([('exam_center_id', '=', center.id),('date','=',date)])
                    student_exam_sitting_line = self.env['odoocms.exam.sitting.line'].search([('sitting_id', 'in', student_exam_sitting.ids)])
                    student = student_exam_sitting_line.filtered(lambda x : x.student_id.program_id.id == program.id)
                    student_count = len(student)

                    data = {
                        'date' : date,
                        'program':program.name + ' ' + '(' + str(center.center_id.code) +')',
                        'student_count' : student_count
                    }
                    list_data.append(data)
                final_list.append(list_data)
                print(data)
        docargs = {
            'doc_ids': [],
            'company_id':company_id or False,
            'final_list': final_list,
            'center_student': False,
            'dates_filterd_list': dates_filterd_list or False,
        }
        return docargs



