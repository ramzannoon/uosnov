import pdb
import time
from odoo import api, fields, models,_, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class RegisterDueDateWizard(models.TransientModel):
    _name = 'register.due.date.wizard'
    _description = 'Register Due Date Wizard'

    @api.model
    def _get_register(self):
        if self.env.context.get('active_model', False) == 'odoocms.admission.register' and self.env.context.get('active_id', False):
            return self.env.context['active_id']
        
    register_id = fields.Many2one('odoocms.admission.register', 'Admission Register', required=True,default=_get_register)
    current_due_date = fields.Date('Current Due Date')
    new_due_date = fields.Date('New Due Date',required=True)

    @api.onchange('register_id')
    def onchange_register(self):
        self.current_due_date = self.register_id.date_end
        
    def set_due_date(self):
        self.register_id.date_end = self.new_due_date
        return {'type': 'ir.actions.act_window_close'}
        




