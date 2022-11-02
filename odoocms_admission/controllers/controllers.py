# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.http import request
from werkzeug.exceptions import NotFound


class OdoocmsAdmission(http.Controller):
    def sitemap_jobs(env, rule, qs):
        if not qs or qs.lower() in '/Admissions':
            yield {'loc': '/Admissions'}

    @http.route('/Admissions', auth='public',type='http',website=True,sitemap=sitemap_jobs)
    def admissions(self, **kwargs):
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        Admissions = env['odoocms.admission.register']
        domain = request.website.website_domain()
        register_ids = Admissions.search([('state','=','application')], order="website_published desc").ids
        Admissions = Admissions.sudo().browse(register_ids)

        return request.render("odoocms_admission.index", {
            'Admissions': Admissions,
         
        })



    @http.route('/Admissions/add', type='http', auth="user", website=True)
    def admissions_add(self, **kwargs):
        admission = request.env['odoocms.admission.register'].with_context(rendering_bundle=True).create({
            'name': _('admission Title'),
        })
        return request.redirect("/Admissions/details/%s?enable_editor=1" % slug(admission))

    
    @http.route('''/Admissions/detail/<model("odoocms.admission.register","[('website_id', 'in', (False, current_website_id))]"):admission>''', type='http', auth="public", website=True)
    def admissions_detail(self, admission, **kwargs):

        return request.render("odoocms_admission.detail", {
            'admission': admission,
            'main_object': admission,
        })


    @http.route('''/Admissions/apply/<model("odoocms.admission.register","[('website_id', 'in', (False, current_website_id))]"):admission>''', type='http', auth="public", website=True)
    def admissions_apply(self, admission, **kwargs):
        error = {}
        default = {}
        if 'odoocms_admission_error' in request.session:
            error = request.session.pop('odoocms_admission_error')
            default = request.session.pop('odoocms_admission_default')
        return request.render("odoocms_admission.apply", {
            'admission': admission,
            'error': error,
            'default': default,
        })
