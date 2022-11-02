import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
from datetime import date , datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time


class OdooCMSExamAssignSemesterRemarksWiz(models.TransientModel):
    _name = 'odoocms.exam.assign.semester.remarks.wiz'
    _description = 'Exam Assign Semester Remarks'


    batch_id = fields.Many2one('odoocms.batch', string='Batch', required=True)
    # term_id = fields.Many2one('odoocms.academic.term','Academic Semester')
    

    def assign_remarks(self):
        self.ensure_one()
        freshman_semesters = self.env.user.company_id.freshman_semesters
        student_ids = self.env['odoocms.student'].search([('batch_id','=',self.batch_id.id)])
        for st in student_ids:

            #For warning
            student_semester_ids = self.env['odoocms.student.semester'].search([('student_id','=',st.id)])
            if student_semester_ids:
                grades = "Grades "
                subjects  = "in "
                for sub in student_semester_ids.mapped('student_subject_ids2'):
                    if (sub.grade in ('XF','F')) or (sub.semester_id in freshman_semesters and sub.grade in ('D+','D','D-','F','XF')):
                        st.remarks_type = 'warning'
                        st.remarks = 'Warning with Grade.'+sub.grade+" in "+ (sub.subject_id.subject_id.name or "")
                        break

                student_semester_id = student_semester_ids.filtered(lambda l:l.term_id == st.term_id)
                if student_semester_id:
                    for sub in student_semester_id.student_subject_ids2:
                        if sub.grade in ('XF',"F"):
                            grades += sub.grade+","
                            subjects += sub.subject_id.subject_id.name+"," or "Draft Subject,"
                    st.remarks = "Warning with "+grades+subjects
                    st.remarks_type = 'warning'
                    student_semester_id.remarks = "Warning with "+grades+subjects
                    student_semester_id.remarks_type = 'warning'

                    if (student_semester_id.sgpa < 2 or student_semester_id.cgpa < 0):
                        student_semester_id.remarks = "Warning with less GPA."
                        st.remarks = "Warning with less GPA."
                        st.remarks_type = 'warning'
                        student_semester_id.remarks = "Warning with less GPA."
                        student_semester_id.remarks_type = 'warning'

            # For probation
            first_semester =  self.env['odoocms.semester'].search([('number','=',1)])
            student_semester_ids = self.env['odoocms.student.semester'].search([
                ('student_id', '=', st.id)]).filtered(lambda l:l.semester_id != first_semester)
            for sem in student_semester_ids:
                if sem.cgpa < 2:
                    st.remarks = "Probation with less GPA."
                    st.remarks_type = 'probation'
                    current_st_sem = sem.filtered(lambda l:l.semester_id == st.semester_id)
                    current_st_sem.remarks = "Probation with less GPA."
                    current_st_sem.remarks_type = 'probation'
                    break

            # For suspension
            student_semester_id = self.env['odoocms.student.semester'].search([('student_id', '=', st.id),('term_id', '=', st.term_id.id)])
            absent_count = 0
            dt = date.today()
            attendance_lines = self.env['odoocms.class.attendance.line'].search([('student_id', '=', st.id),('term_id', '=', st.term_id.id)]).sorted(key=lambda r: r.date_class, reverse=False)
            present_list = attendance_lines.mapped('present')

            for p in present_list:
                if absent_count >30:
                    break
                if p == False:
                    absent_count += 1
                else:
                    absent_count = 0
            if student_semester_id and student_semester_id.student_subject_ids2.filtered(lambda l:l.attendance_percentage <75 or absent_count>30):
                st.remarks = "Suspension with less Attendance."
                st.remarks_type = 'suspension'
                current_st_sem = self.env['odoocms.student.semester'].search([('student_id', '=', st.id),('term_id','=',st.term_id.id)])
                if current_st_sem:
                    current_st_sem.remarks = "Suspension with less Attendance."
                    current_st_sem.remarks_type = 'suspension'

            # For Withdraw
            student_semester_ids = self.env['odoocms.student.semester'].search([('student_id', '=', st.id)])
            first_semester_id = student_semester_ids.filtered(lambda l: l.semester_id == first_semester)

            first_six_semesters = self.env['odoocms.semester'].search([('number', 'in', (1, 2, 3, 4, 5, 6))])
            f_s_st_sem_ids = self.env['odoocms.student.semester'].search([
                ('student_id', '=', st.id)]).filtered(lambda l: l.semester_id in first_six_semesters)

            if student_semester_ids and first_semester_id:
                if len( student_semester_ids.mapped('student_subject_ids2').filtered(lambda l: l.grade in ('F','XF')) ) >= 10 or len(first_semester_id.student_subject_ids2.filtered(lambda l: l.grade in ('F','XF'))) >= 5:
                    st.remarks = "Withdrawal."
                    st.remarks_type = 'withdraw'
                    current_st_sem = student_semester_ids.filtered(lambda l: l.term_id == st.term_id)
                    current_st_sem.remarks = "Withdrawal."
                    current_st_sem.remarks_type = 'withdraw'

            probation_count = 0
            for sm in f_s_st_sem_ids:
                if probation_count >=3:
                    st.remarks = "Withdrawal with three or more consecutive probation."
                    st.remarks_type = 'withdraw'
                    current_st_sem = student_semester_ids.filtered(lambda l: l.term_id == st.term_id)
                    current_st_sem.remarks = "Withdrawal with three or more consecutive probation."
                    current_st_sem.remarks_type = 'withdraw'
                    break
                if sm.remarks_type == 'probation':
                    probation_count += 1
                else:
                    probation_count = 0

        return True



