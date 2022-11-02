from datetime import datetime, date

from odoo import _, api, fields, models
# from odoo import datetime
from odoo.exceptions import ValidationError
from datetime import datetime


class TravelRequests(models.Model):
    _name = "emp.travel.request"
    _description = "Employee Travelling Requests"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2one('hr.employee', string="Employees", required=True)
    name = fields.Char(string="Name", )
    location = fields.Char(string="location", required=True, )
    date_to = fields.Date(string="End Date")
    # compute = "change_date"
    date_from = fields.Date(string="From Date")
    state = fields.Selection(
        [('to_approve', 'To Approve'), ('approve', 'Approve'), ('refuse', 'Refuse')
         ], string='Status',
        default='to_approve')

    @api.onchange('date_to')
    def check_previous_date(self):
        current_date = datetime.today().date()
        for rec in self:
            if rec.date_to:
                if rec.date_to < current_date:
                    raise ValidationError("Selected today's Date >>>>>>>>>>>>>>")



    # @api.onchange('date_from')
    # def onchange_date(self):
    #     current_date = datetime.date.today()
    #     print(current_date)
    #     if self.date_from :
    #         print("ahsannnn")
    #     else:
    #         print("saddd")
    #
    #
    # @api.onchange('date_from')
    # def _onchange_start_date(self):
    #     current_date = datetime.date.today()
    #
    #     if self.date_from:
    #         self.current_date = datetime.datetime.combine(self.current_date, datetime.time.min)

    # @api.onchange('stop_date')
    # def _onchange_stop_date(self):
    #     if self.stop_date:
    #         self.stop = datetime.datetime.combine(self.stop_date, datetime.time.max)

    def button_to_approve(self):
        self.write({'state': "approve"})

    def button_refuse(self):
        self.write({'state': "refuse"})
