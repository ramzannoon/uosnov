from odoo import fields, models, _, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools.safe_eval import safe_eval
import pdb
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from odoo.tools.safe_eval import safe_eval
from odoo import tools
import pdb
import logging
_logger = logging.getLogger(__name__)


class OdooCMSAdmissionApplicationDegree(models.Model):
    _name = 'odoocms.degree.list'
    _description = 'Applications for the admission'

    name = fields.Char('Degree Name', required=True)
    code = fields.Char('Code', required=True)

    sequence = fields.Integer('Sequence', default=10)
    group_ids = fields.One2many('odoocms.degee.lines','group_id','Groups')

    active = fields.Boolean(default=True)


class OdooCMSAdmissionApplicationDegreeLines(models.Model):
    _name = 'odoocms.degee.lines'
    _description = 'Applications for the admission'

    name = fields.Char('Degree Name')
    code = fields.Char('Code')
    group_id = fields.Many2one('odoocms.degree.list', string="Degree")

