# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
import pdb
import logging

_logger = logging.getLogger(__name__)


class OdooCMSRoomGenerateWiz(models.TransientModel):
    _name = "odoocms.room.generate.wiz"
    _description = "This Wizard will Generate the Rooms From Start Number To End Number"

    start_num = fields.Integer('Start Number', default=1)
    end_num = fields.Integer('End Number', default=50)
    name_prefix = fields.Char('Room Name PreFix', default='Room#')
    name_postfix_length = fields.Integer('Name PostFix Length', default=3)
    notes = fields.Html('Notes')

    @api.constrains('start_num', 'end_num')
    def start_end_number_constrains(self):
        for rec in self:
            if rec.start_num <= 0:
                raise ValidationError(_('Start Number Should be Greater Then Zero.'))
            if rec.end_num <= 0:
                raise ValidationError(_('End Number Should be Greater Then Zero.'))
            if rec.end_num <= rec.start_num:
                raise ValidationError(_('End Number Should be Greater Then Start Number.'))

    def action_shift_student(self):
        for rec in self:
            if rec.start_num > 0 and rec.end_num > 0:
                for r in range(rec.start_num, rec.end_num + 1):
                    rr = str(r).zfill(rec.name_postfix_length)
                    r_name = rec.name_prefix + rr
                    already_exist = self.env['odoocms.rooms'].search([('name', '=', r_name)])
                    if not already_exist:
                        room_values = {
                            'room_no': rr,
                            'prefix': rec.name_prefix,
                            'name': r_name
                        }
                        new_rec = self.env['odoocms.rooms'].create(room_values)
                        _logger.info('New Room is Created %s' % new_rec.name)
                    else:
                        _logger.info('Room %s Already Exists ' % r_name)
