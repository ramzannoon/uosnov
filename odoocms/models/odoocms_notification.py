from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import logging
import re
import pdb
import sys
import ftplib
import os
import time
import base64
import codecs
from datetime import datetime, date
from odoo.http import request

_logger = logging.getLogger(__name__)


class OdooCMSNotification(models.Model):
    _name = 'odoocms.notification'
    _description = 'Notification'


    def get_default_user(self):
        return request.env.user.id

    name = fields.Char('Title')
    description = fields.Html('Description')
    date = fields.Datetime('Date', default=datetime.now())
    expiry = fields.Date('Expiry Date', default=date.today() + relativedelta(days=7))
    image = fields.Binary('Image', attachment=True)
    uploaded_by = fields.Many2one('res.users', 'Uploaded By', default= get_default_user)
    visible_for = fields.Selection([('faculty','Faculty'),('student','Student'),('all','All')], string='Visible For')
    allow_preview = fields.Boolean('Allow Preview', default=True)