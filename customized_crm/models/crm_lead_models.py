# -*- coding: utf-8 -*-
import datetime

import html2text

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, ValidationError


class CRMLean(models.Model):
    _inherit = "crm.lead"

    # Opportunity
    calls_opportunity = fields.Selection([("incoming", "Incoming Calls"),
                                          ("outgoing", "Outgoing Calls")], string="Calls")
    visitor_check = fields.Boolean(string="Visitor")
    pending_reasons_id = fields.Many2one('pending.reasons', string="Pending Reasons")
    lead_type_id = fields.Many2one('lead.type', string="Lead Type")

    date = fields.Date(string="Date")
    cnic = fields.Char(string="CNIC")
    inter_marks = fields.Integer(string="Intermediate Marks %")
    interested_program = fields.Many2one('odoocms.program', string="Interested Program")
    expected_visit = fields.Date(string="Expected Visit")
    reminder = fields.Date(string="Reminder")

    followup_1 = fields.Text(string="Followup 1")
    followup_2 = fields.Text(string="Followup 2")
    followup_3 = fields.Text(string="followup 3")

    compute_field = fields.Boolean(string="Sale Person Check", compute='_check_user')

    @api.onchange('stage_id')
    def stage_onchange(self):
        user = self.env.user
        if not user.has_group('customized_crm.group_mark_won_button'):
            if self.stage_id.is_won:
                raise ValidationError(_("You Don't Have Rights to Move on Won Stage"))

    @api.depends('compute_field')
    def _check_user(self):
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('base.user_admin'):
            self.compute_field = True
        else:
            self.compute_field = False

    def send_confirm_btn(self):
        notification_xml_id = 'customized_crm.lead_notification'
        notification_template_id = self.env.ref(notification_xml_id, False)
        current_date = datetime.date.today()
        crm_lead = self.env['crm.lead'].search([])
        for rec in crm_lead:
            if rec.user_id and rec.reminder:
                if current_date == rec.reminder:
                    rec.send_notification(rec.user_id, notification_template_id)

    def send_notification(self, partner, notification_template_id):
        """
        Main function for Send Notification
        """
        ctx = {
            'recipient_users': partner,
        }
        RenderMixin = self.env['mail.template'].with_context(**ctx)
        body_html = RenderMixin._render_template(notification_template_id.body_html, 'crm.lead', self.ids, post_process=True)[self.id]
        body = tools.html_sanitize(body_html)
        msg_body = html2text.html2text(body)
        self.message_post(body=msg_body, subtype="mail.mt_comment")
        return True

    def send_mail_msg(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self.env['ir.model.data'].xmlid_to_res_id(
            'customized_crm.mail_template_crm_lead', raise_if_not_found=False)

        self.ensure_one()
        ctx = {
            'default_model': 'crm.lead',
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True,
            'email_to': self.email_from,
            'res_id': self.id,
        }
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }
