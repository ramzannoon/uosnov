import pdb
from odoo import fields, models, api, _
import logging
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
 
    marks_rounding = fields.Char(string="Marks Rounding", config_parameter='odoocms.marks_rounding', default='0')
    gpa_rounding = fields.Char(string="GPA Rounding", config_parameter='odoocms.gpa_rounding', default='2')
    sgpa_rounding = fields.Char(string="SGPA Rounding", config_parameter='odoocms.sgpa_rounding', default='2')
    cgpa_rounding = fields.Char(string="CGPA Rounding", config_parameter='odoocms.cgpa_rounding', default='2')

    excluded_histogram_grades = fields.Char(string='Grades Excluded in Histogram', config_parameter='odoocms.excluded_histogram_grades', default='W,I,RW')
