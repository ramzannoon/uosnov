# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import pdb


class OdooCMSHostelAmenities(models.Model):
    _name = 'odoocms.hostel.amenities'
    _description = 'Amenities in Institution'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True, help='Name of amenity', tracking=True)
    code = fields.Char(string='Code', help='Code of amenity', tracking=True)
    sequence = fields.Integer()
    state = fields.Selection([('draft', 'Draft'), ('lock', 'Locked')], string='Status', default='draft', tracking=True)
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [('unique_code', 'unique(name)', "Another Amenity already exists with this Name!"), ]

    @api.model
    def create(self, values):
        if values.get('name', False):
            already_exit = self.env['odoocms.hostel.amenities'].search([('name', '=', values['name'])])
            if already_exit:
                raise UserError('Duplicate Name Are Not Allow, Please Change The Name.')
        res = super(OdooCMSHostelAmenities, self).create(values)
        return res

    def write(self, values):
        if values.get('name', False):
            already_exit = self.env['odoocms.hostel.amenities'].search([('name', '=', values['name'])])
            if already_exit:
                raise UserError('Duplicate Name Are Not Allow, Please Change The Name.')
        res = super(OdooCMSHostelAmenities, self).write(values)
        return res

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'


class OdooCMSHostelRoomType(models.Model):
    _name = 'odoocms.hostel.room.type'
    _description = "Room Types"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True, tracking=True)
    code = fields.Char(string="Code", tracking=True)
    sequence = fields.Integer("Sequence")
    capacity = fields.Integer('Capacity', required=True, default=0, tracking=True)
    per_month_rent = fields.Float('Per Month Rent', tracking=True, default=0)
    currency_id = fields.Many2one('res.currency', string='Int. Currency', default=2)
    per_month_rent_int = fields.Monetary('Per Month Rent Int.', tracking=True, default=0)
    state = fields.Selection([('draft', 'Draft'), ('lock', 'Locked')], string='Status', default='draft', tracking=True)
    active = fields.Boolean('Active', default=True, tracking=True)

    @api.model
    def create(self, values):
        if values.get('name', False):
            already_exit = self.env['odoocms.hostel.room.type'].search([('name', '=', values['name'])])
            if already_exit:
                raise UserError('Duplicate Name Are Not Allow, Please Change The Name.')
        res = super(OdooCMSHostelRoomType, self).create(values)
        return res

    def write(self, values):
        if values.get('name', False):
            already_exit = self.env['odoocms.hostel.room.type'].search([('name', '=', values['name'])])
            if already_exit:
                raise UserError('Duplicate Name Are Not Allow, Please Change The Name.')
        res = super(OdooCMSHostelRoomType, self).write(values)
        return res

    @api.constrains('per_month_rent')
    def rent_amount_constrains(self):
        for rec in self:
            if rec.per_month_rent <= 0:
                raise ValidationError(_('Rent Amount Should be Greater Then Zero.'))

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'


class OdooCMSRooms(models.Model):
    _name = 'odoocms.rooms'
    _description = "Rooms Management"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence = fields.Char('Sequence')
    name = fields.Char('Name', required=True)
    room_no = fields.Char(string="No.", required=True)
    active = fields.Boolean('Active', default=True)
    hostel_room_ids = fields.One2many('odoocms.hostel.room', 'room_id', 'Hostel Rooms')
    state = fields.Selection([('draft', 'Draft'), ('lock', 'Locked')], string='Status', default='draft', tracking=True)
    prefix = fields.Char('Prefix')

    _sql_constraints = [('name_uniq', 'unique (name)', "Room Name already exists !"), ]

    @api.model
    def create(self, values):
        if values.get('name', False):
            already_exit = self.env['odoocms.rooms'].search([('name', '=', values['name'])])
            if already_exit:
                raise UserError('Duplicate Name Are Not Allow, Please Change The Name of the Room.')
        res = super(OdooCMSRooms, self).create(values)
        return res

    def write(self, values):
        if values.get('name', False):
            already_exit = self.env['odoocms.rooms'].search([('name', '=', values['name'])])
            if already_exit:
                raise UserError('Duplicate Name Are Not Allow, Please Change The Name of the Room.')
        res = super(OdooCMSRooms, self).write(values)
        return res

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'


