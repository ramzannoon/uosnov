import pdb
from odoo import api, fields, models, _
from datetime import date, datetime, timedelta

import logging

_logger = logging.getLogger(__name__)


class ReportStudentData(models.AbstractModel):
    _name = 'report.odoocms_exam.report_student_grades'
    _description = 'Student Data Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        if data and data.get('form', False):
            term_id = data['form']['term_id'][0]


        data.get('abc','-')

        
        #     plan_id = data['form']['plan_id'][0]
        #     date_from = data['form']['date_from']
        #     date_to = data['form']['date_to']
        #     docs = self.env['compensation.achievement'].search([
        #         ('partner_id', '=', partner_id), ('plan_id', '=', plan_id),
        #         ('date_from', '<=', date_to), ('date_to', '>=', date_from)
        #     ])
        # elif docids:
        
        students = self.env['odoocms.student'].search([])
        st_data = []
        for student in students:
            data_dic = {
                'student': student,
                'A': len(self.env['odoocms.student.course'].search([('student_id','=',student.id),('term_id','=',term_id),('grade','=','A')])),
                'B': len(self.env['odoocms.student.course'].search([('student_id', '=', student.id),('term_id','=',term_id), ('grade', '=', 'B')])),
                'C': len(self.env['odoocms.student.course'].search([('student_id', '=', student.id),('term_id','=',term_id), ('grade', '=', 'C')])),
                'D': len(self.env['odoocms.student.course'].search([('student_id', '=', student.id),('term_id','=',term_id), ('grade', '=', 'D')])),
                'F': len(self.env['odoocms.student.course'].search([('student_id', '=', student.id),('term_id','=',term_id), ('grade', '=', 'F')])),
            }
            st_data.append(data_dic)
        report = self.env['ir.actions.report']._get_report_from_name('odoocms.odoocms_exam.report_student_data')
        docargs = {
            # 'doc_ids': docids,
            'students': st_data,
            # 'doc_model': report.model,
            # 'data': data,
        }
        return docargs
