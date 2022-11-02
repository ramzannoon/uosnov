from odoo import http
import json
from odoo.http import request
from odoo.addons.odoocms_faculty_portal.controllers import main as faculty_main
from datetime import date, datetime, timedelta
import re
import base64

class FacultyProject(http.Controller):

    # for tickets of projects
    @http.route(['/faculty/projects'], type='http', auth="user", website=True)
    def faculty_project(self, id=0, date_begin=None, date_end=None, sortby=None, **kw):
        values, success, faculty_staff = faculty_main.prepare_portal_values(request)
        if not success:
            return request.render("odoocms_faculty_portal.faculty_error", values)

        project_ids = http.request.env['odoocms.student.project'].sudo().search(
            [('supervisor', '=', faculty_staff.id), ('state', '=', 'accept')])

        # ('co_supervisor', '=', faculty_staff.id),
        # term_ids = term_ids.sorted(key=lambda r: r.id, reverse=True)
        # terms = []
        # data = terms

        color = ['md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700',
                 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                 'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800',
                 'md-bg-deep-orange-A200', 'md-bg-brown-400']

        values.update({
            'projects': project_ids or False,
            'rechecking_requests': False,
            # These are for breadcrumbs
            'active_menu': 'projects',
            'color': color
        })
        return request.render("odoocms_spm.faculty_portal_projects", values)

    # single project details
    @http.route(['/faculty/project/detail/id/<int:id>'], type='http', auth="user", website=True)
    def faculty_project_details(self, id=0, date_begin=None, date_end=None, sortby=None, **kw):
        try:
            values, success, faculty_staff = faculty_main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)

            if id != 0:
                domain = [('id', '=', id),]
                project = request.env['odoocms.student.project'].sudo().search(domain)
                unselected_milestones = request.env['odoocms.student.project.milestone'].sudo().search(
                    [('id', '!=', project.selected_milestone_ids.milestone_id.ids)])
                centralized_milestones = request.env['odoocms.student.project.milestone'].sudo().search([])
                # if not project:
                #     values = {
                #         'header': 'Error!',
                #         'error_message': 'Project detail does not exists!',
                #     }
                #     return request.render("odoocms_faculty_portal.faculty_error", values)
                AT = kw.get('AT')
                print(project.project_document_ids)
                values.update({
                    'project': project,
                    'selected_milestones': project.selected_milestone_ids or False,
                    'documents': project.project_document_ids or False,
                    'unselected_milestones': unselected_milestones or False,
                    'centralized_milestones': centralized_milestones or False,
                    'company': request.env.user.company_id,
                    'AT': AT,
                })
                return request.render("odoocms_spm.faculty_portal_project_detail", values)
            else:
                values = {
                    'header': 'Error!',
                    'error_message': 'Nothing Found!',
                }
                return request.render("odoocms_faculty_portal.faculty_error", values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)

    # faculty feedback general
    @http.route(['/project/faculty/feedback'], type='http', auth="user", website=True, method=['POST'],
                csrf=False)
    def facultyprojectfeedback(self, **kw):

        try:
            values, success, faculty_staff = faculty_main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            project_id = request.httprequest.form.getlist('project_id')
            message = request.httprequest.form.getlist('submited_message')
            project = request.env['odoocms.student.project'].sudo().search([('id', '=', project_id[0])])

            # message = kw['submit_message'] or False

            if project.supervisor_feedback:
                project.supervisor_feedback += '<br>' + message[0]
                values = {
                    'supervisor_feedback': project.supervisor_feedback
                }
            else:
                values = {
                    'supervisor_feedback': message
                }
            if project:
                project.sudo().write(values)
            values = {}
            data = {}
        except Exception as e:
            values = {
                'error_message': e or False
            }

        data = json.dumps(data)
        return data


    # supervisor_meeting_link
    @http.route(['/project/faculty/meeting/link'], type='http', auth="user", website=True, method=['POST'],
                csrf=False)
    def facultyprojectmeetingnotification(self, **kw):

        try:
            values, success, faculty_staff = faculty_main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)

            project_id = request.httprequest.form.getlist('project_id')
            link = request.httprequest.form.getlist('link')
            project = request.env['odoocms.student.project'].sudo().search([('id', '=', project_id[0])])

            notification = request.env['cms.notification'].sudo().search([])

            notification_values = {}
            User_ids = []

            for student in project.student_ids:
                if student.user_id:
                    User_ids.append(student.user_id.id)
                    # notification_values['recipient_ids'] = [(6, 0, User_ids)]
            notification_values = {
                'recipient_ids': User_ids,
                'description': link[0],
                'allow_preview': True,
                'name': 'Supervisor and Student Meeting',
                'visible_for': 'student',
                'alert': True,
                'expiry': date.today() + timedelta(7),
                'url':link[0]

            }
            notification.sudo().create(notification_values)
            values = {
                'supervisor_meeting_link': link[0]
            }
            if project:
                project.sudo().write(values)
            values = {}
            notification_values = {}
            data = {}
        except Exception as e:
            values = {
                'error_message': e or False
            }
        data = json.dumps(data)
        return data

    # add milestone selected
    @http.route(['/faculty/project/milestone/add'], type='http', auth="user", website=True,
                method=['GET', 'POST'],
                csrf=False)
    def project_milestone_add(self, **kw):
        try:
            values, success, faculty_staff = faculty_main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)

            milestone_names = request.httprequest.form.getlist('milestone_name')
            milestone_orignal_ids = request.httprequest.form.getlist('milestone_orignal_id')
            project_id = request.httprequest.form['project_id']
            project = request.env['odoocms.student.project'].sudo().search([('id', '=', project_id)])
            added_milestones = request.env['odoocms.student.project.milestone'].sudo().search([('id', 'in', milestone_orignal_ids)])
            milestone_line = request.env['odoocms.student.project.checklist.lines'].sudo().search([])


            data = {
                'duplication': 'False'
            }
            added_milestones_list =  []
            for rec in added_milestones:
                if rec.id in milestone_line.milestone_id.ids:
                    data ={
                        'duplication':'True'
                    }
                else:
                    added_milestones_list.append(rec.id)
            values = {}
            if data['duplication'] == 'False':
                for i in range(len(milestone_names)):
                    values = {
                        'milestone_id':added_milestones_list[i],
                        'project_id': project.id
                    }
                    milestone_line.sudo().create(values)
                    values = {}

                    data = json.dumps(data)
                return data
            else:
                return data
            # return request.redirect('/faculty/project/detail/id/' + project_id)


        except Exception as e:
            values = {
                'error_message': e or False
            }
        return http.request.render('odoocms_faculty_portal.faculty_error', values)

    # attach milestone datatable
    @http.route(['/faculty/project/milestone/update'], type='http', auth="user", website=True, method=['GET', 'POST'],
                csrf=False)
    def project_milestone_update(self, **kw):
        try:
            values, success, faculty_staff = faculty_main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)

            names = request.httprequest.form.getlist('name')
            start_dates = request.httprequest.form.getlist('start_date')
            end_dates = request.httprequest.form.getlist('end_date')
            actives = request.httprequest.form.getlist('completed_check')
            milestones = request.httprequest.form.getlist('milestone_id')

            project_id = request.httprequest.form['project']
            project = request.env['odoocms.student.project'].sudo().search([('id', '=', project_id)])
            values = {}
            milestone_line = request.env['odoocms.student.project.checklist.lines'].sudo().search([])
            for rec in project.selected_milestone_ids:
                rec.unlink()
            for i in range(len(names)):
                values = {
                    'milestone_id': milestones[i],
                    'start_date': start_dates[i] or False,
                    'end_date': end_dates[i] or False,
                    'project_id': project.id
                }
                milestone_line.sudo().create(values)
                values = {}
            return request.redirect('/faculty/project/detail/id/'+project_id)


        except Exception as e:
            values = {
                'error_message': e or False
            }
        return http.request.render('odoocms_faculty_portal.faculty_error', values)

    # milestone feedback datatable
    # datatable
    @http.route(['/faculty/project/milestone/feedback'], type='http', auth="user", website=True, method=['GET', 'POST'],
                csrf=False)
    def project_milestone_feedback_update(self, **kw):
        try:
            values, success, faculty_staff = faculty_main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            names = request.httprequest.form.getlist('name')
            feedbacks = request.httprequest.form.getlist('feedback')
            milestones = request.httprequest.form.getlist('milestone_orignal_id')
            project_id = request.httprequest.form['project_id']
            project = request.env['odoocms.student.project'].sudo().search([('id', '=', project_id)])
            values = {}
            feedback_line = request.env['odoocms.spm.feedback.lines'].sudo().search([('milestone_id','=',int(milestones[0])),('project_id', '=', project_id)])
            if feedback_line.feedback:
                feedbacks[0] += '\n'+ str(feedback_line.feedback)
            if feedback_line:
                feedback_line.unlink()
            values = {
                'milestone_id': milestones[0],
                'feedback':feedbacks[0],
                'project_id': project.id
            }
            feedback_line.sudo().create(values)
            data = {}
        except Exception as e:
            values = {
                'error_message': e or False
            }
        data = json.dumps(data)
        return data

        # milestone feedback history datatable
    @http.route(['/faculty/project/milestone/feedback/history'], type='http', auth="user", website=True,
                method=['GET', 'POST'],
                csrf=False)

    def project_milestone_feedback_history(self, **kw):
        try:
            values, success, faculty_staff = faculty_main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            milestones = request.httprequest.form.getlist('milestone_orignal_id')
            project_id = request.httprequest.form['project_id']
            project = request.env['odoocms.student.project'].sudo().search([('id', '=', project_id)])
            values = {}
            feedback_line = request.env['odoocms.spm.feedback.lines'].sudo().search([('milestone_id', '=', int(milestones[0])),('project_id', '=', project.id)])
            if feedback_line.feedback:
                feedback_data = feedback_line.feedback
                cleanr = re.compile('<.*?>')
                cleantext = re.sub(cleanr, '', feedback_data)
                data = {'feedback':cleantext}
                # return request.redirect('/faculty/project/detail/id/'+project_id)
        except Exception as e:
            values = {
                'error_message': e or False
            }
        data = json.dumps(data)
        return data

    # completion check
    @http.route(['/faculty/project/milestone/complete/status'], type='http', auth="user", website=True,
                method=['GET', 'POST'],
                csrf=False)
    def project_milestone_completion(self, **kw):
        try:
            values, success, faculty_staff = faculty_main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)

            start_date = request.httprequest.form.getlist('start_date')
            end_date = request.httprequest.form.getlist('end_date')
            complition_status = request.httprequest.form.getlist('complition_status')
            milestone_orignal_id = request.httprequest.form.getlist('milestone_orignal_id')
            project_id = request.httprequest.form['project_id']
            checklist_line_id = request.httprequest.form['checklist_line_id']
            project = request.env['odoocms.student.project'].sudo().search([('id', '=', project_id)])
            status = complition_status[0] in ("True")

            values = {}
            checklist_line = request.env['odoocms.student.project.checklist.lines'].sudo().search(
                [('id', '=', checklist_line_id)])
            values = {
                'start_date': start_date[0] or False,
                'end_date': end_date[0] or False,
                'milestone_id': milestone_orignal_id[0] or False,
                'complition_status': status,
                'project_id': project.id,
                'complition_date': date.today()
            }
            checklist_line.sudo().write(values)
            values = {}
            data= {}
        except Exception as e:
            values = {
                'error_message': e or False
            }
        data = json.dumps(data)
        return data

    # delete milestone request
    @http.route(['/faculty/project/milestone/remove'], type='http', auth="user", website=True, method=['POST'], csrf=False)
    def deleteMilestone(self, **kw):
        try:
            values, success, faculty_staff = faculty_main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)

            req_id = int(kw.get('id'))
            selected_milestone_id = request.env['odoocms.student.project.checklist.lines'].sudo().search(
                [('id', '=', req_id)])
            if selected_milestone_id:
                selected_milestone_id.unlink()

            data = {}

        except Exception as e:
            data = {
                'status_is': "Error",
                'message': e.args[0],
                'color': '#FF0000'
            }
        data = json.dumps(data)
        return data

    @http.route(['/project/document/download/<int:id>'], type='http', auth="user", website=True, csrf=True)
    def project_attachment(self, id=0, **kw):
        env = http.request.env
        record = env['odoocms.spm.document.lines'].sudo().browse(id)
        status, content, filename, mimetype, filehash = env['ir.http'].sudo()._binary_record_content(record,
                                                                                                     field='attachment_file')
        status, headers, content = env['ir.http'].sudo()._binary_set_headers(status, content, filename, mimetype,
                                                                             unique=False, filehash=filehash,
                                                                             download=True)
        if status != 200:
            return request.env['ir.http'].sudo()._response_by_status(status, headers, content)
        else:
            content_base64 = base64.b64decode(content)
            headers.append(('Content-Length', len(content_base64)))
            response = request.make_response(content_base64, headers)
        return response