class OdooCMSHostelRoom(models.Model):
    _name = 'odoocms.hostel.room'
    _description = "Room"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", tracking=True, compute='compute_room_data', store=True)
    code = fields.Char(string="No.", tracking=True, compute='compute_room_data', store=True)
    sequence = fields.Integer('Sequence')
    hostel_type_id = fields.Many2one('odoocms.hostel.type', 'Hostel Type', tracking=True, index=True, ondelete='restrict')
    hostel_id = fields.Many2one('odoocms.hostel', required=True, string="Hostel", tracking=True, index=True, ondelete='restrict')
    floor_no = fields.Many2one('odoocms.hostel.floor', required=True, string="Floor No.", tracking=True, index=True, ondelete='restrict')
    room_id = fields.Many2one('odoocms.rooms', 'Room', tracking=True, index=True, ondelete='restrict')
    room_type = fields.Many2one('odoocms.hostel.room.type', 'Type', tracking=True, index=True, ondelete='restrict')
    room_capacity = fields.Char(string="Capacity", tracking=True, compute='_compute_hostel_room_capacity', store=True)
    responsible = fields.Many2one('odoocms.hostel.warden', string="Responsible Staff", tracking=True, index=True, ondelete='restrict')
    allocated_number = fields.Char(string="Allocated Students", compute='get_total_allocated', store=True)
    vacancy = fields.Char(string="Vacancy", compute='get_total_allocated', store=True)
    company_id = fields.Many2one('res.company', string='Company', default=1, tracking=True, index=True, ondelete='restrict')
    state = fields.Selection([('Vacant', 'Vacant'), ('Occupied', 'Occupied')], default='Vacant', string='Status', tracking=True, index=True)
    special = fields.Boolean('Special', default=False, tracking=True)
    active = fields.Boolean('Active', default=True)
    allocate_date = fields.Date('Allocate Date')
    vacant_date = fields.Date('Vacant Date')
    room_blocked = fields.Boolean('Blocked', default=False, tracking=True)
    blockage_reason_id = fields.Many2one('odoocms.hostel.room.blockage.reason', 'Blockage Reason', tracking=True)
    student_ids = fields.One2many('odoocms.student', 'room_id', string="Students")
    faculty_ids = fields.One2many('odoocms.faculty.staff', 'room_id', string="Students")
    amenity_ids = fields.One2many('odoocms.room.amenity', 'room_id', tracking=True)
    per_month_rent = fields.Float('Per Month Rent', tracking=True, compute="_compute_room_month_rent", default=0, store=True)
    currency_id = fields.Many2one('res.currency', string='Int. Currency', compute="_compute_room_month_rent", default=2, store=True)
    per_month_rent_int = fields.Monetary('Per Month Rent Int.', tracking=True, compute="_compute_room_month_rent", default=0, store=True)

    @api.onchange('hostel_id', 'floor_no')
    def get_rooms(self):
        """adding domain for floors"""
        hostel = None
        if self.hostel_id:
            hostel = self.hostel_id.id
        return {
            'domain': {
                'floor_no': [('hostel_id', '=', hostel)]
            }
        }

    @api.depends('room_id')
    def compute_room_data(self):
        for rec in self:
            if rec.hostel_id and rec.room_id:
                hostel_code = rec.hostel_id.code and rec.hostel_id.code or ""
                room_no = rec.room_id.room_no and rec.room_id.room_no or ""
                rec.name = "H" + hostel_code + "-" + "Room" + room_no
                rec.code = rec.room_id.room_no and rec.room_id.room_no or ''
                rec.room_capacity = rec.room_type and str(rec.room_type.capacity) or '0'

    @api.depends('student_ids', 'hostel_id', 'floor_no', 'room_capacity')
    def get_total_allocated(self):
        """counting the allocated and vacancy for room"""
        for std in self:
            std_count = self.env['odoocms.student'].search_count([('room_id', '=', std.id), ('state', '!=', 'vacated'), ('vacated_date', '=', False)])
            # if std_count > int(std.room_capacity):
            #     raise ValidationError(_('Room Capacity is Over'))
            std.allocated_number = std_count
            std.vacancy = int(std.room_capacity) - std_count

    @api.model
    def create(self, values):
        res = super(OdooCMSHostelRoom, self).create(values)
        return res

    def write(self, values):
        if values.get('student_ids', False):
            hostel_type = self.hostel_id.hostel_type.type
            if hostel_type=='Boys':
                girls_recs = self.student_ids.filtered(lambda l: l.gender=='f')
                if girls_recs:
                    raise UserError(_('Girls Cannot be allocated Boys Hostel, please check that.'))
            if hostel_type=='Girls':
                boys_recs = self.student_ids.filtered(lambda l: l.gender=='m')
                if boys_recs:
                    raise UserError(_('Boys Cannot be allocated Girls Hostel, Please check that.'))
        res = super(OdooCMSHostelRoom, self).write(values)

    def unlink(self):
        return super(OdooCMSHostelRoom, self).unlink()

    def student_view(self):
        """get the students allocated in the room"""
        self.ensure_one()
        domain = [
            ('room', '=', self.id),
            ('state', '=', 'allocated'),
            ('vacated_date', '=', False)]
        return {
            'name': _('Students'),
            'domain': domain,
            'res_model': 'odoocms.student',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'context': "{'default_room': '%s'}" % self.id
        }

    @api.depends('room_type', 'room_type.per_month_rent',
        'room_type.per_month_rent_int', 'room_type.currency_id')
    def _compute_room_month_rent(self):
        for rec in self:
            per_month_rent = 0
            per_month_rent_int = 0
            currency_id = 165
            if rec.room_type:
                per_month_rent = rec.room_type.per_month_rent
                per_month_rent_int = rec.room_type.per_month_rent_int
                currency_id = rec.room_type.currency_id.id
            rec.per_month_rent = per_month_rent
            rec.per_month_rent_int = per_month_rent_int
            rec.currency_id = currency_id

    @api.depends('room_type', 'room_type.capacity')
    def _compute_hostel_room_capacity(self):
        for rec in self:
            rec.room_capacity = rec.room_type.capacity


