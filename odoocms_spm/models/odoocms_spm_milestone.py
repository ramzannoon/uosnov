from odoo import models, fields, _, api


class OdooCMSStudentProjectMileStone(models.Model):
    _name = 'odoocms.student.project.milestone'
    _description = 'Student Project Milestone'
    _rec_name = 'name'

    name = fields.Char(string='Name', help='Name of Mile Stone', required=True)
    code = fields.Char(string='Code', help='Code of Mile Stone',required=True)
    effective_date = fields.Date(string='Effective Date', help='Effective Date of MileStone')
    status = fields.Boolean('Active', default=True,
                           help="Current Status of MileStone")