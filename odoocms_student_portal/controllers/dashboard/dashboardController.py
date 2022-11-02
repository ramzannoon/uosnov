import json
import pdb

from .. import main
from odoo import http
from odoo.http import request
from datetime import date

class Dashboard(http.Controller):
    @http.route(['/student/dashboard'], type='http', auth="user", website=True)
    def home(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)
            partner = request.env.user.partner_id
            # survey_input_ids = http.request.env['survey.user_input'].sudo().search([('partner_id', '=', partner.id)])
            # if survey_input_ids:
            #     for survey in survey_input_ids:
            #         if (survey.state == 'new' or survey.state == 'skip') and survey.survey_id.state == 'open':
            #             return request.redirect('/student/qa/feedback')
                    # elif (survey.state == 'new' or survey.state == 'skip') and survey.survey_id.state == 'close':
                    #     return request.redirect('/student/qa/feedback')

            inprogress_credits = 0
            completed_credits = 0
            for cred in student.course_ids:
                inprogress_credits = cred.credits + inprogress_credits
            for com_cred in student.term_ids:
                completed_credits = com_cred.credits + completed_credits
            #today_classes = http.request.env['odoocms.class.attendance'].sudo().search([])
            terms=[]
            sgpa = []
            cgpa =[]
            att_class=[]
            att_per=[]

            for term in student.term_ids:
                terms.append(term.term_id.name)
                sgpa.append(term.sgpa)
                cgpa.append(term.cgpa)
            student_subjects = http.request.env['odoocms.student.course'].sudo().search([
                ('student_id', '=', student.id), ('term_id', '=', values['term'].id)])
            for att in student_subjects:
                att_class.append(att.primary_class_id.name)
                att_per.append(att.attendance_percentage)
            # today_classes = []
            # for p_class in student_subjects:
            #     for c_class in p_class.component_ids:
            #         today_classes.append(c_class.att_line_ids.filtered(lambda l: l.student_id.id == student.id ))
            #
            # attendances = http.request.env['odoocms.class.attendance'].sudo().search([ ('date_class', '=', date.today())])
            # for attendance in attendances:
            #     attendance_classes = attendance.class_id.registration_component_ids.filtered(lambda l: l.student_id.id == student.id)
            attendances = http.request.env['odoocms.class.attendance'].sudo().search([('date_class', '=', date.today())])
            today_classes=[]
            for attendance in attendances:
                classes = attendance.attendance_lines.filtered(lambda l: l.student_id.id == student.id)
                if classes:
                    today_classes.append(classes)
            # many to many relation
            #sql = """SELECT DISTINCT project_id FROM project_student_rel WHERE student_id = """+str(student.id)
            #request.cr.execute(sql)
            #returned_ids = request.cr.fetchall()
            #studentsList = []
            #for rec in returned_ids:
            #    studentsList.append(rec[0])
            #student_projects = http.request.env['odoocms.student.project'].sudo().search([('id', 'in', studentsList)])
            values.update({
                'inprogress_credits': inprogress_credits,
                'completed_credits': completed_credits,
                'today_classes':today_classes or False,
                'terms': terms,
                'sgpa':sgpa,
                'cgpa': cgpa,
                'att_class': att_class,
                'att_per':att_per,
                #'student_projects': student_projects
            })
            return http.request.render('odoocms_student_portal.student_dashboard_new',values)
        except Exception as e:
            data = {
                #'student_id': student.id,
                'name': 'dashboard',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)

    @http.route(['/student/dashboard/new'], type='http', auth="user", website=True)
    def homeDasch(self, **kw):
        try:
            values, success, student = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_student_portal.student_error", values)

            inprogress_credits = 0
            completed_credits = 0
            for cred in student.course_ids:
                inprogress_credits = cred.credits + inprogress_credits
            for com_cred in student.term_ids:
                completed_credits = com_cred.credits + completed_credits
            #today_classes = http.request.env['odoocms.class.attendance'].sudo().search([])
            terms=[]
            sgpa = []
            cgpa =[]
            att_class=[]
            att_per=[]
            for term in student.term_ids:
                terms.append(term.term_id.name)
                sgpa.append(term.sgpa)
                cgpa.append(term.cgpa)

            student_subjects = http.request.env['odoocms.student.course'].sudo().search([
                ('student_id', '=', student.id), ('term_id', '=', values['term'].id)])
            for att in student_subjects:
                att_class.append(att.primary_class_id.name)
                att_per.append(att.attendance_percentage)
            # today_classes = []
            # for p_class in student_subjects:
            #     for c_class in p_class.component_ids:
            #         today_classes.append(c_class.att_line_ids.filtered(lambda l: l.student_id.id == student.id ))
            #
            # attendances = http.request.env['odoocms.class.attendance'].sudo().search([ ('date_class', '=', date.today())])
            # for attendance in attendances:
            #     attendance_classes = attendance.class_id.registration_component_ids.filtered(lambda l: l.student_id.id == student.id)


            attendances = http.request.env['odoocms.class.attendance'].sudo().search([('date_class', '=', date.today())])

            today_classes=[]
            for attendance in attendances:
                classes = attendance.attendance_lines.filtered(lambda l: l.student_id.id == student.id)
                if classes:
                    today_classes.append(classes)
            # many to many relation
            #sql = """SELECT DISTINCT project_id FROM project_student_rel WHERE student_id = """+str(student.id)
            #request.cr.execute(sql)
            #returned_ids = request.cr.fetchall()
            #studentsList = []
            #for rec in returned_ids:
            #    studentsList.append(rec[0])
            #student_projects = http.request.env['odoocms.student.project'].sudo().search([('id', 'in', studentsList)])


            values.update({
                'inprogress_credits': inprogress_credits,
                'completed_credits': completed_credits,
                'today_classes':today_classes or False,
                'terms': terms,
                'sgpa':sgpa,
                'cgpa': cgpa or False,
                'att_class': att_class,
                'att_per':att_per,
                #'student_projects': student_projects
            })
            return http.request.render('odoocms_student_portal.student_dashboard_new',values)
        except Exception as e:
            data = {
                #'student_id': student.id,
                'name': 'dashboard',
                'description': e or False,
                'state': 'submit',
            }
            request.env['odoocms.error.reporting'].sudo().create(data)
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_student_portal.student_error', values)