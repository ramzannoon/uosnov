from odoo import fields, models, api, _


class CourseType(models.Model):
    _name = 'odoocms.course.type'
    _description = 'Course type'

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
