
from odoo import fields, models, api, _


class OdooCMSShortCourse(models.Model):
    _name = "odoocms.short.course"
    _description = "CMS Short Course"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    department_id = fields.Many2one('odoocms.department', string="Department")

    _sql_constraints = [
        ('code', 'unique(code)', "Code already exists "),
    ]

    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.department_id:
                name = name + ' - ' + (
                            record.department_id.institute_id and record.department_id.institute_id.code or '')
            res.append((record.id, name))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            recs = self.search([('name', operator, name)] + (args or []), limit=limit)
            if not recs:
                recs = self.search([('code', operator, name)] + (args or []), limit=limit)
            return recs.name_get()
        return super().name_search(name, args=args, operator=operator, limit=limit)

