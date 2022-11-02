
from odoo import fields, models, api


class OdooCMSDegree(models.Model):
    _name = 'odoocms.degree'
    _description = 'Degree'

    name = fields.Char('Eligibility Criteria', required=True)
    code = fields.Char('Code', required=True)
    career_id = fields.Many2one('odoocms.career', string="Admission Career")
    sequence = fields.Integer('Sequence',default=10)
    active = fields.Boolean(default=True)

    program_ids = fields.Many2many('odoocms.program', 'program_degree_rel', 'degree_id', 'program_id', 'Programs')


class OdooCMSProgram(models.Model):
    _inherit = "odoocms.program"

    degree_ids = fields.Many2many('odoocms.degree','program_degree_rel','program_id','degree_id','Degrees')

# class OdooCmsDistrict(models.Model):
#     _name = 'odoocms.district'
#     _description = 'District'
#
#     province_id = fields.Many2one('odoocms.province', string="Province")
#     name = fields.Char('District Name',size=32, required=True)
#     code = fields.Char('Code', size=8, required=True)

