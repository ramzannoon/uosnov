from odoo import fields, models, api, _


class BatchInterview(models.Model):
    _name = 'batch.interview'
    _description = 'Batch Interview'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    interview_date = fields.Datetime(string='Date')
    student_application_emails = fields.Char('Student Emails', compute="_get_students_email")
    state = fields.Selection([('draft', 'Draft'), ('mail_send', 'Mail Sent')], default='draft')

    bi_student_application_ids = fields.Many2many('odoocms.application', 'batch_interview_id')

    @api.depends('student_application_emails')
    def _get_students_email(self):
        for rec in self:
            if rec.bi_student_application_ids:
                std_emails = []
                for student in rec.bi_student_application_ids:
                    if student.email:
                        std_emails.append(student.email)
                rec.student_application_emails = str(std_emails).replace("'", "").replace("[", "").replace("]", "")

    def send_interview_email(self):
        for rec in self:
            if rec.bi_student_application_ids:
                ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
                self.ensure_one()
                template_id = self.env['ir.model.data'].xmlid_to_res_id(
                    'odoocms_admission.custom_mail_template_batch_interview', raise_if_not_found=False)

                self.ensure_one()
                print(1111111111111111111111, self.student_application_emails)
                ctx = {
                    'default_model': 'batch.interview',
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


class MailComposeMessageBI(models.TransientModel):
    _inherit = 'mail.compose.message'

    def action_send_mail(self):
        model = self._context.get('res_model')
        res_model = self._context.get('default_model')
        state = self._context.get('state')

        if res_model == 'batch.interview':
            batch_interview = self.env['batch.interview'].browse(self.res_id)
            batch_interview.write({'state': 'mail_send'})
            for lines in batch_interview.bi_student_application_ids:
                if lines.email:
                    lines.write({'state': 'interview'})
                    lines.message_post(body=f'{self.body}')
            return super(MailComposeMessageBI, self).action_send_mail()

        if res_model == 'batch.entry.test':
            batch_entry_test = self.env['batch.entry.test'].browse(self.res_id)
            if batch_entry_test:
                batch_entry_test.write({'state': 'mail_send'})
                for lines in batch_entry_test.student_application_ids:
                    if lines.email:
                        lines.write({'state': 'entry_test'})
                        lines.message_post(body=f'{self.body}')
                return super(MailComposeMessageBI, self).action_send_mail()

        if res_model == 'batch.offered.program':
            batch_offered_program = self.env['batch.offered.program'].browse(self.res_id)
            if batch_offered_program:
                batch_offered_program.write({'state': 'mail_send'})
                for lines in batch_offered_program.student_application_ids:
                    if lines.email:
                        lines.write({'state': 'offered_program'})
                        lines.message_post(body=f'{self.body}')
                return super(MailComposeMessageBI, self).action_send_mail()

        if model == 'odoocms.application' and state == 'approve':
            student_entry_test = self.env['odoocms.application'].browse(self.res_id)
            if student_entry_test.email:
                student_entry_test.write({'state': 'entry_test'})
            return super(MailComposeMessageBI, self).action_send_mail()

        elif model == 'odoocms.application' and state == 'entry_test':
            student_interview = self.env['odoocms.application'].browse(self.res_id)
            if student_interview.email:
                student_interview.write({'state': 'interview'})
            return super(MailComposeMessageBI, self).action_send_mail()

        elif model == 'odoocms.application' and state == 'interview':
            student_interview = self.env['odoocms.application'].browse(self.res_id)
            if student_interview.email:
                student_interview.write({'state': 'offered_program'})
            return super(MailComposeMessageBI, self).action_send_mail()

        elif res_model == 'odoocms.application':
            odoocms_application = self.env['odoocms.application'].browse(self.res_id)
            for line in odoocms_application:
                if line.email:
                    line.write({'state': 'reject'})
            return super(MailComposeMessageBI, self).action_send_mail()
        else:
            return super(MailComposeMessageBI, self).action_send_mail()
