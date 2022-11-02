from odoo import _, api, fields, models
from odoo.odoo.exceptions import UserError
from odoo.odoo.http import content_disposition

import re

from odoo import fields, models, _, api
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.tools.safe_eval import safe_eval
import pdb
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from odoo.http import content_disposition, Controller, request, route
import random


class Notice(models.Model):
    _name = "documents.notice"
    _description = "Documents Notice"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Notice", required=True, track_visibility='onchange')
    court_name = fields.Char(string="Court Name", required=True, track_visibility='onchange')
    adjudication_elements_id = fields.Many2one('adjudication.elements',required=True, string="Adjudication elements", track_visibility='onchange')
    description = fields.Html(string="Description")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('send_for_approval', 'Send For Approval'),
        ('done', 'Done')], tracking=True, string='States', default='draft')

    def send_for_approval_btn(self):
        self.write({"state": "send_for_approval"})

    def approve_btn(self):
        self.write({"state": "done"})

    def _show_report(self, model, report_type, report_ref, download=False):
        if report_type not in ('html', 'pdf', 'text'):
            raise UserError(_("Invalid report type: %s") % report_type)

        # method_name = 'render_qweb_%s' % (report_type)
        # report = getattr(report_sudo, method_name)([model.id], data={'report_type': report_type})[0]
        report = self.env.ref(report_ref).render_qweb_pdf(model.ids)[0]
        reporthttpheaders = [
            ('Content-Type', 'application/pdf' if report_type == 'pdf' else 'text/html'),
            ('Content-Length', len(report)),
        ]
        if report_type == 'pdf' and download:
            filename = "%s.pdf" % (re.sub('\W+', '-', model.application_no))
            reporthttpheaders.append(('Content-Disposition', content_disposition(filename)))

            if report_ref == 'odoocms_employee_portal.notice_report_template':
                self.write({
                    'application_download_date': date.today(),
                })
        return request.make_response(report, headers=reporthttpheaders)

