from odoo import http, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.http import request
from werkzeug.exceptions import NotFound
import base64


class WebsiteHrRecruitment(http.Controller):
    def sitemap_jobs(env, rule, qs):
        if not qs or qs.lower() in '/jobs':
            yield {'loc': '/jobs'}
    @http.route([
        '/jobs',
        '/jobs/country/<model("res.country"):country>',
        '/jobs/department/<model("hr.department"):department>',
        '/jobs/country/<model("res.country"):country>/department/<model("hr.department"):department>',
        '/jobs/office/<int:office_id>',
        '/jobs/country/<model("res.country"):country>/office/<int:office_id>',
        '/jobs/department/<model("hr.department"):department>/office/<int:office_id>',
        '/jobs/country/<model("res.country"):country>/department/<model("hr.department"):department>/office/<int:office_id>',
    ], type='http', auth="public", website=True, sitemap=sitemap_jobs)
    def jobs(self, country=None, department=None, office_id=None, **kwargs):
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))

        Country = env['res.country']
        Jobs = env['hr.job']

        # List jobs available to current UID
        domain = request.website.website_domain()
        job_ids = Jobs.search(domain, order="is_published desc, no_of_recruitment desc").ids
        # Browse jobs as superuser, because address is restricted
        jobs = Jobs.sudo().browse(job_ids)

        # Default search by user country
        if not (country or department or office_id or kwargs.get('all_countries')):
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                countries_ = Country.search([('code', '=', country_code)])
                country = countries_[0] if countries_ else None
                if not any(j for j in jobs if j.address_id and j.address_id.country_id == country):
                    country = False

        # Filter job / office for country
        if country and not kwargs.get('all_countries'):
            jobs = [j for j in jobs if j.address_id is None or j.address_id.country_id and j.address_id.country_id.id == country.id]
            offices = set(j.address_id for j in jobs if j.address_id is None or j.address_id.country_id and j.address_id.country_id.id == country.id)
        else:
            offices = set(j.address_id for j in jobs if j.address_id)

        # Deduce departments and countries offices of those jobs
        departments = set(j.department_id for j in jobs if j.department_id)
        countries = set(o.country_id for o in offices if o.country_id)

        if department:
            jobs = [j for j in jobs if j.department_id and j.department_id.id == department.id]
        if office_id and office_id in [x.id for x in offices]:
            jobs = [j for j in jobs if j.address_id and j.address_id.id == office_id]
        else:
            office_id = False

        # Render page
        return request.render("website_hr_recruitment.index", {
            'jobs': jobs,
            'countries': countries,
            'departments': departments,
            'offices': offices,
            'country_id': country,
            'department_id': department,
            'office_id': office_id,
        })



    # @http.route('/jobs/add', type='http', auth="user", website=True)
    # def jobs_add(self, **kwargs):
    #     # avoid branding of website_description by setting rendering_bundle in context
    #     job = request.env['hr.job'].with_context(rendering_bundle=True).create({
    #         'name': _('Job Title'),
    #     })
    #     return request.redirect("/jobs/detail/%s?enable_editor=1" % slug(job))
    #     return request.render("recruitement_employee_form.my_custom_from")




