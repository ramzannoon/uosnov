
from odoo import fields, models, api
from datetime import date
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import pdb


class OdooCMSMeritRegisterWizard(models.TransientModel):
    _inherit = 'odoocms.merit.register.wizard'


    # In Case of Change
    # #new_rep = fields.Selection([('new','New'),('edit','Edit')],'List', default='new')
    # #merit_list = fields.Many2one('odoocms.merit.register','Merit List')

    @api.depends('register_id')
    def _get_list(self):
        if self.register_id:
            if self.register_id.merit_register_id:
                if date.today() <= self.register_id.merit_register_id.date_end:
                    self.comment = "Closing date of %s mert list is %s. Please wait before closing date or change the closing Date!" % (self.register_id.merit_register_id.merit_list_id.name,self.register_id.merit_register_id.date_end,)
                else:
                    for app in self.register_id.merit_register_id.merit_application_ids.filtered(lambda l: l.state == 'draft' and l.voucher_image == None):
                        if date.today() > self.register_id.merit_register_id.date_end:
                            app.application_id.state = 'reject'
                            app.state = 'reject'
                            app.application_id.message_post(body='Admission Cancelled after listing in Merit list.')
                    # This is just to ensure all the applicants are processeed before generating next merit list.
                    if any([app.state == 'draft' for app in self.register_id.merit_register_id.merit_application_ids]):
                        self.comment = "Please Process %s Merit List before generating next." % (self.register_id.merit_register_id.merit_list_id.name,)

            next_number = self.register_id.merit_register_id and self.register_id.merit_register_id.merit_list_id.number + 1 or 1
            merit_list = self.env['odoocms.merit.list'].search([('number', '=', next_number)])
            if merit_list:
                self.name = merit_list.id
            else:
                self.comment = "There is no Merit List defined for Number %s" % (next_number,)

            allocation_id = self.env['odoocms.admission.allocation'].search([
                ('academic_session_id','=',self.register_id.academic_session_id.id)
            ])
            self.total_seats = sum(program.seats for program in allocation_id.seat_ids)
            locked = len(self.register_id.application_ids.filtered(lambda l: l.locked == True))
            self.merit_seats = self.total_seats - locked

    def generate_merit_register(self):
        if date.today() > self.register_id.merit_register_id.date_end:
            for app in self.register_id.merit_register_id.merit_application_ids.filtered(lambda l: l.state == 'draft' and l.voucher_image == None):
                app.application_id.state = 'reject'
                app.state = 'reject'
                app.application_id.message_post(body='Admission Cancelled after listing in Merit list.')

        data = {
            'register_id': self.register_id.id,
            'name': self.name.name + ' / ' + self.register_id.name,
            'date_list': self.date_list,
            'date_end': self.date_end,
            'merit_list_id': self.name.id,
            'remarks': self.remarks,
        }
        merit_register = self.env['odoocms.merit.register'].create(data)
        if self.register_id.merit_register_id:
            self.register_id.merit_register_id.next_merit_register_id = merit_register.id
            merit_register.prev_merit_register_id = self.register_id.merit_register_id.id
        else:
            self.register_id.first_merit_register_id = merit_register.id

        self.register_id.merit_register_id = merit_register.id
        self.register_id.merit_list(merit_register)


