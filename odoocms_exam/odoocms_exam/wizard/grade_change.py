import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
from datetime import date , datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time


class OdooCMSCourseGradeChangeWiz(models.TransientModel):
    _name = 'odoocms.course.grade.change.wiz'
    _description = 'Course Grade Change Wizard'

    @api.model
    def _get_requests(self):
        if self.env.context.get('active_model', False) == 'odoocms.course.grade.change' and self.env.context.get('active_ids', False):
            return self.env.context['active_ids']

    request_ids = fields.Many2many('odoocms.course.grade.change', string = 'Grade Change Requests', default = _get_requests)


    def request_submit(self):
        for req in self.request_ids:
            req.action_submit()