class OdooCMSRoomAmenity(models.Model):
    _name = 'odoocms.room.amenity'
    _description = "Room Amenity"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    amenity_id = fields.Many2one('odoocms.hostel.amenities', string="Amenity", required=True, tracking=True, index=True, ondelete='restrict')
    qty = fields.Integer(string="Quantity", default=1, tracking=True)
    room_id = fields.Many2one('odoocms.hostel.room', 'Room No', tracking=True, index=True, ondelete='restrict')
    active = fields.Boolean('Active', default=True, tracking=True)
    state = fields.Selection([('draft', 'Draft'), ('lock', 'Locked')], string='Status', default='draft', tracking=True)

    @api.constrains('qty')
    def check_qty(self):
        for rec in self:
            if rec.qty <= 0:
                raise ValidationError(_('Quantity must be positive'))

    @api.model
    def create(self, values):
        if values.get('amenity_id', False) and values.get('room_id', False):
            already_exit = self.env['odoocms.room.amenity'].search([('amenity_id', '=', values['amenity_id']), ('room_id', '=', values['room_id'])])
            if already_exit:
                raise UserError('Duplicate Name Are Not Allow, Please Change The Name.')
        res = super(OdooCMSRoomAmenity, self).create(values)
        return res

    def write(self, values):
        if values.get('amenity_id', False) and self.room_id:
            already_exit = self.env['odoocms.room.amenity'].search(
                [('amenity_id', '=', values['amenity_id']), ('room_id', '=', self.room_id.id)])
            if already_exit:
                raise UserError('Duplicate Name Are Not Allow, Please Change The Name.')
        if values.get('room_id', False) and self.amenity_id:
            already_exit = self.env['odoocms.room.amenity'].search(
                [('room_id', '=', values['room_id']), ('amenity_id', '=', self.amenity_id.id)])
            if already_exit:
                raise UserError('Duplicate Name Are Not Allow, Please Change The Name.')
        res = super(OdooCMSRoomAmenity, self).write(values)
        return res

    def action_lock(self):
        self.state = 'lock'

    def action_unlock(self):
        self.state = 'draft'
