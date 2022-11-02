import pdb
import calendar
from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    timetable_unitime = fields.Boolean(string="Unitime for Scheduling", config_parameter='odoocms.timetable_unitime')
    unitime_server = fields.Char(string="Unitime Server IP", config_parameter='odoocms.unitime_server')
    unitime_user = fields.Char(string="Unitime User", config_parameter='odoocms.unitime_user')
    unitime_pass = fields.Char(string="Unitime Pass", config_parameter='odoocms.unitime_pass')
    unitime_session = fields.Char(string="Unitime Session", config_parameter='odoocms.unitime_session')