from odoo import api, fields, models, _


class OdooCMSAdmissionLead(models.TransientModel):
    _name = 'odoocms.admission.lead'
    _description = 'Admission Lead'

    def _get_applicants_ids(self):
        applicants = []
        if self.env.context.get('active_model', False) == 'odoocms.application' \
                and self.env.context.get('active_ids', False):
            for rec in self.env['odoocms.application'].browse(self.env.context.get('active_ids')):
                applicants.append(rec.id)
            return applicants

    application_ids = fields.Many2many('odoocms.application', string="Application Ids", default=_get_applicants_ids)
    sales_person = fields.Many2one('res.users')

    def generate_admission_lead(self):
        applications_list = []
        for applicant in self.application_ids:
            if not applicant.lead_generate:
                name = ""
                if applicant.first_name:
                    name += applicant.first_name
                if applicant.middle_name:
                    name += " " + applicant.middle_name
                if applicant.last_name:
                    name += " " + applicant.last_name

                values = {
                    'name': name,
                    'calls_opportunity': 'outgoing',
                    'phone': applicant.mobile,
                    'user_id': self.sales_person.id,
                }
                crm_lead_rec = self.env['crm.lead'].sudo().create(values)
                if crm_lead_rec:
                    applicant.lead_generate = True
                applications_list.append(crm_lead_rec.id)
        return {
            'domain': [('id', 'in', applications_list)],
            'name': _('CRM LEAD'),
            'view_mode': 'tree,form',
            'res_model': 'crm.lead',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }
