import logging
from odoo.tools.translate import _
from odoo.tools import email_split
from odoo.exceptions import UserError
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


def extract_email(email):
    """ extract the email address from a user-friendly email address """
    addresses = email_split(email)
    return addresses[0] if addresses else ''


class EmployeePortalWizard(models.TransientModel):
    _name = 'employee.portal.wizard.actser'
    _description = 'Employee Portal Access'

    def _default_user_ids(self):
        # for each partner, determine corresponding portal.wizard.user records
        partner_ids = self.env.context.get('active_ids', [])
        contact_ids = set()
        user_changes = []
        for partner in self.env['hr.employee'].sudo().browse(partner_ids):
            print("employeeeeeeeeeeeeeeeess", partner)
            contact_partners = partner.child_ids.filtered(lambda p: p.type in ('employee', 'other')) | partner
            print("employeeeeeeeeeeeeeeeess 2", contact_partners)

            for contact in contact_partners:
                # make sure that each contact appears at most once in the list
                if contact.id not in contact_ids:
                    print("employeeeeeeeeeeeeeeeess 3", contact.id,contact_ids,)

                    contact_ids.add(contact.id)
                    in_portal = False
                    print("employeeeeeeeeeeeeeeeess 3.5", contact_ids, in_portal)

                    # if contact.user_ids:
                    #     print("employeeeeeeeeeeeeeeeess 4", contact, in_portal,)
                    #
                    #     in_portal = self.env.ref('base.group_portal') in contact.user_ids[0].groups_id
                    #     print("employeeeeeeeeeeeeeeeess 5", in_portal,)

                    user_changes.append((0, 0, {
                        'partner_id': contact.id,
                        'email': contact.work_email,
                        'in_portal': in_portal,
                    }))
                    print("employeeeeeeeeeeeeeeeess 6", user_changes)

        return user_changes

    user_ids = fields.One2many('portal.wizard.user.new', 'wizard_id', string='Users', default=_default_user_ids)
    welcome_message = fields.Text('Invitation Message',
                                  help="This text is included in the email sent to new users of the portal.")

    def action_apply(self):
        self.ensure_one()
        self.user_ids.action_apply()
        return {'type': 'ir.actions.act_window_close'}