class WebsiteHrRecruitmentMine(http.Controller):

    @http.route('''/jobs/apply/<model("hr.job", "[('website_id', 'in', (False, current_website_id))]"):job>''',
                type='http', auth="public", website=True)
    # def jobs_apply(self, job, **kwargs):
    #     print(66666666666666666666666666666666, job)
    #     if not job.can_access_from_current_website():
    #         raise NotFound()
    #     job_id = kwargs.get('job_id')
    #
    #     job_id = request.env['hr.job'].sudo().search([()])
    #     print(job_id, 99999999999999999999999999999999999999999)
    #
    #     applicant_id = request.env['hr.applicant'].sudo().search([])
    #     print(job_id, 22222222222222222222222222222222222222222222222222)
    #     country = request.env['res.country'].sudo().search([])
    #
    #     data = {
    #         'job_id': job_id,
    #         'type_id': applicant_id,
    #         'country': country,
    #     }
    #     return request.render("recruitement_employee_form.recruitment_employee_form", data)


    @http.route('''/jobs/detail/<model("hr.job", "[('website_id', 'in', (False, current_website_id))]"):job>''', type='http', auth="public", website=True)
    def jobs_detail(self, job,**kwargs):
        if not job.can_access_from_current_website():
            raise NotFound()
        # job_id = request.env['hr.job'].sudo().search([()])
        # applicant_id = request.env['hr.applicant'].sudo().search([])
        country = request.env['res.country'].sudo().search([])
        # data = {
        #     'job_id': job_id.id,
        #     'type_id': applicant_id,
        #     'country': country,
        # }
        # return request.render("recruitement_employee_form.recruitment_employee_form", data)
        print(job.name,999999999999999999999998888888888888888888888888)
        print("Hello world",999999999999999999999998888888888888888888888888)


        return request.render("recruitement_employee_form.recruitment_employee_form", {
            'job': job.id,
            'job_id': job,
            'main_object': job,
            'country': country,

        })


    @http.route(['/jobs/apply/submit'], type='http', auth="public", website=True, method=['POST'])
    def job_form_submit(self, **kwargs):
        print(66666666666666666666666666666666, kwargs)
        name = kwargs.get('name')
        middle_name = kwargs.get('middle_name')
        Last_name = kwargs.get('Last_name')
        print(888888888888888888888888888888888888888888888, Last_name, middle_name)

        email_from = kwargs.get('email_from')
        partner_phone = kwargs.get('partner_phone')
        salary_expected = kwargs.get('salary_expected')
        address = kwargs.get('address')
        zip_code = kwargs.get('zip_code')
        city = kwargs.get('city')
        province = kwargs.get('province')
        birth_date = kwargs.get('birth_date')
        citizen = kwargs.get('citizen')
        worked_before = kwargs.get('worked_before')
        skills = kwargs.get('skills')
        qualification = kwargs.get('qualification')
        current_employment = kwargs.get('current_employment')
        position = kwargs.get('position')
        sallary = kwargs.get('salary_expected')
        reason = kwargs.get('reason')
        resume_attach = kwargs.get('resume_attach')
        signature_attach = kwargs.get('signature_attach')
        sallary = kwargs.get('sallary')
        country = kwargs.get('country')

        country = request.env['res.country'].sudo().search([('id', '=', country)])

        high_school = kwargs.get('high_school')
        number_of_years_attended = kwargs.get('number_of_years_attended')
        graduated = kwargs.get('graduated')
        area_of_Degree_stud = kwargs.get('area_of_Degree_stud')

        reference_1 = kwargs.get('reference_1')
        relationship = kwargs.get('relationship')
        years_Acquainted = kwargs.get('years_Acquainted')
        reference_1_phone = kwargs.get('reference_1_phone')
        reference_1_email = kwargs.get('reference_1_email')

        reference_2 = kwargs.get('reference_2')
        relationship_reference_2 = kwargs.get('relationship_reference_2')
        years_Acquainted_2 = kwargs.get('years_Acquainted_2')
        reference_2_phone = kwargs.get('reference_2_phone')
        reference_2_email = kwargs.get('reference_2_email')

        previous_employer_1 = kwargs.get('previous_employer_1')
        previous_employer_start_date = kwargs.get('previous_employer_start_date')
        previous_employer_end_date = kwargs.get('previous_employer_start_date_2')
        previous_employer_salary = kwargs.get('previous_employer_salary')
        previous_employer_position = kwargs.get('previous_employer_position')
        previous_employer_reasonleave = kwargs.get('previous_employer_reasonleave')

        previous_employer_2 = kwargs.get('previous_employer_2')
        previous_employer_start_date_2 = kwargs.get('previous_employer_start_date_2')
        previous_employer_end_date_2 = kwargs.get('previous_employer_end_date_2')
        previous_employer_salary_2 = kwargs.get('previous_employer_salary_2')
        previous_employer_position_2 = kwargs.get('previous_employer_position_2')
        previous_employer_reasonleave_2 = kwargs.get('previous_employer_reasonleave_2')

        reference_2_email = kwargs.get('reference_2_email')
        availability = kwargs.get('availability')
        empl_desired_sallary = kwargs.get('empl_desired_sallary')
        job_id = kwargs.get('job_id')
        applicant_request = request.env['hr.applicant'].sudo().create({
            'previous_employer_1': previous_employer_1,
            'previous_employer_start_date': previous_employer_start_date,
            'previous_employer_end_date': previous_employer_end_date,
            'previous_employer_salary': previous_employer_salary,
            'previous_employer_position': previous_employer_position,
            'previous_employer_reasonleave': previous_employer_reasonleave,

            'previous_employer_2': previous_employer_2,
            'previous_employer_start_date_2': previous_employer_start_date_2,
            'previous_employer_end_date_2': previous_employer_end_date_2,
            'previous_employer_salary_2': previous_employer_salary_2,
            'previous_employer_position_2': previous_employer_position_2,
            'previous_employer_reasonleave_2': previous_employer_reasonleave_2,


            'empl_desired_position_applying_for': job_id,
            'empl_desired_sallary': empl_desired_sallary,
            'desired_date': availability,

            'reference_1': reference_1,
            'relationship': relationship,
            'years_Acquainted': years_Acquainted,
            'reference_1_phone': reference_1_phone,
            'reference_1_email': reference_1_email,

            'reference_2': reference_2,
            'relationship_reference_2': relationship_reference_2,
            'years_Acquainted_2': years_Acquainted_2,
            'reference_2_phone': reference_2_phone,
            'reference_2_email': reference_2_email,

            'high_school': high_school,
            'number_of_years_attended': number_of_years_attended,
            'graduated': graduated,
            'area_of_Degree_stud': area_of_Degree_stud,
            # ' '.join([post.get('first_name'), post.get('middle_name'), post.get('last_name')]),

            'name': str(name) + ' ' + str(middle_name) + ' ' + str(Last_name),
            'email_from': email_from,
            'partner_phone': partner_phone,
            # 'salary_expected': salary_expected,
            'address': address,
            'zip_code': zip_code,
            'country': country.name,
            'city': city,
            'province': province,
            'birth_date': birth_date,
            'citizen': citizen,
            'worked_before': worked_before,
            'skills': skills,
            'qualification': qualification,
            'position': position,
            'sallary': sallary,
            'reason': reason,
            # 'sallary': sallary,
            'signature_attach': base64.encodestring(signature_attach.read()),
            'resume_attach': base64.encodestring(resume_attach.read())
        })
        return request.render("recruitement_employee_form.test_success", )

        # attachment_value = {
        #     'image': base64.encodestring(file.read())
        # }
        # application.sudo().update(attachment_value)
