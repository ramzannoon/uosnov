
from odoo import fields, models, api


class OdooCMSMeritStatus(models.TransientModel):
    _inherit = 'odoocms.merit.status'


    def change_status(self):
        self.merit_id.write({
            'state': self.state,
            'comments': self.comments,
        })
        self.locked = self.merit_id.locked

        if self.state in ('cancel', 'reject', 'absent'):
            self.merit_id.application_id.state = 'reject'
            self.merit_id.application_id.message_post(body='Admission Cancelled after listing in Merit list.')
        elif self.state == 'done' and self.merit_id.preference == 1:
            self.merit_id.application_id.state = 'approve'
            self.merit_id.application_id.locked = True
            self.merit_id.locked = True
        elif self.state == 'done':
            self.merit_id.application_id.state = 'approve'
        
        if self.locked:
            self.merit_id.application_id.locked = True

