# -*- coding: utf-8 -*-
import pdb

from odoo import http
import json
import base64
from datetime import date, timedelta
import random
import string


class AdmissionApplication(http.Controller):
    @http.route('/admission/registration', type='http', auth="user", method=['GET'], website=True)
    def admission_registration(self, **get):
        company = http.request.env['res.company'].sudo().search([])
        register = http.request.env['odoocms.admission.register'].sudo().search([('state', '=', 'application')])
        steps = http.request.env['odoocms.application.steps'].sudo().search([])
        test_step_sequence = http.request.env['odoocms.application.steps'].sudo().search(
            [('invisible', '=', 'test')]).sequence - 1
        countries = http.request.env['res.country'].sudo().search([])
        provinces = http.request.env['odoocms.province'].sudo().search([])
        religion_id = http.request.env['odoocms.religion'].sudo().search([])
        admission_quota = http.request.env['odoocms.admission.quota'].sudo().search([])

        current_user = http.request.env.user
        application = http.request.env['odoocms.application'].sudo().search([('cnic', '=', current_user.login)])
        program_preferences = http.request.env['odoocms.application.preference'].sudo().search(
            [('application_id', '=', application.id)])

        # program_preferences_ordered = http.request.env['odoocms.application.preference'].sudo().search(
        #     [('application_id', '=', application.id)], order='preference asc')

        program_preferences_ordered = http.request.env['odoocms.application.preference'].sudo().search([], order='preference asc')

        matric_education = http.request.env['odoocms.application.academic'].sudo().search(
            [('application_id', '=', application.id), ('degree_level', 'in', ('Matric', 'O-Level'))])
        inter_education = http.request.env['odoocms.application.academic'].sudo().search(
            [('application_id', '=', application.id), ('degree_level', 'in', ('A-Level', 'Intermediate', 'DAE'))])
        ug_education = http.request.env['odoocms.application.academic'].sudo().search(
            [('application_id', '=', application.id), ('degree_level', '=', 'UG')])

        application_documents = http.request.env['odoocms.application.documents'].sudo().search(
            [('application_id', '=', application.id)])
        boards = http.request.env['odoocms.application.board'].sudo().search([])
        matric_sessions = http.request.env['odoocms.application.passing.year'].sudo().search([('matric', '=', True)])
        inter_sessions = http.request.env['odoocms.application.passing.year'].sudo().search([('inter', '=', True)])
        ug_sessions = http.request.env['odoocms.application.passing.year'].sudo().search([('ug', '=', True)])
        domicile_domain = [('province_id', '=', application.province_id.id)] if application.province_id else []

        domiciles = http.request.env['odoocms.domicile'].sudo().search(domicile_domain)

        discipline_ids = http.request.env['odoocms.discipline'].sudo().search([])
        degree_ids = http.request.env['odoocms.degree'].sudo().search([])

        # test_center_ids = []
        test_center_ids = http.request.env['odoocms.admission.test.center'].sudo().search([])

        # if not program_preferences_ordered:
        #     test_center_ids = http.request.env['odoocms.admission.test.center'].sudo().search([])
        # else:
        #     for dis in program_preferences_ordered.discipline_id:
        #         test_center_id = http.request.env['odoocms.admission.test.center'].sudo().search([('discipline_id', '=', dis.id)])
        #         test_center_ids.append(test_center_id)

        discipline_1 = http.request.env['odoocms.discipline'].sudo()
        discipline_2 = http.request.env['odoocms.discipline'].sudo()
        # prefs_1 = http.request.env['odoocms.application.preference'].sudo()
        prefs_2 = http.request.env['odoocms.application.preference'].sudo()

        # skip discipline check for uom
        # for program in program_preferences_ordered:
        #     if not discipline_1 and program.discipline_preference == 1:
        #         discipline_1 = program.discipline_id
        #     if not discipline_2 and program.discipline_preference == 2:
        #         discipline_2 = program.discipline_id
        #
        #     if program.discipline_id.id == discipline_1.id:
        #         prefs_1 += program
        #     else:
        #         prefs_2 += program
        # .program_id.matric_min

        prefs_1 = program_preferences_ordered
        discipline_programs = []
        if not register:
            values = {
                'header': 'Admission Closed!',
                'message': 'Admission Closed for Current Session!'
            }
            return http.request.render("odoocms_admission_portal.submission_message", values)
        else:
            print(register)
            print(register[0])
            programs = register[0].program_ids & application.degree.program_ids
            for program in programs:
                discipline_programs.append(
                    {'id': program.id, 'name': program.name, 'discipline': program.discipline_id})

        if date.today() > register[0].date_end:
            values = {
                'header': 'Admission Closed!',
                'message': 'Date over. Admission Closed for Current Session now!'
            }
            return http.request.render("odoocms_admission_portal.submission_message", values)

        if not application:
            application = http.request.env['odoocms.application'].sudo().create({
                'cnic': current_user.login,
                'email': current_user.email,
                'name': current_user.name,
                'register_id': register[0].id,
            })
        student_quotas = []
        for rec in application.quota_ids:
            student_quotas.append(rec.quota_id.id)
        print(9998888888777766666666555555544444444, application)
        Data = {
            'steps': steps,
            'test_step_sequence': test_step_sequence,
            'students': application,
            'programs': register[0].program_ids,
            'discipline_programs': discipline_programs,
            'countries': countries,
            'provinces': provinces,
            'current_user': current_user,
            'register': register,
            'program_preferences': program_preferences,
            'program_preferences_ordered': program_preferences_ordered,
            'discipline_1': discipline_1,
            'discipline_2': discipline_2,
            'prefs_1': prefs_1,
            'prefs_2': prefs_2,
            'selected_discipline': program_preferences_ordered.discipline_id,
            'matric_education': matric_education,
            'inter_education': inter_education,
            'ug_education': ug_education,
            'application_documents': application_documents,
            'boards': boards,
            'matric_sessions': matric_sessions,
            'inter_sessions': inter_sessions,
            'ug_sessions': ug_sessions,
            'religion_id': religion_id,
            'company': company,
            'domiciles': domiciles,
            'today': date.today(),
            'last_year': date.today() - timedelta(days=365),
            'readonly': False,
            'readonly2': False,
            'discipline_ids': discipline_ids,
            'degree_ids': degree_ids,
            'test_center_ids': test_center_ids,
            'admission_quota': admission_quota,
            'student_quotas': student_quotas
        }
        if (application.state == 'draft'
                and application.fee_voucher_state != 'verify'):
            Data['readonly2'] = True
            return http.request.render('odoocms_admission_portal.addmission_registration', Data)

        elif (application.state == 'draft'):
            return http.request.render('odoocms_admission_portal.addmission_registration', Data)

        elif (application.state == 'confirm'):
            Data['readonly'] = True
            Data['readonly2'] = False
            return http.request.render('odoocms_admission_portal.addmission_registration', Data)
        else:
            values = {
                'header': 'Application In Process',
                'message': 'Application Is in Process. Kindly wait for merit list!',
            }
            return http.request.render('odoocms_admission_portal.submission_message', values)

    @http.route('/admissiononline/testcenter/change', csrf=False, type="http", methods=['POST', 'GET'], auth="public",
                website=True)
    def test_center_change(self, **kw):
        try:

            current_user = http.request.env.user
            center_id = int(kw.get('id'))
            application = http.request.env['odoocms.application'].sudo().search([('cnic', '=', current_user.login)])
            test_center_id = http.request.env['odoocms.admission.test.center'].sudo().search([('id', '=', center_id)])

            template = http.request.env.ref('odoocms_admission_portal.admission_test_center').sudo()
            test_center_step = http.request.env['odoocms.application.steps'].sudo().search(
                [('template', '=', template.id)])

            if center_id:
                data = {'center_id': center_id}
                if application.step_number < test_center_step.sequence:
                    data['step_number'] = test_center_step.sequence
                application.sudo().write(data)

            center_list = []
            test_center = []
            schedule_list = []
            for center in test_center_id:
                # test_center = [{'id': center.id, 'center': center.name, 'code': center.code,
                #                     'test_type': center.test_type,
                #                     'discipline': center.discipline_id.name}]
                if center.time_ids:
                    for schedule in center.time_ids:
                        if schedule.active_time and application.degree in schedule.degree_ids:
                            schedule_list.append({'id': schedule.id, 'date': schedule.date.strftime("%m/%d/%Y"),
                                                  'time': '%02d:%02d' % (divmod(schedule.time * 60, 60))})

                # center_list.append({'center':test_center, 'data': schedule_list})
            record = {
                'status_is': "noerror",
                'center_id': test_center_id.id,
                'test_type': test_center_id.test_type,
                # 'discipline': test_center_id.discipline_id.name,
                'schedule': schedule_list,
                'schedules': len(schedule_list)
            }
            return json.dumps(record)

        except:
            record = {'status_is': "error"}
            return json.dumps(record)

    @http.route('/admissiononline/testcenter/save', csrf=False, type="http", methods=['POST', 'GET'], auth="public",
                website=True)
    def test_center_change_save(self, **kw):
        try:
            current_user = http.request.env.user
            center_id = int(kw.get('center_id'))
            time_id = int(kw.get('time_id'))
            application = http.request.env['odoocms.application'].sudo().search([('cnic', '=', current_user.login)])

            if center_id and time_id:
                template = http.request.env.ref('odoocms_admission_portal.admission_test_center').sudo()
                test_center_step = http.request.env['odoocms.application.steps'].sudo().search(
                    [('template', '=', template.id)])
                data = {
                    'center_id': center_id,
                    'slot_id': time_id,
                }
                if application.step_number < test_center_step.sequence:
                    data['step_number'] = test_center_step.sequence
                application.sudo().write(data)

            record = {
                'status_is': "noerror",
            }
            return json.dumps(record)

        except:
            record = {'status_is': "error"}
            return json.dumps(record)

    @http.route('/admission/test_center/form', type='http', auth="user", method=['GET'], website=True)
    def admission_test_center_form(self, **get):
        company = http.request.env['res.company'].sudo().search([])
        register = http.request.env['odoocms.admission.register'].sudo().search([('state', '=', 'application')])
        current_user = http.request.env.user
        application = http.request.env['odoocms.application'].sudo().search([('cnic', '=', current_user.login)])
        # test_center_ids = []
        test_center_ids = http.request.env['odoocms.admission.test.center'].sudo().search([])

        # if not program_preferences_ordered:
        #     test_center_ids = http.request.env['odoocms.admission.test.center'].sudo().search([])
        # else:
        #     for dis in program_preferences_ordered.discipline_id:
        #         test_center_id = http.request.env['odoocms.admission.test.center'].sudo().search([('discipline_id', '=', dis.id)])
        #         test_center_ids.append(test_center_id)

        if not register:
            values = {
                'header': 'Admission Closed!',
                'message': 'Admission Closed for Current Session!'
            }
            return http.request.render("odoocms_admission_portal.submission_message", values)

        if date.today() > register.date_end:
            values = {
                'header': 'Admission Closed!',
                'message': 'Date over. Admission Closed for Current Session now!'
            }
            return http.request.render("odoocms_admission_portal.submission_message", values)

        if not application:
            application = http.request.env['odoocms.application'].sudo().create({
                'cnic': current_user.login,
                'email': current_user.email,
                'name': current_user.name,
                'register_id': register[0].id,
            })

        Data = {
            'student': application,
            'programs': register[0].program_ids,
            'current_user': current_user,
            'register': register,
            'today': date.today(),
            'last_year': date.today() - timedelta(days=365),
            'readonly': False,
            'readonly2': False,
            'test_center_ids': test_center_ids,
        }
        return http.request.render('odoocms_admission_portal.test_center_form', Data)

    @http.route('/admissiononline/province/change', csrf=False, type="http", methods=['POST', 'GET'], auth="public",
                website=True)
    def province_change(self, **kw):
        try:
            current_user = http.request.env.user
            province_id = int(kw.get('province_id'))
            application = http.request.env['odoocms.application'].sudo().search([('cnic', '=', current_user.login)])
            domicile_data = []
            domiciles = http.request.env['odoocms.domicile'].sudo().search([('province_id', '=', province_id)])
            for domicile in domiciles:
                domicile_data.append({'id': domicile.id, 'name': domicile.name})
            record = {
                'status_is': "noerror",
                'domiciles': domicile_data,
            }
        except:
            record = {'status_is': "error"}

        return json.dumps(record)

    @http.route('/admissiononline/discipline/change', csrf=False, type="http", methods=['POST', 'GET'], auth="public",
                website=True)
    def discipline_change(self, **kw):
        try:
            current_user = http.request.env.user
            discipline_id = int(kw.get('id'))
            current_discipline_id = int(kw.get('current_dis'))
            application = http.request.env['odoocms.application'].sudo().search([('cnic', '=', current_user.login)])
            register = http.request.env['odoocms.admission.register'].sudo().search(
                [('state', '=', 'application'), ('id', '=', application.register_id.id)])

            http.request.env['odoocms.application.preference'].sudo().search(
                [('application_id', '=', application.id), ('discipline_preference', '>=', current_discipline_id)]
            ).unlink()
            discipline_programs = []
            programs = register[0].program_ids.filtered(
                lambda l: l.discipline_id.id == discipline_id) & application.degree.program_ids
            for program in programs:
                discipline_programs.append(
                    {'id': program.id, 'name': program.name, 'discipline': program.discipline_id.name})
            record = {
                'status_is': "noerror",
                'discipline_programs': discipline_programs,
                'current_dis': int(kw.get('current_dis')),
            }
        except:
            record = {'status_is': "error"}

        return json.dumps(record)

    @http.route('/download/admission/form', csrf=False, type="http", methods=['POST', 'GET'], auth="public",
                website=True)
    def download_admission_form(self, **kw):
        current_user = http.request.env.user
        application = http.request.env['odoocms.application'].sudo().search([('cnic', '=', current_user.login)])
        return application._show_report(model=application, report_type='pdf',
                                        report_ref='odoocms_admission_portal.admission_final_report', download=True)

    @http.route('/download/admission/slip', csrf=False, type="http", methods=['POST', 'GET'], auth="public",
                website=True)
    def download_admission_slip(self, **kw):
        current_user = http.request.env.user

        application = http.request.env['odoocms.application'].sudo().search([('cnic', '=', current_user.login)])
        application.sudo().write({
            'fee_voucher_state': 'download'
        })
        application.fee_voucher_download_date = date.today()

        return application._show_report(model=application, report_type='pdf',
                                        report_ref='odoocms_admission_portal.admission_invoices', download=True)

    # This is called from ajax to save applicant data
    @http.route(['/admission/save'], csrf=False, type="http", methods=['POST', 'GET'], auth="public", website=True)
    def save_admission_application_contents(self, application_id=False, access_token=None, report_type=None,
                                            download=False, **kw):
        print("KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW", kw)
        current_user = http.request.env.user
        try:
            application = http.request.env['odoocms.application'].sudo().search([('cnic', '=', current_user.login)])
        except:
            record = {'status_is': "error", 'msg': 'Unknown'}
            return json.dumps(record)
        try:
            is_hafiz = bool(kw.get('is_hafiz'))
            is_forces_quota = kw.get('is_forces_quota')
            forces_quota = kw.get('forces_quota')
            is_rural_quota = kw.get('is_rural_quota')
            rural_quota = kw.get('rural_quota')

            finance_ass = bool(kw.get('finance_ass', False))
            finance_ass_duration = kw.get('finance_ass_duration', False)
            finance_ass_amt = kw.get('finance_ass_amt', False)

            bdata = {
                'cnic': current_user.login,
                'is_forces_quota': bool(is_forces_quota),
                'forces_quota': forces_quota,
                'is_rural_quota': bool(is_rural_quota),
                'rural_quota': rural_quota,
                'is_hafiz': is_hafiz,
                'finance_ass': finance_ass,
                'finance_ass_duration': finance_ass_duration,
                'finance_ass_amt': finance_ass_amt,
            }
            personal_data = self.process_personal_data(kw)
            contact_data = self.process_contact_data(kw)
            guardian_data = self.process_guardian_data(kw)
            program_preference_data = self.process_program_preference(kw)
            data = dict(bdata)
            data.update(personal_data)
            data.update(contact_data)
            data.update(guardian_data)
            data.update(program_preference_data)

            test_type = kw.get('test_type')
            test_total_marks = kw.get('test_total_marks')
            test_obtained_marks = kw.get('test_obtained_marks')
            test_percentage = kw.get('test_percentage')
            test_date = kw.get('test_date')

            # if finance_ass_amount:
            #     finance_ass_amount = int(finance_ass_amount)
            data['test_type'] = test_type
            if test_type == 'SAT' and test_total_marks and len(test_total_marks) > 0 and test_percentage and len(
                    test_percentage) > 0:
                data['test_total_marks'] = int(test_total_marks)
                data['test_percentage'] = float(test_percentage)
                if test_obtained_marks and len(test_obtained_marks) > 0:
                    data['test_obtained_marks'] = int(test_obtained_marks)

            elif test_type == 'UET' and test_date and len(test_date) != 0:
                if kw.get('uet_test_obtained_marks') and len(kw.get('uet_test_obtained_marks')) > 0:
                    data['test_obtained_marks'] = int(kw.get('uet_test_obtained_marks'))
                    data['test_date'] = test_date
                    data['test_percentage'] = float(kw.get('uet_test_obtained_marks'))

            if application.state != 'draft':
                data = {}
                if test_type == 'SAT' and test_total_marks and len(
                        test_total_marks) > 0 and test_percentage and len(test_percentage) > 0:
                    data['test_total_marks'] = int(test_total_marks)
                    data['test_percentage'] = float(test_percentage)
                    if test_obtained_marks and len(test_obtained_marks) > 0:
                        data['test_obtained_marks'] = int(test_obtained_marks)
                elif test_type == 'UET' and test_date and len(test_date) != 0:
                    if kw.get('uet_test_obtained_marks') and len(kw.get('uet_test_obtained_marks')) > 0:
                        data['test_obtained_marks'] = int(kw.get('uet_test_obtained_marks'))
                        data['test_date'] = test_date
                        data['test_percentage'] = float(kw.get('uet_test_obtained_marks'))

            fee_template = http.request.env.ref('odoocms_admission_portal.admission_fee_voucher').sudo()
            fee_step = http.request.env['odoocms.application.steps'].sudo().search([('template', '=', fee_template.id)])

            steps = http.request.env['odoocms.application.steps'].sudo().search([], order='sequence desc')
            for step in steps:
                # if fee_step <= data['step_number'] and fee_step.test_field and application.fee_voucher_verified:
                if step.test_field and bool(data.get(step.test_field.name, False)) != False:
                    if application.step_number < step.sequence:
                        data['step_number'] = min(step.sequence, 10)  # + 1
                    break
            print(12222222222222222222999999999999999999999, application)
            application.sudo().write(data)
            self.process_matric_data(application, kw)
            self.process_inter_data(application, kw)
            self.process_ug_data(application, kw)
            record = {'status_is': "update", 'msg': 'Update', 'step_number': application.step_number}
        except Exception as e:
            record = {'status_is': "error", 'msg': e.args[0]}

        return json.dumps(record)

    def process_personal_data(self, kw):
        print("personal details 11111111111", kw)
        degree = kw.get('degree')
        country = kw.get('country_id')
        domicile_id = kw.get('domicile_id')
        nationality = kw.get('nationality')
        religion_id = kw.get('religion_id')

        data = {
            'first_name': kw.get('first_name'),
            'middle_name': kw.get('middle_name'),
            'last_name': kw.get('last_name'),
            'blood_group': kw.get('bloodgroup'),

            'gender': kw.get('gender'),
            'date_of_birth': kw.get('dob'),
            'cnic': kw.get('cnic'),
            'is_dual_nationality': bool(kw.get('is_dual_nationality', False)),
            'passport': kw.get('passport'),
            'no_of_sibling': kw.get('no_of_sibling'),
            'family_in_university': kw.get('family_in_university'),
            'province_id': kw.get('province_id'),
            'province2': kw.get('province2'),

            'is_any_disease': bool(kw.get('is_any_disease', False)),
            'disease': kw.get('is_any_disease'),
            'is_any_disability': bool(kw.get('is_any_disability', False)),
            'disability': kw.get('disability'),

            'get_info_from': kw.get('get_info_from'),

        }

        if degree and degree != '':
            data['degree'] = int(degree)
        if domicile_id and domicile_id != '':
            data['domicile_id'] = int(domicile_id)
        if religion_id and religion_id != '':
            data['religion_id'] = int(religion_id)
        if nationality and nationality != '':
            data['nationality'] = int(nationality)
        if country and country != '':
            data['country_id'] = int(country)

        if country and country != '':
            data['country_id'] = int(country)
        return data

    def process_program_preference(self, kw):
        pref_c1 = kw.get('pref_c1')
        pref_c2 = kw.get('pref_c2')
        pref_c3 = kw.get('pref_c3')
        data = {
            'choice_one': kw.get('pref_c1'),
            'choice_two': kw.get('pref_c2'),
            'choice_three': kw.get('pref_c3'),
        }
        if pref_c1 and pref_c1 != '':
            data['choice_one'] = int(pref_c1)
        if pref_c2 and pref_c2 != '':
            data['choice_two'] = int(pref_c2)
        if pref_c3 and pref_c3 != '':
            data['choice_three'] = int(pref_c3)
        return data

    def process_contact_data(self, kw):
        print("process_contact_data 222222222222222222222", kw)

        per_country = kw.get('per_country', False)
        present_country_id = kw.get('present_country_id', False)

        data = {
            'email': kw.get('email'),
            'mobile': kw.get('mobile'),
            'per_street': kw.get('per_street', False),
            'per_street2': kw.get('per_street2', False),
            'per_city': kw.get('per_city', False),
            'per_province': kw.get('per_province', False),
            'per_province2': kw.get('per_province2', False),

            'street': kw.get('street', False),
            'street2': kw.get('street2', False),
            'city': kw.get('city', False),
            'present_province': kw.get('present_province', False),
            'present_province2': kw.get('present_province2', False),

            'is_same_address': bool(kw.get('is_same_address')),
        }
        if per_country and per_country != '':
            data['per_country_id'] = int(per_country)

        if present_country_id and present_country_id != '':
            data['present_country_id'] = int(present_country_id)

        return data

    def process_guardian_data(self, kw):
        father_education = kw.get('father_education')
        mother_education = kw.get('mother_education')

        data = {
            'father_name': kw.get('father_name'),
            'mother_name': kw.get('mother_name'),
            'father_status': kw.get('father_status'),
            'mother_status': kw.get('mother_status'),
            'single_parent': bool(kw.get('single_parent', False)),

            'guardian_name': kw.get('guardian_name'),
            'guardian_cnic': kw.get('guardian_cnic'),
            'guardian_occupation': kw.get('guardian_occupation'),
            'father_income': kw.get('father_income'),
            'guardian_relation': kw.get('guardian_relation'),
            'guardian_mobile': kw.get('guardian_mobile'),
            'guardian_landline': kw.get('guardian_landline'),
            'guardian_address': kw.get('guardian_address'),

        }
        print(1111111111, data)
        if father_education and father_education != '':
            data['father_education'] = father_education
        if mother_education and mother_education != '':
            data['mother_education'] = mother_education
        return data

    def process_matric_data(self, application, kw):
        matric_degree = kw.get('matric_degree')
        matric_pass_year = kw.get('matric_pass_year')
        matric_board = kw.get('matric_board')

        grade_aa = kw.get('grade_aa')
        grade_a = kw.get('grade_a')
        grade_b = kw.get('grade_b')
        grade_c = kw.get('grade_c')
        grade_d = kw.get('grade_d')
        grade_e = kw.get('grade_e')
        grade_f = kw.get('grade_f')
        grade_g = kw.get('grade_g')
        o_level_total = kw.get('o-level-totalmarks')
        o_level_obtained = kw.get('o-level-obtainedmarks')
        o_level_percentage = kw.get('o-level-percentage')

        matric_data = {
            'degree_level': matric_degree,
            'subjects': kw.get('matric_subject'),
            'roll_number': kw.get('matricrollnumber'),
            'total_marks': kw.get('matrictotalmarks'),
            'obtained_marks': kw.get('matricobtainedmarks'),
            'percentage': kw.get('matricpercentage'),
        }
        if matric_pass_year and len(matric_pass_year) > 0:
            matric_data['year'] = matric_pass_year
        if matric_board and len(matric_board) > 0:
            matric_data['board'] = matric_board

        if matric_degree and matric_degree == 'O-Level':
            matric_data['board'] = False
            matric_data['roll_number'] = kw.get('olevelrollnumber')

            if grade_aa and len(grade_aa) > 0 and o_level_total and o_level_obtained and o_level_percentage and len(
                    o_level_total) > 0 and len(o_level_obtained) > 0 and \
                    len(o_level_percentage) > 0:
                matric_data['grade_aa'] = int(grade_aa)
                matric_data['o_level_total'] = int(o_level_total)
                if o_level_obtained:
                    matric_data['o_level_obtained'] = float(o_level_obtained)
                if o_level_percentage:
                    matric_data['o_level_percentage'] = float(o_level_percentage)
            if grade_a and grade_b and grade_c and grade_d and grade_d and grade_e and grade_f and grade_g and \
                    len(grade_g) > 0 and len(grade_f) > 0 and len(grade_e) > 0 and len(grade_d) > 0 and len(
                grade_c) > 0 and len(grade_b) > 0 and len(grade_a) > 0:
                matric_data['grade_a'] = int(grade_a)
                matric_data['grade_b'] = int(grade_b)
                matric_data['grade_c'] = int(grade_c)
                matric_data['grade_d'] = int(grade_d)
                matric_data['grade_e'] = int(grade_e)
                matric_data['grade_f'] = int(grade_f)
                matric_data['grade_g'] = int(grade_g)

        if (matric_degree and len(matric_degree) > 0) and application.state == 'draft':
            application_academic_line = http.request.env['odoocms.application.academic'].sudo().search(
                [('degree_level', 'in', ('Matric', 'O-Level')), ('application_id', '=', application.id)])
            if application_academic_line:
                application_academic_line.sudo().unlink()

            application_academic_line = http.request.env['odoocms.application.academic']
            matric_data['application_id'] = application.id
            application_academic_line.sudo().create(matric_data)

    def process_inter_data(self, application, kw):
        inter_degree = kw.get('inter_degree')
        inter_pass_year = kw.get('inter_pass_year')
        inter_board = kw.get('inter_board')
        inter_subject = kw.get('inter_subject')

        # math_marks = kw.get('math_marks')
        # math_total_marks = kw.get('math_total_marks')
        # math_marks_per = kw.get('math_marks_per')
        #
        # physics_marks = kw.get('physics_marks')
        # physics_total_marks = kw.get('physics_total_marks')
        # physics_marks_per = kw.get('physics_marks_per')
        #
        # chemistry_marks = kw.get('chemistry_marks')
        # chemistry_total_marks = kw.get('chemistry_total_marks')
        # chemistry_marks_per = kw.get('chemistry_marks_per')

        inter_or_dae = kw.get('inter_or_dae')
        if inter_or_dae == 'DAE':
            inter_degree = 'DAE'
        #     math_marks = kw.get('dae_math_marks')
        #     math_total_marks = kw.get('dae_math_total_marks')
        #     math_marks_per = kw.get('dae_math_marks_per')
        #
        #     physics_marks = kw.get('dae_physics_marks')
        #     physics_total_marks = kw.get('dae_physics_total_marks')
        #     physics_marks_per = kw.get('dae_physics_marks_per')
        #
        #     chemistry_marks = kw.get('dae_chemistry_marks')
        #     chemistry_total_marks = kw.get('dae_chemistry_total_marks')
        #     chemistry_marks_per = kw.get('dae_chemistry_marks_per')
        #
        # computer_marks = kw.get('computer_marks')
        # computer_total_marks = kw.get('computer_total_marks')
        # computer_marks_per = kw.get('computer_marks_per')

        intertotalmarks = kw.get('intertotalmarks')
        interobtainedmarks = kw.get('interbtainedmarks')
        interpercentage = kw.get('interpercentage')

        a_level_grade_aa = kw.get('a_level_grade_aa')
        a_level_grade_a = kw.get('a_level_grade_a')
        a_level_grade_b = kw.get('a_level_grade_b')
        a_level_grade_c = kw.get('a_level_grade_c')
        a_level_grade_d = kw.get('a_level_grade_d')
        a_level_grade_e = kw.get('a_level_grade_e')
        a_level_grade_f = kw.get('a_level_grade_f')
        a_level_grade_g = kw.get('a_level_grade_g')
        a_level_total = kw.get('a_level_total')
        a_level_obtained = kw.get('a_level_obtained')
        a_level_percentage = kw.get('a_level_percentage')

        a_level_math = kw.get('a_level_math')
        a_level_che = kw.get('a_level_che')
        a_level_com = kw.get('a_level_com')
        a_level_physics = kw.get('a_level_physics')
        a_level_math_percentage = kw.get('a_level_math_percentage')
        a_level_che_percentage = kw.get('a_level_che_percentage')
        a_level_com_percentage = kw.get('a_level_com_percentage')
        a_level_physics_percentage = kw.get('a_level_physics_percentage')

        fy_totalmarks = kw.get('fy_totalmarks')
        fy_obtainedmarks = kw.get('fy_obtainedmarks')
        sd_y_totalmarks = kw.get('sd_y_totalmarks')
        sd_y_obtainedmarks = kw.get('sd_y_obtainedmarks')
        td_y_totalmarks = kw.get('td_y_totalmarks')
        td_y_obtainedmarks = kw.get('td_y_obtainedmarks')
        fy_percentage = kw.get('fy_percentage')
        sd_y_percentage = kw.get('sd_y_percentage')
        td_y_percentage = kw.get('td_y_percentage')

        add_math_total_marks = kw.get('add_math_total_marks')
        add_math_marks = kw.get('add_math_marks')
        add_math_marks_per = kw.get('add_math_marks_per')

        inter_data = {
            'degree_level': inter_degree,
            'roll_number': kw.get('interrollnumber')
        }
        if inter_pass_year and len(inter_pass_year) > 0:
            inter_data['year'] = inter_pass_year

        # if matric_pass_year and inter_pass_year and matric_pass_year >= inter_pass_year:
        #     record = {'status_is': "error",'msg':'Please check Matric and Intermediate Passing Years'}
        #     return json.dumps(record)

        if inter_board and len(inter_board) > 0:
            inter_data['board'] = inter_board
        if intertotalmarks and len(intertotalmarks) > 0:
            inter_data['total_marks'] = int(intertotalmarks)
        if interobtainedmarks and len(interobtainedmarks) > 0:
            inter_data['obtained_marks'] = int(interobtainedmarks)
        if interpercentage and len(interpercentage) > 0:
            inter_data['percentage'] = float(interpercentage)

        # if physics_marks and len(physics_marks) > 0:
        #     inter_data['physics_marks'] = int(physics_marks)
        # if physics_total_marks and len(physics_total_marks) > 0:
        #     inter_data['physics_total_marks'] = int(physics_total_marks)
        # if physics_marks_per and len(physics_marks_per) > 0:
        #     inter_data['physics_marks_per'] = float(physics_marks_per)
        #
        # if math_total_marks and len(math_total_marks) > 0:
        #     inter_data['math_total_marks'] = int(math_total_marks)
        # if math_marks and len(math_marks) > 0:
        #     inter_data['math_marks'] = int(math_marks)
        # if math_marks_per and len(math_marks_per) > 0:
        #     inter_data['math_marks_per'] = float(math_marks_per)

        if add_math_total_marks and len(add_math_total_marks) > 0:
            inter_data['add_math_total_marks'] = int(add_math_total_marks)
        if add_math_marks and len(add_math_marks) > 0:
            inter_data['add_math_marks'] = int(add_math_marks)
        if add_math_marks_per and len(add_math_marks_per) > 0:
            inter_data['add_math_marks_per'] = float(add_math_marks_per)

        # if chemistry_marks and len(chemistry_marks) > 0:
        #     inter_data['chemistry_marks'] = float(chemistry_marks)
        # if chemistry_total_marks and len(chemistry_total_marks) > 0:
        #     inter_data['chemistry_total_marks'] = int(chemistry_total_marks)
        # if chemistry_marks_per and len(chemistry_marks_per) > 0:
        #     inter_data['chemistry_marks_per'] = float(chemistry_marks_per)
        #
        # if computer_marks and len(computer_marks) > 0:
        #     inter_data['computer_marks'] = int(computer_marks)
        # if computer_total_marks and len(computer_total_marks) > 0:
        #     inter_data['computer_total_marks'] = int(computer_total_marks)
        # if computer_marks_per and len(computer_marks_per) > 0:
        #     inter_data['computer_marks_per'] = float(computer_marks_per)

        if inter_subject and len(inter_subject) > 0:
            inter_data['subjects'] = inter_subject
            if inter_subject == 'Pre-Medical':
                if kw.get('is_additional_maths'):
                    inter_data['is_additional_maths'] = kw.get('is_additional_maths')
                else:
                    inter_data['is_additional_maths'] = False

        if inter_degree and inter_degree == 'A-Level':
            inter_data['board'] = False
            inter_data['roll_number'] = kw.get('alevelrollnumber')

            inter_data['a_level_math'] = a_level_math
            inter_data['a_level_physics'] = a_level_physics

            if a_level_che:
                inter_data['a_level_che'] = a_level_che
            if a_level_com:
                inter_data['a_level_com'] = a_level_com

            if a_level_grade_aa and len(a_level_grade_aa) > 0 and a_level_grade_a and len(
                    a_level_grade_a) > 0 and a_level_grade_b and len(a_level_grade_b) > 0 \
                    and a_level_grade_c and len(a_level_grade_c) > 0 and a_level_grade_d and len(
                a_level_grade_d) > 0 and a_level_grade_e and len(a_level_grade_e) > 0 and \
                    a_level_grade_f and len(a_level_grade_f) > 0 and a_level_grade_g and len(a_level_grade_g) > 0:
                inter_data['a_level_grade_aa'] = int(a_level_grade_aa)
                inter_data['a_level_grade_a'] = int(a_level_grade_a)
                inter_data['a_level_grade_b'] = int(a_level_grade_b)
                inter_data['a_level_grade_c'] = int(a_level_grade_c)
                inter_data['a_level_grade_d'] = int(a_level_grade_d)
                inter_data['a_level_grade_e'] = int(a_level_grade_e)
                inter_data['a_level_grade_f'] = int(a_level_grade_f)
                inter_data['a_level_grade_g'] = int(a_level_grade_g)
            if a_level_total and len(a_level_total) > 0:
                inter_data['a_level_total'] = int(a_level_total)
            if a_level_obtained and len(a_level_obtained) > 0 and a_level_obtained != 0:
                inter_data['a_level_obtained'] = float(a_level_obtained)
            if a_level_percentage and len(a_level_percentage) > 0 and a_level_percentage != 0:
                inter_data['a_level_percentage'] = float(a_level_percentage)

        if a_level_math_percentage and len(a_level_math_percentage) > 0:
            inter_data['a_level_math_percentage'] = float(a_level_math_percentage)
        if a_level_che_percentage and len(a_level_che_percentage) > 0:
            inter_data['a_level_che_percentage'] = float(a_level_che_percentage)
        if a_level_com_percentage and len(a_level_com_percentage) > 0:
            inter_data['a_level_com_percentage'] = float(a_level_com_percentage)
        if a_level_physics_percentage and len(a_level_physics_percentage) > 0:
            inter_data['a_level_physics_percentage'] = float(a_level_physics_percentage)

        if inter_degree and inter_degree == 'DAE':

            if kw.get('dae_totalmarks') and len(kw.get('dae_totalmarks')) > 0:
                inter_data['dae_totalmarks'] = int(kw.get('dae_totalmarks'))
            if kw.get('dae_obtainedmarks') and len(kw.get('dae_obtainedmarks')) > 0:
                inter_data['dae_obtainedmarks'] = int(kw.get('dae_obtainedmarks'))
            if kw.get('dae_percentage') and len(kw.get('dae_percentage')) > 0:
                inter_data['dae_percentage'] = float(kw.get('dae_percentage'))
            if kw.get('dae_specialization') and len(kw.get('dae_specialization')) > 0:
                inter_data['dae_specialization'] = kw.get('dae_specialization')

        if inter_degree and inter_degree == 'Intermediate':
            inter_data['inter_result_status'] = kw.get('inter_result_status')

        if inter_degree and inter_degree == 'DAE':
            inter_data['dae_result_status'] = kw.get('dae_result_status')

        if fy_totalmarks and len(fy_totalmarks) > 0:
            inter_data['dae_first_year_total'] = int(fy_totalmarks)
            inter_data['dae_first_year_roll_number'] = kw.get('dae1yrollnumber')
        if fy_obtainedmarks and len(fy_obtainedmarks) > 0:
            inter_data['dae_first_year_obtained'] = int(fy_obtainedmarks)
        if fy_percentage and len(fy_percentage) > 0:
            inter_data['dae_first_year_percentage'] = float(fy_percentage)

        if sd_y_totalmarks and len(sd_y_totalmarks) > 0:
            inter_data['dae_sec_year_total'] = int(sd_y_totalmarks)
            inter_data['dae_sec_year_roll_number'] = kw.get('dae2yrollnumber')
        if sd_y_obtainedmarks and len(sd_y_obtainedmarks) > 0:
            inter_data['dae_sec_year_obtained'] = int(sd_y_obtainedmarks)
        if sd_y_percentage and len(sd_y_percentage) > 0:
            inter_data['dae_sec_year_percentage'] = float(sd_y_percentage)

        if td_y_totalmarks and len(td_y_totalmarks) > 0:
            inter_data['dae_third_year_total'] = int(td_y_totalmarks)
            inter_data['dae_third_year_roll_number'] = kw.get('dae3yrollnumber')
        if td_y_obtainedmarks and len(td_y_obtainedmarks) > 0:
            inter_data['dae_third_year_obtained'] = int(td_y_obtainedmarks)
        if td_y_percentage and len(td_y_percentage) > 0:
            inter_data['dae_third_year_percentage'] = float(td_y_percentage)

        if (inter_degree and len(inter_degree) > 0) and application.state == 'draft':
            application_academic_line = http.request.env['odoocms.application.academic'].sudo().search(
                [('degree_level', 'in', ('A-Level', 'Intermediate', 'DAE')),
                 ('application_id', '=', application.id)])
            if application_academic_line:
                application_academic_line.sudo().unlink()

            application_academic_line = http.request.env['odoocms.application.academic']
            inter_data['application_id'] = application.id
            application_academic_line.sudo().create(inter_data)

    def process_ug_data(self, application, kw):
        ug_degree = kw.get('ug_degree')
        ug_pass_year = kw.get('ug_pass_year')

        ug_data = {
            'degree_level': ug_degree,
            'degree': kw.get('degree_name'),
            'ug_university_name': kw.get('university_name'),
            'total_marks': kw.get('ug_total_cgpa'),
            'obtained_marks': kw.get('ug_obtained_cgpa'),
            'percentage': kw.get('ug_cgpa_percentage'),
        }
        if ug_pass_year and len(ug_pass_year) > 0:
            ug_data['year'] = ug_pass_year

        if (ug_degree and len(ug_degree) > 0) and application.state == 'draft':
            application_academic_line = http.request.env['odoocms.application.academic'].sudo().search(
                [('degree_level', '=', 'UG'), ('application_id', '=', application.id)])
            if application_academic_line:
                application_academic_line.sudo().unlink()

            application_academic_line = http.request.env['odoocms.application.academic']
            ug_data['application_id'] = application.id
            application_academic_line.sudo().create(ug_data)

    @http.route('/admission/discipline/preference/save', csrf=False, type="http", methods=['POST', 'GET'],
                auth="public", website=True)
    def save_preference_discipline(self, **kw):
        current_user = http.request.env.user
        application = http.request.env['odoocms.application'].sudo().search([('cnic', '=', current_user.login)])
        preference = int(kw.get('preference'))
        discipline_preference = int(kw.get('discipline_preference'))

        choice_list = []
        try:
            http.request.env['odoocms.application.preference'].sudo().search(
                [('application_id', '=', application.id), ('discipline_preference', '=', discipline_preference),
                 ('preference', '>=', preference)]).unlink()
            http.request.env['odoocms.application.preference'].sudo().create({
                'application_id': application.id,
                'program_id': int(kw.get('program_id')),
                'discipline_preference': discipline_preference,
                'preference': preference
            })
            template = http.request.env.ref('odoocms_admission_portal.admission_programs').sudo()
            admission_programs_step = http.request.env['odoocms.application.steps'].sudo().search(
                [('template', '=', template.id)])
            if application.step_number < admission_programs_step.sequence:
                application.step_number = admission_programs_step.sequence
            preference_ids = http.request.env['odoocms.application.preference'].sudo().search([
                ('application_id', '=', application.id)])
            if preference_ids:
                program_ids = application.register_id.program_ids
                choice_list.append((program_ids - preference_ids.mapped('program_id')).mapped('id'))
                choice_list.append((program_ids - preference_ids.mapped('program_id')).mapped('name'))
        except:
            choice_list = choice_list
        return json.dumps(choice_list)

    # This is to save documents
    @http.route('/save/voucher', csrf=False, type="http", methods=['POST', 'GET'], auth="public", website=True)
    def save_voucher(self, **kw):
        current_user = http.request.env.user
        application = http.request.env['odoocms.application'].sudo().search([('cnic', '=', current_user.login)])
        file = kw.get('voucher_image')
        if file and application.fee_voucher_state in ('download', 'upload', 'unverify'):
            voucher_image_uploaded = application.sudo().write({'voucher_image': base64.encodestring(file.read())})
            if voucher_image_uploaded and application:
                application.sudo().write({
                    'fee_voucher_state': 'upload0'
                })
                application.fee_voucher_upload_date = date.today()

        record = {'fee_voucher_state': application.fee_voucher_state}
        return json.dumps(record)

    @http.route('/save/voucher/details', csrf=False, type="http", methods=['POST', 'GET'], auth="public", website=True)
    def save_voucher_details(self, **kw):
        current_user = http.request.env.user
        application = http.request.env['odoocms.application'].sudo().search([('cnic', '=', current_user.login)])
        voucher_number = kw.get('voucher_number')
        voucher_date = kw.get('voucher_date')

        if voucher_number and len(voucher_number) > 0:
            if application.fee_voucher_state in ('no', 'download'):
                record = {'msg': 'not_uploaded'}
            else:
                values = {
                    'fee_voucher_state': 'upload',
                    'voucher_number': voucher_number,
                    'voucher_date': voucher_date,
                }
                application.sudo().write(values)
                template = http.request.env.ref(
                    'odoocms_admission_portal.email_template_admission_voucher_upload').sudo()
                post_message = application.message_post_with_template(template.id, composition_mode='comment')
                record = {'msg': 'success'}
        else:
            record = {'msg': 'no_info'}

        return json.dumps(record)

    @http.route('/admission/online/confirm', csrf=False, type='http', auth="user", method=['GET'], website=True)
    def application_change_state(self, **get):
        current_user = http.request.env.user
        application = http.request.env['odoocms.application'].sudo().search([('cnic', '=', current_user.login)])
        if (application):
            # template = http.request.env.ref('odoocms_admission_portal.admission_final_confirmation').sudo()
            # final_confirmation_step = http.request.env['odoocms.application.steps'].sudo().search([('template', '=', template.id)])
            # if application.step_number < final_confirmation_step.sequence:
            #     application.step_number = final_confirmation_step.sequence

            application.sudo().write({'state': 'confirm'})
            template = http.request.env.ref('odoocms_admission_portal.mail_template_application_submit').sudo()
            post_message = application.message_post_with_template(template.id, composition_mode='comment')
            Data = {"state": "confirm"}
            # applicant.step_number = 9
        else:
            Data = {"state": "draft"}
        return json.dumps(Data)

    # This is to save documents
    @http.route('/save/application/documents', csrf=False, type="http", methods=['POST', 'GET'], auth="public",
                website=True)
    def save_application_documents(self, **kw):
        current_user = http.request.env.user
        application = http.request.env['odoocms.application'].sudo().search([('cnic', '=', current_user.login)])

        matric_scaned_copy = kw.get('matric_scaned_copy', False)
        inter_scaned_copy = kw.get('inter_scaned_copy', False)
        domicile_scaned_copy = kw.get('domicile_scaned_copy', False)
        salary_slip_scaned_copy = kw.get('salary_slip_scaned_copy', False)
        test_certificate = kw.get('test_certificate', False)
        cnic_scanned_copy = kw.get('cnic_scanned_copy', False)
        cnic_back_scanned_copy = kw.get('cnic_back_scanned_copy', False)
        dae_first_year = kw.get('dae_first_year', False)
        dae_second_year = kw.get('dae_second_year', False)
        dae_third_year = kw.get('dae_third_year', False)
        hope_certificate_scanned_copy = kw.get('hope_certificate_scanned_copy', False)

        try:
            attachment_value = {
                'application_id': application.id,
            }
            if matric_scaned_copy != False:
                attachment_value['matric_scaned_copy'] = base64.encodestring(matric_scaned_copy.read())
                attachment_value['matric_scaned_copy_name'] = matric_scaned_copy.filename

            if inter_scaned_copy != False:
                attachment_value['inter_scaned_copy'] = base64.encodestring(inter_scaned_copy.read())
                attachment_value['inter_scaned_copy_name'] = inter_scaned_copy.filename
            # 'inter_scaned_copy_size': os.stat(inter_scaned_copy).st_size,

            if domicile_scaned_copy != False:
                attachment_value['domicile_scaned_copy'] = base64.encodestring(domicile_scaned_copy.read())
                attachment_value['domicile_scaned_copy_name'] = domicile_scaned_copy.filename

            if salary_slip_scaned_copy != False:
                attachment_value['salary_slip_scaned_copy'] = base64.encodestring(salary_slip_scaned_copy.read())
                attachment_value['salary_slip_scaned_copy_name'] = salary_slip_scaned_copy.filename

            if hope_certificate_scanned_copy != False:
                attachment_value['hope_certificate_scanned_copy'] = base64.encodestring(
                    hope_certificate_scanned_copy.read())
                attachment_value['hope_certificate_scanned_copy_name'] = hope_certificate_scanned_copy.filename

            if test_certificate != False:
                attachment_value['test_certificate'] = base64.encodestring(test_certificate.read())
                attachment_value['test_certificate_name'] = test_certificate.filename
            # 'domicile_scaned_copy_size': os.stat(domicile_scaned_copy).st_size,

            if cnic_scanned_copy != False:
                attachment_value['cnic_scanned_copy'] = base64.encodestring(cnic_scanned_copy.read())
                attachment_value['cnic_scanned_copy_name'] = cnic_scanned_copy.filename

            if cnic_back_scanned_copy != False:
                attachment_value['cnic_back_scanned_copy'] = base64.encodestring(cnic_back_scanned_copy.read())
                attachment_value['cnic_back_scanned_copy_name'] = cnic_back_scanned_copy.filename

            if dae_first_year != False:
                attachment_value['dae_first_year'] = base64.encodestring(dae_first_year.read())
                attachment_value['dae_first_year_name'] = dae_first_year.filename

            if dae_second_year != False:
                attachment_value['dae_second_year'] = base64.encodestring(dae_second_year.read())
                attachment_value['dae_second_year_name'] = dae_second_year.filename

            if dae_third_year != False:
                attachment_value['dae_third_year'] = base64.encodestring(dae_third_year.read())
                attachment_value['dae_third_year_name'] = dae_third_year.filename

            application_documents = http.request.env['odoocms.application.documents'].sudo().search(
                [('application_id', '=', application.id)])
            if (application_documents):
                application_documents.sudo().write(attachment_value)
                record = {'status_is': "update"}
            else:
                application_documents.sudo().create(attachment_value)
                record = {'status_is': "create"}

            template = http.request.env.ref('odoocms_admission_portal.admission_documents_upload').sudo()
            documents_upload_step = http.request.env['odoocms.application.steps'].sudo().search(
                [('template', '=', template.id)])
            if application.step_number < documents_upload_step.sequence:
                data = {'step_number': documents_upload_step.sequence}
                application.sudo().write(data)

        except:
            record = {'status_is': "error"}
        return json.dumps(record)

    # This is to save profile image
    @http.route('/admissiononline/profileimage/save', csrf=False, type="http", methods=['POST', 'GET'], auth="public",
                website=True)
    def save_profile_image(self, **kw):
        current_user = http.request.env.user
        file = kw.get('profile_image')
        application = http.request.env['odoocms.application'].sudo().search([('cnic', '=', current_user.login)])
        try:
            attachment_value = {
                'image': base64.encodestring(file.read())
            }
            application.sudo().update(attachment_value)

            template = http.request.env.ref('odoocms_admission_portal.admission_photo_upload').sudo()
            photo_upload_step = http.request.env['odoocms.application.steps'].sudo().search(
                [('template', '=', template.id)])
            if application.step_number < photo_upload_step.sequence:
                data = {'step_number': photo_upload_step.sequence}
                application.sudo().write(data)

            record = {'status_is': "noerror", 'step_number': application.step_number}
        except:
            record = {'status_is': "error", 'step_number': application.step_number}
        return json.dumps(record)

    @http.route('/confirm/test/center', csrf=False, type="http", methods=['POST', 'GET'], auth="public",
                website=True)
    def lock_test_center(self, **kw):
        current_user = http.request.env.user
        application = http.request.env['odoocms.application'].sudo().search([('cnic', '=', current_user.login)])
        try:
            data = {
                'confirm_test_center': True,
            }
            application.write(data)
        except:
            record = {'status_is': "error", 'step_number': application.step_number}
        return json.dumps(data)

    # This is to save program apply for because after selection of program register you need to reload the programs
    @http.route('/get/step', csrf=False, type="http", methods=['POST', 'GET'], auth="public", website=True)
    def get_step_number(self, **kw):
        current_user = http.request.env.user
        try:
            application = http.request.env['odoocms.application'].sudo().search([('cnic', '=', current_user.login)])
            register = http.request.env['odoocms.admission.register'].sudo().search(
                [('state', '=', 'application'), ('id', '=', application.register_id.id)])

            program_preferences_ordered = http.request.env['odoocms.application.preference'].sudo().search(
                [('application_id', '=', application.id)], order='preference asc')
            fee_template = http.request.env.ref('odoocms_admission_portal.admission_fee_voucher').sudo()
            fee_step_sequence = http.request.env['odoocms.application.steps'].sudo().search(
                [('template', '=', fee_template.id)]).sequence - 1

            fee_verified = False
            if application.fee_voucher_state == 'verify':
                fee_verified = True
            # company = http.request.env['res.company'].sudo().search([])
            # if (application.state == 'draft' and company.short_name == 'NUTECH' and not application.fee_voucher_verified):
            matric_min = 0
            inter_min = 0
            a_level_min = 0
            physics_per_min = 0
            math_per_min = 0
            computer_per_min = 0
            chemistry_per_min = 0
            for rec in program_preferences_ordered:
                if rec.program_id.matric_min >= matric_min:
                    matric_min = rec.program_id.matric_min
                if rec.program_id.inter_min >= inter_min:
                    inter_min = rec.program_id.matric_min
                if rec.program_id.a_level_min >= a_level_min:
                    a_level_min = rec.program_id.a_level_min
                if rec.program_id.physics_per_min >= physics_per_min:
                    physics_per_min = rec.program_id.physics_per_min
                if rec.program_id.math_per_min >= math_per_min:
                    math_per_min = rec.program_id.math_per_min
                if rec.program_id.computer_per_min >= computer_per_min:
                    computer_per_min = rec.program_id.computer_per_min
                if rec.program_id.chemistry_per_min >= chemistry_per_min:
                    chemistry_per_min = rec.program_id.chemistry_per_min

            record = {
                'step_number': application.step_number,
                'fee_step_sequence': fee_step_sequence,
                'fee_verified': fee_verified,
                'app_status': application.state,
                'matric_min': matric_min,
                'inter_min': inter_min,
                'a_level_min': a_level_min,
                'physics_per_min': physics_per_min,
                'math_per_min': math_per_min,
                'computer_per_min': computer_per_min,
                'chemistry_per_min': chemistry_per_min,
            }
        except:
            record = {'step_number': application.step_number}
        return json.dumps(record)

    @http.route('/download/admit/card', csrf=False, type="http", methods=['POST', 'GET'], auth="public",
                website=True)
    def download_admit_card(self, **kw):
        current_user = http.request.env.user
        length = 6
        all = string.ascii_letters + string.digits + '$#)(+-<=_@%*&!~?>'
        # string.punctuation
        password = "".join(random.sample(all, length))

        application = http.request.env['odoocms.application'].sudo().search([('cnic', '=', current_user.login)])
        if not application.cbt_password:
            application.sudo().write({
                'cbt_password': password
            })
        # application.fee_voucher_download_date = date.today()
        return application._show_report(model=application, report_type='pdf',
                                        report_ref='odoocms_admission_portal.action_applicant_admit_card',
                                        download=True)