class PortalWizardUser(models.TransientModel):
    _name = 'portal.wizard.user.new'
    _description = 'Portal User Config'

    wizard_id = fields.Many2one('employee.portal.wizard.actser', string='Wizard', required=True, ondelete='cascade')
    partner_id = fields.Many2one('hr.employee', string='Contact', required=True, readonly=True, ondelete='cascade')
    email = fields.Char('Email')
    in_portal = fields.Boolean('In Portal')
    user_id = fields.Many2one('res.users', string='Login User')

    def get_error_messages(self):
        emails = []
        partners_error_empty = self.env['res.partner']
        partners_error_emails = self.env['res.partner']
        partners_error_user = self.env['res.partner']
        partners_error_internal_user = self.env['res.partner']

        for wizard_user in self.with_context(active_test=False).filtered(
                lambda w: w.in_portal and not w.partner_id):
            email = extract_email(wizard_user.email)
            if not email:
                partners_error_empty |= wizard_user.partner_id
            elif email in emails:
                partners_error_emails |= wizard_user.partner_id
            user = self.env['res.users'].sudo().with_context(active_test=False).search([('login', '=ilike', email)])
            if user:
                partners_error_user |= wizard_user.partner_id
            emails.append(email)

        # for wizard_user in self.with_context(active_test=False):
        #     if any(u.has_group('base.group_user') for u in wizard_user.sudo().partner_id):
        #         partners_error_internal_user |= wizard_user.partner_id

        error_msg = []
        if partners_error_empty:
            error_msg.append("%s\n- %s" % (_("Some contacts don't have a valid email: "),
                                           '\n- '.join(partners_error_empty.mapped('display_name'))))
        if partners_error_emails:
            error_msg.append("%s\n- %s" % (_("Several contacts have the same email: "),
                                           '\n- '.join(partners_error_emails.mapped('email'))))
        if partners_error_user:
            error_msg.append("%s\n- %s" % (_("Some contacts have the same email as an existing portal user:"),
                                           '\n- '.join(
                                               ['%s <%s>' % (p.display_name, p.email) for p in partners_error_user])))
        if partners_error_internal_user:
            error_msg.append("%s\n- %s" % (_("Some contacts are already internal users:"),
                                           '\n- '.join(partners_error_internal_user.mapped('email'))))
        if error_msg:
            error_msg.append(_("To resolve this error, you can: \n"
                               "- Correct the emails of the relevant contacts\n"
                               "- Grant access only to contacts with unique emails"))
            error_msg[-1] += _("\n- Switch the internal users to portal manually")
        return error_msg

    def action_apply(self):
        self.env['res.partner'].check_access_rights('write')
        """ From selected partners, add corresponding users to chosen portal group. It either granted
            existing user, or create new one (and add it to the group).
        """
        error_msg = self.get_error_messages()
        if error_msg:
            raise UserError("\n\n".join(error_msg))

        for wizard_user in self.sudo().with_context(active_test=False):

            group_portal = self.env.ref('base.group_portal')
            # Checking if the partner has a linked user
            # user = wizard_user.partner_id if wizard_user.partner_id else None
            user = self.env['res.users'].search([('name', '=', wizard_user.partner_id.name),
                                                 ('login', '=', wizard_user.email)])
            print(111111111111111111111111111, user)
            # update partner email, if a new one was introduced
            if wizard_user.partner_id.work_email != wizard_user.email:
                wizard_user.partner_id.write({'work_email': wizard_user.email})
            # add portal group to relative user of selected partners
            if wizard_user.in_portal:
                print(999999999999999999)
                if not user:
                    print(888888888888888888)
                    if wizard_user.partner_id:
                        partner_id = wizard_user.partner_id.id
                    else:
                        partner_id = self.env.company.id

                    user_portal = wizard_user.sudo().with_context(partner_id=partner_id)._create_user()
                    # user_portal.write({'groups_id': [(3, group_portal.id)], 'active': False})

                    if user_portal:
                        wizard_user.partner_id.update({
                            'user_id': user_portal.id,
                        })
                else:
                    user_portal = user
                # wizard_user.write({'user_id': user_portal.id})
                # if not wizard_user.user_id.active or group_portal not in wizard_user.user_id.groups_id:
                #     wizard_user.user_id.write({'active': True, 'groups_id': [(4, group_portal.id)]})
                #     # prepare for the signup process
                #     wizard_user.user_id.partner_id.signup_prepare()
                # wizard_user.with_context(active_test=True)._send_email()
                # wizard_user.refresh()
            else:
                # remove the user (if it exists) from the portal group
                if user and group_portal in user.groups_id:
                    # if user belongs to portal only, deactivate it
                    if len(user.groups_id) <= 1:
                        user.write({'groups_id': [(3, group_portal.id)], 'active': False})
                    else:
                        user.write({'groups_id': [(3, group_portal.id)]})

    def _create_user(self):
        uuuu = self.env['res.users'].search([])
        x_group_portal_user = self.env.ref('base.group_portal')

        return self.env['res.users'].with_context(no_reset_password=True).create({
            'name': self.partner_id.name,
            'email': extract_email(self.email),
            'login': extract_email(self.email),
            # 'partner_id': self.partner_id.id,
            'company_id': self.partner_id.company_id.id,
            'user_type': 'public',
            'groups_id': [(6, 0, [x_group_portal_user.id])],
        })

    def _send_email(self):
        """ send notification email to a new portal user """
        if not self.env.user.email:
            raise UserError(_('You must have an email address in your User Preferences to send emails.'))

        # determine subject and body in the portal user's language
        template = self.env.ref('portal.mail_template_data_portal_welcome')
        for wizard_line in self:
            lang = wizard_line.user_id.lang
            partner = wizard_line.user_id.partner_id

            portal_url = partner.with_context(signup_force_type_in_url='', lang=lang)._get_signup_url_for_action()[
                partner.id]
            partner.signup_prepare()

            if template:
                template.with_context(dbname=self._cr.dbname, portal_url=portal_url, lang=lang).send_mail(
                    wizard_line.id, force_send=True)
            else:
                _logger.warning("No email template found for sending email to the portal user")

        return True
