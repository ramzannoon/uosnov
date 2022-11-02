
from odoo import fields, models, api


class OdooCMSMeritStatus(models.TransientModel):
    _name = 'odoocms.merit.status'
    _description = 'Merit Status'

    @api.model
    def _get_applicant(self):
        applicant_id = self.env['odoocms.application.merit'].browse(self._context.get('active_id', False))
        if applicant_id:
            return applicant_id.id
        return True
    
    merit_id = fields.Many2one('odoocms.application.merit', string='Applicant',default=_get_applicant)
    application_id = fields.Many2one('odoocms.application','Application',related='merit_id.application_id')
    amount = fields.Float('Amount',related='merit_id.amount')
    merit_register_id = fields.Many2one('odoocms.merit.register','Merit Register', related='merit_id.merit_register_id' )
    preference = fields.Integer('Preference',related='merit_id.preference')
    entryID = fields.Char('Entry ID',related='application_id.entryID')
    locked = fields.Boolean('Locked', default=False)
    comment = fields.Char()
    comments = fields.Text('Comments')
    state = fields.Selection([
        ('draft', 'Draft'), ('done', 'Done'), ('cancel', 'Cancel'), ('reject', 'Rejected'), ('absent', 'Absent')
    ], 'Status', default='draft')

    @api.onchange('state')
    def onchange_state(self):
        self.comment = ''
        if self.state == 'done' and self.amount > 0:
            if not self.env['odoocms.admission.confirm.fee'].search([
                    ('application_id', '=', self.application_id.id), ('merit_id', '=', False), ('amount', '=', self.amount)]):
                self.comment = "Please Process/Enter Fee before Confirming the Admission."
        

    def change_status(self):
        fee_rec = self.env['odoocms.admission.confirm.fee'].search([
            ('application_id', '=', self.application_id.id), ('merit_id', '=', False), ('amount', '=', self.amount)])
        fee_rec.write({
            'state': 'done',
            'merit_id': self.merit_id.id ,
        })
       
        self.merit_id.write({
            'state': self.state,
            'locked': self.locked,
            'comments': self.comments,
        })
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

