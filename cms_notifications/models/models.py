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
    _name = 'cms.notification'
    _description = 'Notification'


    def get_default_user(self):
        return self.env.user.id

    name = fields.Char('Title')
    description = fields.Html('Description')
    url = fields.Html('link')
    date = fields.Datetime('Date', default=datetime.now())
    expiry = fields.Date('Expiry Date', default=date.today() + relativedelta(days=7))
    image = fields.Binary('Image', attachment=True)
    uploaded_by = fields.Many2one('res.users', 'Uploaded By', default= get_default_user)
    visible_for = fields.Selection([('faculty','Faculty'),('student','Student'),('all','All')], string='Visible For', default='all')
    priority = fields.Boolean('Visible Top', default=False)
    alert = fields.Boolean('alert', default=False)
    #recipient_ids = fields.Integer('Recipient',default=0)
    #student_ids = fields.Many2many('odoocms.student', 'notification_student_recipient_rel','recipient_id','student_id','Recipient', domain='student_domain')
    #faculty_ids = fields.Many2many('odoocms.faculty.staff', 'notification_faculty_recipient_rel', 'recipient_id', 'faculty_id', 'Recipient')
    recipient_ids = fields.Many2many('res.users', 'notification_recipient_rel', 'recipient_id', 'user_id', 'Recipient')
    #student_domain = fields.Char('Student Domain ', tracking=True)
    #faculty_domain = fields.Char('Faculty Domain', tracking=True)
    allow_preview = fields.Boolean('Allow Preview', default=True)

    #===========================================================================
    # @api.model
    # def create(self, values):
    #     print('Call Got')
    #     print (values)
    #     res = super(OdooCMSNotification, self).create(values)
    #     #=======================================================================
    #     # for student_id in values.student_domain:
    #     #     values.recipient_ids = student_id.id
    #     #     res = super(OdooCMSNotification, self).create(values)
    #     # for faculty_id in values.faculty_domain:
    #     #     values.recipient_ids = faculty_id.id
    #     #     res = super(OdooCMSNotification, self).create(values)
    #     #=======================================================================
    #     print (res)
    #     return res
    #===========================================================================