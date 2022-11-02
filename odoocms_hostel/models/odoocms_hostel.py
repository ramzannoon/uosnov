# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import pdb
import logging

_logger = logging.getLogger(__name__)


class OdooCMSHostel(models.Model):
    _name = 'odoocms.hostel'
    _description = "Hostel"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    name = fields.Char(string="Name", required=True, tracking=True)
    code = fields.Char(string="Code", tracking=True)
    hostel_floors = fields.Char(string="Floors Limit", default='10')
    hostel_rooms = fields.One2many('odoocms.hostel.room', 'hostel_id', string="Rooms")

    hostel_warden = fields.Many2one('odoocms.hostel.warden', string="Manager Hostel", tracking=True, index=True, ondelete='restrict')
    warden_email = fields.Char('Manager Email', compute="get_warden_data", store=True, tracking=True)
    warden_mobile = fields.Char('Manager Mobile', compute="get_warden_data", store=True, tracking=True)
    hostel_type = fields.Many2one('odoocms.hostel.type', 'Type', tracking=True, index=True, ondelete='restrict')

    hostel_capacity = fields.Integer(string="Capacity", tracking=True, compute="_compute_student_total", store=True)
    total_students = fields.Integer(string="Total Students", compute="compute_total_student", store=True, tracking=True)
    total_rooms = fields.Integer(string="Total Rooms", compute="_compute_student_total", store=True, tracking=True)
    total_floors = fields.Char(string="Total Floors", compute="_compute_student_total", store=True, tracking=True)
    vacancy = fields.Integer(string="Vacancy", compute="_compute_student_total", store=True, tracking=True)
    allocated_number = fields.Integer(string="Allocated", compute="_compute_student_total", store=True, tracking=True)

    total_single_rooms = fields.Integer(string="Single Bed Rooms", compute="_compute_student_total", store=True)
    total_double_rooms = fields.Integer(string="Double Bed Rooms", compute="_compute_student_total", store=True)
    total_double_rooms2 = fields.Integer(string="Double Bed Rooms2", compute="_compute_student_total", store=True)
    total_triple_rooms = fields.Integer(string="Triple Bed Rooms", compute="_compute_student_total", store=True)

    single_bed_vacant = fields.Integer(string="Single Bed Vacant", compute="_compute_student_total", store=True)
    double_bed_vacant = fields.Integer(string="Double Bed Vacant", compute="_compute_student_total", store=True)
    double_bed_vacant2 = fields.Integer(string="Double Bed Vacant2", compute="_compute_student_total", store=True)
    triple_bed_vacant = fields.Integer(string="Triple Bed Vacant", compute="_compute_student_total", store=True)
    total_vacant = fields.Integer(string="Total Vacant", compute="_compute_student_total", store=True)

    full_occupied_single_bed = fields.Integer(string="Single Bed Fully Occupied", compute="_compute_student_total", store=True)
    full_occupied_double_bed = fields.Integer(string="Double Bed Fully Occupied", compute="_compute_student_total", store=True)
    full_occupied_double_bed2 = fields.Integer(string="Double Bed Fully Occupied2", compute="_compute_student_total", store=True)
    full_occupied_triple_bed = fields.Integer(string="Triple Bed Fully Occupied", compute="_compute_student_total", store=True)
    fully_occupied_total = fields.Integer(string="Fully Occupied Total", compute="_compute_student_total", store=True)

    double_partial_occupied_bed = fields.Integer(string="Double Bed Partial Occupied", compute="_compute_student_total", store=True)
    double_partial_occupied_bed2 = fields.Integer(string="Double Bed Partial Occupied2", compute="_compute_student_total", store=True)
    triple_partial_occupied_bed = fields.Integer(string="Triple Bed Partial Occupied", compute="_compute_student_total", store=True)
    partially_occupied_total = fields.Integer(string="Partially Occupied Total", compute="_compute_student_total", store=True)

    room_rent = fields.Char(string="Room Rent", required=False, tracking=True)
    mess_fee = fields.Char(string="Mess Fee", required=False, tracking=True)
    color = fields.Integer(string='Color Index')

    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip', change_default=True)
    city = fields.Char('City', tracking=True)
    state_id = fields.Many2one("res.country.state", string='State')
    country_id = fields.Many2one('res.country', string='Country')
    phone = fields.Char('Phone', tracking=True)
    mobile = fields.Char('Mobile', tracking=True)
    email = fields.Char('Email', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=1)
    active = fields.Boolean('Active', default=True, tracking=True)
    to_be = fields.Boolean('To Be', default=False)
    student_ids = fields.One2many('odoocms.student', 'hostel_id', 'Students')
    faculty_ids = fields.One2many('odoocms.faculty.staff', 'hostel_id', 'Students')
    floor_ids = fields.One2many('odoocms.hostel.floor', 'hostel_id', 'Floors')

    unit_ids = fields.One2many('odoocms.hostel.free.units', 'hostel_id', ' Fee Units Detail')
    electrical_meter_no = fields.Char('Electrical Meter No.')
    sui_gas_meter_no = fields.Char('Sui Gas Meter No.')

    hostel_supervisor = fields.Char(string="Caretaker")
    supervisor_mobile = fields.Char(string='Caretaker Mobile')
    wing_ids = fields.Many2many('odoocms.hostel.wings', 'hostel_wings_rel_table', 'hostel_id', 'wing_id', 'Wings')
    state = fields.Selection([('draft', 'Draft'), ('lock', 'Locked')], string='Status', default='draft', tracking=True)
    user_ids = fields.Many2many('res.users', 'odoocms_hostel_users_rel', 'hostel_id', 'user_id', string='Users')

    @api.depends('student_ids', 'hostel_rooms', 'hostel_rooms.room_capacity',
        'student_ids.hostel_id', 'student_ids.room_id', 'hostel_rooms.student_ids')
    def _compute_student_total(self):
        """compute the vacancy,total students and hostel capacity"""
        for dt in self:
            total_vacancy = 0
            allocated = 0
            capacity = 0

            single_rooms = 0
            double_rooms = 0
            double_rooms2 = 0
            triple_rooms = 0

            single_vacant = 0
            double_vacant = 0
            double_vacant2 = 0
            triple_vacant = 0

            single_fully_occupied = 0
            double_fully_occupied = 0
            double_fully_occupied2 = 0
            triple_fully_occupied = 0

            double_partial_occupied = 0
            double_partial_occupied2 = 0
            triple_partial_occupied = 0

            if dt.hostel_rooms:
                dt.total_rooms = len(dt.hostel_rooms)
            if dt.floor_ids:
                dt.total_floors = len(dt.floor_ids)

            for rm in dt.hostel_rooms:
                total_vacancy += rm.vacancy and int(rm.vacancy) or 0
                allocated += rm.allocated_number and int(rm.allocated_number) or 0
                capacity += rm.room_capacity and int(rm.room_capacity) or 0
                # room_type---->1 it is Single or Cubicle
                if rm.room_type.id==1:
                    single_rooms += 1
                    if int(rm.allocated_number)==0:
                        single_vacant += 1
                    if int(rm.allocated_number)==int(rm.room_capacity):
                        single_fully_occupied += 1

                # room_type---->2 it is Double or Bi-Seater with Attached Bath
                if rm.room_type.id==2:
                    double_rooms += 1
                    if int(rm.allocated_number)==0:
                        double_vacant += 1
                    if int(rm.allocated_number)==1:
                        # _logger.info('Room---> %s and allocated_number---> %s', rm.name, rm.allocated_number)
                        double_partial_occupied += 1
                    if int(rm.allocated_number)==int(rm.room_capacity):
                        double_fully_occupied += 1

                # room_type---->3 it is Double or Bi-Seater with Community Bath
                if rm.room_type.id==3:
                    double_rooms2 += 1
                    if int(rm.allocated_number)==0:
                        double_vacant2 += 1
                    if int(rm.allocated_number)==1:
                        # _logger.info('Room---> %s and allocated_number---> %s', rm.name, rm.allocated_number)
                        double_partial_occupied2 += 1
                    if int(rm.allocated_number)==int(rm.room_capacity):
                        double_fully_occupied2 += 1

                # room_type---->4 it is Triple Bed or Tri-Seater with Community Bath
                if rm.room_type.id==4:
                    triple_rooms += 1
                    if int(rm.allocated_number)==0:
                        triple_vacant += 1
                    if int(rm.allocated_number) in (1, 2):
                        triple_partial_occupied += 1
                    if int(rm.allocated_number)==int(rm.room_capacity):
                        triple_fully_occupied += 1

            dt.hostel_capacity = capacity
            dt.total_students = allocated
            dt.vacancy = total_vacancy
            dt.allocated_number = allocated

            dt.total_single_rooms = single_rooms
            dt.total_double_rooms = double_rooms
            dt.total_double_rooms2 = double_rooms2
            dt.total_triple_rooms = triple_rooms

            dt.single_bed_vacant = single_vacant
            dt.double_bed_vacant = double_vacant
            dt.double_bed_vacant2 = double_vacant2
            dt.triple_bed_vacant = triple_vacant
            dt.total_vacant = single_vacant + double_vacant + double_vacant2 + triple_vacant

            dt.full_occupied_single_bed = single_fully_occupied
            dt.full_occupied_double_bed = double_fully_occupied
            dt.full_occupied_double_bed2 = double_fully_occupied2
            dt.full_occupied_triple_bed = triple_fully_occupied
            dt.fully_occupied_total = single_fully_occupied + double_fully_occupied + double_fully_occupied2 + triple_fully_occupied

            dt.double_partial_occupied_bed = double_partial_occupied
            dt.double_partial_occupied_bed2 = double_partial_occupied2
            dt.triple_partial_occupied_bed = triple_partial_occupied
            dt.partially_occupied_total = double_partial_occupied + double_partial_occupied2 + triple_partial_occupied

    def unlink(self):
        return super(OdooCMSHostel, self).unlink()

    @api.model
    def create(self, values):
        """overriding  the create method to show the validation error """
        res = super(OdooCMSHostel, self).create(values)
        return res

    @api.depends('hostel_warden')
    def get_warden_data(self):
        for rec in self:
            if rec.hostel_warden:
                rec.warden_email = rec.hostel_warden.email and rec.hostel_warden.email or ''
                rec.warden_mobile = rec.hostel_warden.mobile and rec.hostel_warden.mobile or ''

    def hostel_student_view(self):
        """shows the students in the hostel"""
        self.ensure_one()
        domain = [
            ('hostel_id', '=', self.id),
            ('hostel_state', '=', 'Allocated'),
            ('vacated_date', '=', False)]
        return {
            'name': _('Students'),
            'domain': domain,
            'res_model': 'odoocms.student',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'context': "{'default_room': '%s'}" % self.id
        }

    def partially_occupied_double_bed_view(self):
        """shows the Partially Occupied Rooms in the hostel"""
        self.ensure_one()
        domain = [
            ('hostel_id', '=', self.id),
            ('room_type', '=', 2),
            ('allocated_number', '=', '1')
        ]
        return {
            'name': _('Rooms'),
            'domain': domain,
            'res_model': 'odoocms.hostel.room',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
        }

    def partially_occupied_double_bed_view2(self):
        """shows the Partially Occupied Rooms in the hostel"""
        self.ensure_one()
        domain = [
            ('hostel_id', '=', self.id),
            ('room_type', '=', 3),
            ('allocated_number', '=', '1')
        ]
        return {
            'name': _('Rooms'),
            'domain': domain,
            'res_model': 'odoocms.hostel.room',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
        }

    def partially_occupied_triple_bed_view(self):
        """shows the Partially Occupied Rooms in the hostel"""
        self.ensure_one()
        domain = [
            ('hostel_id', '=', self.id),
            ('room_type', '=', 4),
            ('allocated_number', 'in', ('1', '2'))
        ]
        return {
            'name': _('Rooms'),
            'domain': domain,
            'res_model': 'odoocms.hostel.room',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
        }

    def fully_occupied_single_bed_view(self):
        """shows the Fully Occupied Rooms in the hostel"""
        self.ensure_one()
        domain = [
            ('hostel_id', '=', self.id),
            ('room_type', '=', 1),
            ('allocated_number', '=', '1')
        ]
        return {
            'name': _('Rooms'),
            'domain': domain,
            'res_model': 'odoocms.hostel.room',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
        }

    def fully_occupied_double_bed_view(self):
        """shows the Fully Occupied Rooms in the hostel"""
        self.ensure_one()
        domain = [
            ('hostel_id', '=', self.id),
            ('room_type', '=', 2),
            ('allocated_number', '=', '2')
        ]
        return {
            'name': _('Rooms'),
            'domain': domain,
            'res_model': 'odoocms.hostel.room',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
        }

    def fully_occupied_double_bed_view2(self):
        """shows the Fully Occupied Rooms in the hostel"""
        self.ensure_one()
        domain = [
            ('hostel_id', '=', self.id),
            ('room_type', '=', 3),
            ('allocated_number', '=', '2')
        ]
        return {
            'name': _('Rooms'),
            'domain': domain,
            'res_model': 'odoocms.hostel.room',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
        }

    def fully_occupied_triple_bed_view(self):
        """shows the Fully Occupied Rooms in the hostel"""
        self.ensure_one()
        domain = [
            ('hostel_id', '=', self.id),
            ('room_type', '=', 4),
            ('allocated_number', '=', '3')
        ]
        return {
            'name': _('Rooms'),
            'domain': domain,
            'res_model': 'odoocms.hostel.room',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
        }

    def single_bed_vacant_view(self):
        """shows the Fully Occupied Rooms in the hostel"""
        self.ensure_one()
        domain = [
            ('hostel_id', '=', self.id),
            ('room_type', '=', 1),
            ('allocated_number', '=', '0')
        ]
        return {
            'name': _('Rooms'),
            'domain': domain,
            'res_model': 'odoocms.hostel.room',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
        }

    def double_bed_vacant_view(self):
        """shows the Fully Occupied Rooms in the hostel"""
        self.ensure_one()
        domain = [
            ('hostel_id', '=', self.id),
            ('room_type', '=', 2),
            ('allocated_number', '=', '0')
        ]
        return {
            'name': _('Rooms'),
            'domain': domain,
            'res_model': 'odoocms.hostel.room',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
        }

    def double_bed_vacant_view2(self):
        """shows the Fully Occupied Rooms in the hostel"""
        self.ensure_one()
        domain = [
            ('hostel_id', '=', self.id),
            ('room_type', '=', 3),
            ('allocated_number', '=', '0')
        ]
        return {
            'name': _('Rooms'),
            'domain': domain,
            'res_model': 'odoocms.hostel.room',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
        }

    def triple_bed_vacant_view(self):
        """shows the Fully Occupied Rooms in the hostel"""
        self.ensure_one()
        domain = [
            ('hostel_id', '=', self.id),
            ('room_type', '=', 4),
            ('allocated_number', '=', '0')
        ]
        return {
            'name': _('Rooms'),
            'domain': domain,
            'res_model': 'odoocms.hostel.room',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
        }

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'
