# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
import pdb
import logging

_logger = logging.getLogger(__name__)


class OdooCMSHostelRoomMappingWiz(models.TransientModel):
    _name = "odoocms.hostel.room.mapping.wiz"
    _description = "This Wizard will Map The Rooms With Hostel Rooms."

    hostel_id = fields.Many2one('odoocms.hostel', 'Hostel')
    room_type = fields.Many2one('odoocms.hostel.room.type', 'Room Type')
    floor_id = fields.Many2one('odoocms.hostel.floor', 'Floor')
    room_ids = fields.Many2many('odoocms.rooms', 'hostel_room_mapping_wiz_rel', 'wiz_id', 'room_id', 'Rooms')

    def action_create_room_mapping_detail(self):
        for rec in self:
            new_room_list = []
            if rec.room_ids:
                for room_id in rec.room_ids:
                    rec_already_exit = self.env['odoocms.hostel.room'].search([('room_id', '=', room_id.id),
                                                                               ('hostel_id', '=', rec.hostel_id.id),
                                                                               ('room_type', '=', rec.room_type.id),
                                                                               ('floor_no', '=', rec.floor_id.id)])
                    if not rec_already_exit:
                        room_values = {
                            'room_id': room_id.id,
                            'room_type': rec.room_type and rec.room_type.id or False,
                            'hostel_id': rec.hostel_id and rec.hostel_id.id or False,
                            'floor_no': rec.floor_id and rec.floor_id.id or False,
                            'room_capacity': rec.room_type.capacity,
                            'per_month_rent': rec.room_type.per_month_rent,
                        }
                        new_rec = self.env['odoocms.hostel.room'].create(room_values)
                        new_room_list.append(new_rec.id)
            else:
                raise ValidationError(_("Please Select the Rooms."))

            if new_room_list:
                return {
                    'domain': [('id', 'in', new_room_list)],
                    'name': _('Hostel Rooms'),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'odoocms.hostel.room',
                    'view_id': False,
                    # 'context': {'default_class_id': self.id},
                    'type': 'ir.actions.act_window'
                }
            else:
                return {'type': 'ir.actions.act_window_close'}
