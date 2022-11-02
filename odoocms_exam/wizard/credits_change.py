import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
from datetime import date , datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time


class OdooCMSExamCreditChangeWiz(models.TransientModel):
    _name = 'odoocms.exam.credit.change.wiz'
    _description = 'Exam Credits Change Wizard'

    @api.model
    def _get_class(self):
        if self.env.context.get('active_model', False) == 'odoocms.class' and self.env.context.get('active_id', False):
            return self.env.context['active_id']

    @api.model
    def _get_credits(self):
        if self.env.context.get('active_model', False) == 'odoocms.class' and self.env.context.get('active_id', False):
            class_id = self.env['odoocms.class'].browse(self.env.context['active_id'])
            return class_id.weightage
        
    class_id = fields.Many2one('odoocms.class', string = 'Class', default = _get_class)
    prev_credits = fields.Integer('Current Credits', default=_get_credits)
    new_credits = fields.Integer('New Credits')


    def set_credits(self):
        self.class_id.weightage = self.new_credits
        for registration in self.class_id.registration_ids:
            registration.credits = self.new_credits




