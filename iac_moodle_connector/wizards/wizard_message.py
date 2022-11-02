# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning


class IacWizardMessage(models.TransientModel):
    _name = "iac.wizard.message"
    _description = "Message Wizard"

    text = fields.Text(string='Message')

    @api.model
    def genrated_message(self, message, name='Message/Summary'):
        res = self.create({'text': message})
        return {
            'name': name,
            'type': 'ir.actions.act_window',
            'res_model': 'iac.wizard.message',
            'view_mode': 'form',
            'target': 'new',
            'res_id': res.id,
        }
