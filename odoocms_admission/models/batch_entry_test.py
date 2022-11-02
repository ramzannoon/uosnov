from odoo import fields, models, api, _


class BatchEntryTest(models.Model):
    _name = 'batch.entry.test'
    _description = 'Batch Entry Test'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    entry_test_date = fields.Datetime(string='Date')
    student_application_emails = fields.Char('Student Emails', compute="_get_students_email")
    state = fields.Selection([('draft', 'Draft'), ('mail_send', 'Mail Sent')], default='draft')

    student_application_ids = fields.Many2many('odoocms.application', 'batch_entry_test_id')

    @api.depends('student_application_emails')
    def _get_students_email(self):
        for rec in self:
            if rec.student_application_ids:
                std_emails = []
                for student in rec.student_application_ids:
                    if student.email:
                        std_emails.append(student.email)
                rec.student_application_emails = str(std_emails).replace("'", "").replace("[", "").replace("]", "")

    def send_entry_test_email(self):
        for rec in self:
            if rec.student_application_ids:
                ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
                self.ensure_one()
                template_id = self.env['ir.model.data'].xmlid_to_res_id(
                    'odoocms_admission.custom_mail_template_batch_entry_test', raise_if_not_found=False)

                self.ensure_one()
                ctx = {
                    'default_model': 'batch.entry.test',
                    'default_use_template': bool(template_id),
                    'default_template_id': template_id,
                    'default_composition_mode': 'comment',
                    'force_email': True,
                    'email_to': self.student_application_emails,
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
