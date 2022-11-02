from odoo import api, fields, models, _


class OdooCMSAdmissionSendEmail(models.TransientModel):
    _name = 'odoocms.send.email'
    _description = 'Send Email'

    def _get_applicants_ids(self):
        applicants = []
        if self.env.context.get('active_model', False) == 'odoocms.application' \
                and self.env.context.get('active_ids', False):
            for rec in self.env['odoocms.application'].browse(self.env.context.get('active_ids')):
                applicants.append(rec.id)
            return applicants

    application_ids = fields.Many2many('odoocms.application', string="Application Ids", default=_get_applicants_ids)

    def admission_send_email(self):
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        email_template_id = self.env.ref('odoocms_admission.mail_template_application').id
        ctx = dict(self.env.context or {})

        res_partners = []
        for rec in self:
            for student in rec.application_ids:
                if student.email:
                    res_partners_records = self.env["res.partner"].search([("name", "=", student.email)], limit=1)
                    if res_partners_records:
                        res_partners.append(res_partners_records.id)
        print(1111111111111111111, res_partners)

        ctx.update({
            'default_model': 'odoocms.send.email',
            'default_partner_ids': res_partners if res_partners else False,
            'active_model': 'odoocms.send.email',
            'active_id': self.ids[0],
            'default_res_id': self.ids[0],
            'default_use_template': bool(email_template_id),
            'default_template_id': email_template_id,
            'default_composition_mode': 'comment',
            'force_email': True,
        })
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
