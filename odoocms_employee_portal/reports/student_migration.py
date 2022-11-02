from odoo import api, models
import time
from odoo import api, models, fields, _
from dateutil.parser import parse
from odoo.exceptions import UserError

#
# class StudentLeavingLetter(models.AbstractModel):
#     _name = "report.odoocms_employee_portal.student_migration_report_template"
#
#     @api.model
#     def _get_report_values(self, docids, data=None):
#         print(11111111111111111111, docids)
#         docs = self.env[''].browse(docids)
#         return {
#             'docs': docs,
#             'data': data,
#         }