

from datetime import date, datetime, timedelta
from odoo import http
from . import main
from odoo.http import request
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal

from datetime import date
import json
import pdb
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

import logging
_logger = logging.getLogger(__name__)


class facultyClassPortal(CustomerPortal):

    @http.route(['/faculty/classes'], type='http', auth="user", website=True)
    def facultyClasses(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)

            result_classes = http.request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id),('term_id','=',values['config_term'])])

            color = ['md-bg-deep-purple-A200', 'md-bg-deep-orange-600', 'md-bg-green-800', 'md-bg-cyan-700', 'md-bg-light-blue-600', 'md-bg-deep-orange-900', 'md-bg-indigo-500', 'md-bg-brown-500',
                     'md-bg-blue-grey-500', 'md-bg-deep-purple-300', 'md-bg-teal-800', 'md-bg-purple-500', 'md-bg-pink-800', 'md-bg-deep-orange-A200', 'md-bg-brown-400']
            
            values.update({
                'result_classes': result_classes or False,
                'rechecking_requests': False,
                
                # These are for breadcrumbs
                'active_menu': 'result',
                'color': color,
            })
            return http.request.render('odoocms_faculty_portal.faculty_portal_result', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)

    @http.route(['/faculty/result/view/id/<int:id>'], type='http', auth="user", website=True)
    def faculty_view_grades(self, id=0, date_begin=None, date_end=None, sortby=None, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)

            if id != 0:
                domain = [
                    ('id', '=', id),
                    ('faculty_staff_id', '=', faculty_staff.id),
                ]
                result_class = request.env['odoocms.class'].sudo().search(domain)
                if not result_class:
                    values = {
                        'header': 'Error!',
                        'message': 'Nothing Found!',
                    }
                    return request.render("odoocms_faculty_portal.faculty_error", values)

                assessment_list = []
                for st in result_class.registration_component_ids:
                    marks = []
                    for assessment in result_class.assessment_ids:
                        assessment_lines = request.env['odoocms.assessment.line'].sudo().search([('class_id', '=', result_class.id),('assessment_id', '=', assessment.id)])
                        assessment_line = assessment_lines.filtered(lambda l: l.student_id == st.student_id)
                        if assessment_line:
                            marks.append({'assessment_line_id': assessment_line.id, 'obtained_marks': assessment_line.obtained_marks})
                        else:
                            marks.append({'assessment_line_id': assessment_line.id, 'obtained_marks': 0.0})
                    student_data = {'student': st.student_id.name, 'id': st.student_id.id_number, 'data': marks}
                    assessment_list.append(student_data)

                assessment_sheet = []
                for st in result_class.registration_component_ids:
                    student_list = [{'student': st.student_id.name, 'data': []}]


                today = date.today()
                assessment_data = {
                    "header": [],
                    "data": []
                }
                header_list = ["Student Name", "Reg No"]
                data_list = []

                student_data_list = ["-", "-"]
                for assessment_type in result_class.assessment_component_ids:
                    header_list.append(assessment_type.assessment_type_id.name)
                    student_data_list.append("-")
                header_list.append("GPA")
                header_list.append("Grade")
                assessment_data['header'] = header_list

                #my edits
                assessment_list2 = []
                for st in result_class.registration_component_ids:
                    marks = []
                    for assessment in result_class.assessment_ids:
                        assessment_lines = request.env['odoocms.assessment.line'].sudo().search([('class_id', '=', result_class.id), ('assessment_id', '=', assessment.id)])
                        assessment_line = assessment_lines.filtered(lambda l: l.student_id == st.student_id)
                        if assessment_line:
                            marks.append({'assessment_id': assessment, 'obtained_marks': assessment_line.obtained_marks, 'student_id': st.student_id.id})
                        else:
                            marks.append({'assessment_id': assessment, 'obtained_marks': 0.00, 'student_id': st.student_id.id})
                    student_data = {'student': st.student_id.name, 'id': st.student_id.id_number, 'data': marks}
                    assessment_list2.append(student_data)
                    # assessment_list.append('sulman shaukat')
                
                
                values.update({
                    'result_class': result_class,
                    'batch_class': result_class,
                    'assessment_data': assessment_data,
                    # For breadcrumbs
                    'page': 'view_result',
                    'view_result_class': result_class,
                    'student_assessment_data': assessment_list,
                    # my edits
                    'add_result_class': result_class,
                    'student_assessment_data_create': assessment_list2,
                    'today_date': today,
                    
                })
                
                if result_class.primary_class_id:
                    primary_class_id = request.env['odoocms.class'].sudo().search([('primary_class_id', '=', result_class.primary_class_id.id)])
                    values['batch_class'] = primary_class_id

                    for st in result_class.registration_component_ids:
                        student_data_list[0] = st.student_id.name
                        student_data_list[1] = st.student_id.code

                        i = 2
                        for class_ass in result_class.assessment_component_ids:
                            student_ass_summary = st.assessment_summary_ids.filtered(lambda l: l.assessment_component_id == class_ass)
                            if student_ass_summary:
                                student_data_list[i] = round((student_ass_summary.percentage * class_ass.weightage) / 100, 2)
                            else:
                                student_data_list[i] = "-"
                            i += 1
                        # student_data_list.append(st.gpa or 0)
                        # student_data_list.append(st.grade or "-")
                        data_list.append(student_data_list)

                        student_data_list = ["-", "-"]
                        for assessment_type in result_class.assessment_component_ids:
                            student_data_list.append("-")

                    assessment_data['data'] = data_list
                    values['assessment_data'] = assessment_data

                return request.render("odoocms_faculty_portal.faculty_portal_result_detail", values)
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

    @http.route(['/faculty/result/configure/id/<int:id>'], type='http', auth="user", website=True)
    def faculty_configure_grades(self, id=0, date_begin=None, date_end=None, sortby=None, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
            result_class = http.request.env['odoocms.class'].sudo().sudo().search([('id','=',id),('faculty_staff_id', '=', faculty_staff.id)])


            # if not result_classes:
            #     values = {
            #         'header': 'Error!',
            #         'message': 'Nothing Found!',
            #     }
            #     return request.render("odoocms_faculty_portal.faculty_portal_submission_message", values)

            # rechecking_requests = http.request.env['odoocms.request.subject.rechecking'].sudo().sudo().search([('state', '=', 'approve')])
           
            values.update ({
                'result_class': result_class,
                # 'rechecking_requests':rechecking_requests,
                'rechecking_requests': False,
                
                # These are for breadcrumbs
                'active_menu': 'result',
            })
            return http.request.render('odoocms_faculty_portal.faculty_portal_result_confg', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)
        
    @http.route('/faculty/class/result/save', type='http', auth="user", method=['POST'], website=True, csrf=False)
    def save_class_result(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
            class_id = kw.get('result_class', False)
            class_id = request.env['odoocms.class'].sudo().search([('id','=',class_id)])
            if not class_id or class_id.faculty_staff_id != faculty_staff:
                values = {
                    'header': 'Error!',
                    'error_message': 'Nothing Found!',
                }
                return request.render("odoocms_odoocms_faculty_portal.faculty_error", values)

            for st in class_id.registration_component_ids:
                for assessment in class_id.assessment_ids:
                    key = 'assessment_id_' + str(st.student_id.id) + "_" + str(assessment.id)
                    assessment_lines = request.env['odoocms.assessment.line'].sudo().search([('class_id', '=', class_id.id), ('assessment_id', '=', assessment.id)])
                    assessment_line = assessment_lines.filtered(lambda l: l.student_id == st.student_id)
                    obtained_marks = kw.get(key)

                    # For Summarization of Quizes, Assignments. Mid & Final
                    summary_rec = request.env['odoocms.assessment.summary'].sudo().search(
                        [('class_id', '=', class_id.id), ('student_id', '=', st.student_id.id),
                         ('assessment_component_id', '=', assessment.assessment_component_id.id)])

                    if not summary_rec:
                        summary_vals = {
                            'class_id': class_id.id,
                            'student_id': st.student_id.id,
                            'assessment_component_id': assessment.assessment_component_id.id,
                        }
                        summary_rec = request.env['odoocms.assessment.summary'].sudo().create(summary_vals)

                    if not assessment_line:
                        assessment_line_vals = {
                            'student_id': st.student_id.id,
                            'assessment_id': assessment.id,
                            'summary_id': summary_rec and summary_rec.id or False,
                        }

                        assessment_line = request.env['odoocms.assessment.line'].sudo().create(assessment_line_vals)
                    if obtained_marks and obtained_marks != '':
                        assessment_line.obtained_marks = float(obtained_marks)

            return request.redirect('/faculty/result/view/id/'+ kw.get('result_class', 0))
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)

    @http.route('/faculty/assessment/configure/save', type='http', auth="user", method=['POST'], website=True, csrf=False)
    def assessment_configuration_save(self, **kw):
        try:
            partner = request.env.user.partner_id
            faculty_staff = http.request.env['odoocms.faculty.staff'].sudo().search([('user_partner_id', '=', partner.id)])

            result_class = int(kw.get('result_class', '0'))
            class_id = request.env['odoocms.class'].sudo().search([('id', '=', result_class)])
            if not faculty_staff:
                return http.request.render('odoocms_faculty_portal.faculty_error')

            if not class_id or class_id.faculty_staff_id != faculty_staff:
                return 'Error'
            
            ass_comp_id = int(kw.get('ass_comp_id', '0'))
            ass_name = kw.get('ass_name', False)
            ass_code = kw.get('ass_code', False)
            max_marks = int(kw.get('max_marks', '0'))
            weightage = int(kw.get('weightage', '0'))
            assessment_date = kw.get('classdate', '0')
            assessment_date = assessment_date.replace(".", "/")

            assessment_date = datetime.strptime(assessment_date, '%d/%m/%Y')
            assessment_date2 = datetime.strftime(assessment_date, '%Y-%m-%d')

            assessment_component_id = request.env['odoocms.assessment.component'].sudo().search(
                [('class_id', '=', class_id.id), ('id', '=', ass_comp_id)])

            if not assessment_component_id:
                raise UserError("Assessment Type is not valid")

            assessment_rec = request.env['odoocms.assessment'].sudo().search(
                [('assessment_component_id', '=', assessment_component_id.id),
                 ('class_id', '=', class_id.id), ('code', '=', ass_code)])
            if assessment_rec:
                raise UserError("Assessment with code %s s already exist." % (ass_code,))

            assessment_vals = [{
                'name': ass_name,
                'code': ass_code,
                'assessment_component_id': assessment_component_id.id or False,
                'class_id': class_id.id,
                'max_marks': max_marks,
                'weightage':weightage,
                'date_assessment':assessment_date2
            }]
            assessment_rec = request.env['odoocms.assessment'].sudo().create(assessment_vals)

            assessments = []
            for assessment in class_id.assessment_ids:
                singleDate = "-"
                if assessment.date_assessment:
                    singleDate =  datetime.strftime(assessment.date_assessment, '%Y-%m-%d')

                ass_data = {
                    'id': assessment.id,
                    'name': assessment.name,
                    'code': assessment.code,
                    'assessment_type': assessment.assessment_component_id.assessment_type_name,
                    'max_marks': assessment.max_marks,
                    'weightage': assessment.weightage,
                    'date_assessment':singleDate,
                    'assessment_len': len(assessment.assessment_lines),
                }
                assessments.append(ass_data)

            data = {'assessments': assessments}

        except Exception as e:
            data = {'status_is': "Error",
                    'message': e.args[0],
                    'color': '#FF0000'
                    }
        data = json.dumps(data)
        return data

    @http.route('/faculty/assessmentweightage/update', type='http', auth="user", method=['POST'], website=True, csrf=False)
    def assessment_configuration_updateweightage(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
            assessment_id = int(kw.get('id', '0'))
            weightage = (kw.get('weightage', '0'))
            max_marks = (kw.get('max_marks', '0'))

            visibility = (kw.get('visibility'))
            name = (kw.get('name', '0'))
            code = (kw.get('code', '0'))
            assdate = kw.get('assessmentdate', '0')
            
            assessment_id = request.env['odoocms.assessment'].sudo().search([('id', '=', assessment_id)])

            if not assessment_id or assessment_id.class_id.faculty_staff_id != faculty_staff:
                data = {
                    'status_is': "Error",
                    'error_message': 'Assessment update failed',
                    'color': '#FF0000'
                }
                data = json.dumps(data)
                return data

            class_id = assessment_id.class_id
            assessment_id.weightage = weightage
            assessment_id.max_marks = max_marks
            assessment_id.name = name
            assessment_id.code = code
            assessment_id.date_assessment = assdate
            assessment_id.is_visible = True if visibility =='true' else False
            assessments = []
            for assessment in class_id.assessment_ids:
                ass_data = {
                    'id': assessment.id,
                    'name': assessment.name,
                    'code': assessment.code,
                    'assessment_type': assessment.assessment_component_id.assessment_type_name,
                    'max_marks': assessment.max_marks,
                    'weightage': assessment.weightage,
                    'assessment_len': len(assessment.assessment_lines),
                    'assessment_visibility': assessment.is_visible
                }
                assessments.append(ass_data)
            data = {'assessments': assessments}
            
        except Exception as e:
            data = {
                'status_is': "Error",
                'error_message': e.args[0],
                'color': '#FF0000'
            }
        data = json.dumps(data)
        return data

    @http.route('/faculty/assessment/delete', type='http', auth="user", method=['POST'], website=True, csrf=False)
    def assessment_configuration_delete(self, **kw):
        try:
            assessment_id = int(kw.get('id', '0'))
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
            assessment_id = request.env['odoocms.assessment'].sudo().search([('id', '=', assessment_id)])

            if not assessment_id or assessment_id.class_id.faculty_staff_id != faculty_staff:
                return 'Error'

            class_id = assessment_id.class_id
            assessment_id.sudo().unlink()
            assessments = []
            for assessment in class_id.assessment_ids:
                ass_data = {
                    'id': assessment.id,
                    'name': assessment.name,
                    'code': assessment.code,
                    'assessment_type': assessment.assessment_component_id.assessment_type_name,
                    'max_marks': assessment.max_marks,
                    'weightage': assessment.weightage,
                    'date': assessment.date_assessment or "-",
                    'assessment_len': len(assessment.assessment_lines),
                }
                assessments.append(ass_data)

            data = {'assessments': assessments}

        except Exception as e:
            data = {'status_is': "Error",
                    'message': e.args[0],
                    'color': '#FF0000'
                    }
        data = json.dumps(data)
        return data


    @http.route('/result/assessment/component/save', type='http', auth="user", method=['POST'], website=True, csrf=False)
    def assessment_component_save(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
            result_class = int(kw.get('result_class', '0'))
            partner = request.env.user.partner_id
            result_class = request.env['odoocms.class'].sudo().search([('id', '=', result_class)])

            if not result_class or result_class.faculty_staff_id != faculty_staff:
                return 'Error'

            for ass_comp in result_class.assessment_component_ids:
                key = 'ass_comp_weightage_input_' + str(ass_comp.id)
                weightage = kw.get(key)
                if weightage != '':
                    weightage = float(weightage)
                    if weightage and (weightage < ass_comp.min or weightage > ass_comp.max):
                        return 'error'

                    ass_comp.weightage = weightage

            return request.redirect('/faculty/result/configure/id/' + str(result_class.id))
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)

    @http.route('/result/sheet/upload', type='http', auth="user", method=['POST'], website=True, csrf=False)
    def assessment_import(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
            result_class = int(kw.get('result_class', '0'))
            assessment_sheet = kw.get('assessment_sheet', False)
            
            class_id = request.env['odoocms.class'].sudo().search([('id', '=', result_class)])

            if not class_id or class_id.faculty_staff_id != faculty_staff:
                return 'Error'
            content = assessment_sheet.read()
            if content and class_id:
                res = class_id.assessment_import_excell(content)
                if res:
                    data = {
                        'status_is': "Success",
                        'message': 'Data Successfully Imported',
                        'color': '#00FF00'
                    }
            else:
                data = {
                    'status_is': "Error",
                    'message': 'File Error',
                    'color': '#FF0000'
                }
            
        except Exception as e:
            data = {
                'status_is': "Error",
                'message': e.args[0],
                'color': '#FF0000'
            }
        data = json.dumps(data)
        return data

    @http.route('/download/result/sheet/template/<int:id>', csrf=False, type='http', auth="user", method=['GET'], website=True)
    def assessment_download(self, id=0, **kw):
        values, success, faculty_staff = main.prepare_portal_values(request)
        if not success:
            return request.render("odoocms_faculty_portal.faculty_error", values)
        
        if id != 0:
            domain = [
                ('id', '=', id),
                ('faculty_staff_id', '=', faculty_staff.id),
                # ('term_id', '=', values['config_term'])
            ]
            class_id = request.env['odoocms.class'].sudo().sudo().search(domain)
            if not class_id:
                values = {
                    'header': 'Error!',
                    'message': 'Nothing Found!',
                }
                return 'Error'

            if class_id:
                file_data = class_id.assessment_sheet_excel()
                filename = (class_id.code or 'template') + '.xls'
                return http.send_file(file_data, filename=filename, as_attachment=True, cache_timeout=5)

    @http.route('/result/class/grades/create/<int:id>', type='http', auth="user", website=True, csrf=False)
    def assessment_grades(self, id=0, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
            if id != 0:
                domain = [
                    ('id', '=', id),
                    ('faculty_staff_id', '=', faculty_staff.id),
                    # ('term_id', '=', values['config_term']),
                ]
                result_class = request.env['odoocms.class'].sudo().search(domain)
                if not result_class:
                    values = {
                        'header': 'Error!',
                        'message': 'Nothing Found!',
                    }
                    return request.render("odoocms_faculty_portal.faculty_error", values)
                    
                values.append({
                    'result_class': result_class,
                    # 'rechecking_requests':rechecking_requests,
                   
                    # These are for breadcrumbs
                    'active_menu': 'result',
                })
                return http.request.render('odoocms_faculty_portal.faculty_portal_class_grades', values)
        except Exception as e:
            values = {
                'error_message': e or False
            }
            return http.request.render('odoocms_faculty_portal.faculty_error', values)

    @http.route('/result/class/grades/config/result/update', type='http', auth="user", website=True, csrf=False)
    def assessment_grade_visibility_gpa(self, **kw):
        try:
            values, success, faculty_staff = main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_faculty_portal.faculty_error", values)
            
            assessment_id = int(kw.get('assessment_id', '0'))
            student_visibility = kw.get('student_visibility', '0')
            student_visibility = True if student_visibility == 'true' else False
            
            data = {'assessment_id': assessment_id}
            
        except Exception as e:
            data = {'status_is': "Error",
                    'error_message': e.args[0],
                    'color': '#FF0000'
                    }
        data = json.dumps(data)
        return data





