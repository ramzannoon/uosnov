from odoo import http
from odoo.http import request
from odoo.addons.odoocms_faculty_portal.controllers import main as faculty_main
from datetime import date, datetime, timedelta
# from . import odo
import pdb

class test(http.Controller):



    @http.route(['/faculty/project/detail/update'], type='http', auth="user", website=True, method=['GET', 'POST'],
                csrf=False)
    def project_spm_save(self, **kw):
        try:
            values, success, faculty_staff = faculty_main.prepare_portal_values(request)
            if not success:
                return request.render("odoocms_web.portal_error", values)

            milestone_ids = request.httprequest.form.getlist('milestone_ids')
            project_id = request.httprequest.form['project']
            project = request.env['odoocms.student.project'].sudo().search([('id', '=', project_id)])
            milestone_lines =[]
            values = {}
            if milestone_ids and len(milestone_ids) > 0:
                selected_milestones = request.env['odoocms.student.project.milestone'].sudo().search(
                    [('id', 'in', list(map(int, milestone_ids)))])

                # for rec in selected_milestones:
                #
                #     values = [(0, 0, {
                #         'milestone_id': rec.id,
                #     })]
                #     milestone_lines.append(values)


                # print(values)
                # print(milestone_lines)
                # print(selected_milestones)
                # return
                if selected_milestones:
                    values['selected_milestone_ids'] = [(6, 0, selected_milestones.ids)]

                if project:
                    # project.selected_milestone_ids.milestone_id = milestone_lines

                    # project.sudo().write({
                    #     'selected_milestone_ids.milestone_id' : milestone_lines
                    # })
                    project.sudo().write(values)

            return request.redirect('/faculty/projects')

        except Exception as e:
            values = {
                'error_message': e or False
            }
        return http.request.render('odoocms_web.portal_error', values)