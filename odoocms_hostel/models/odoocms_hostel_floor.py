# -*- coding: utf-8 -*-
from odoo import fields, models, _, api
from odoo.exceptions import ValidationError, UserError
import pdb


class OdooCMSHostelFloors(models.Model):
    _name = 'odoocms.hostel.floor'
    _description = "Hostel Floors Management"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', compute="compute_floor_name", store=True, tracking=True)
    code = fields.Char('Code', compute='compute_floor_code', store=True)
    sequence = fields.Char('Sequence')
    floor_no = fields.Char(string="Floor No.", compute="compute_floor_name", store=True, tracking=True)
    hostel_id = fields.Many2one('odoocms.hostel', required=True, string="Hostel", tracking=True, index=True, ondelete='restrict')
    responsible = fields.Many2one('odoocms.hostel.warden', string="Responsible Staff", tracking=True, index=True, ondelete='restrict')
    active = fields.Boolean('Active', default=True)
    floor_id = fields.Many2one('odoocms.floors', 'Floor', tracking=True, index=True, ondelete='restrict')
    company_id = fields.Many2one('res.company', string='Company', default=1, index=True, tracking=True, ondelete='restrict')
    state = fields.Selection([('draft', 'Draft'), ('lock', 'Locked')], string='Status', default='draft', tracking=True)

    _sql_constraints = [('name_uniq', 'unique(hostel_id,floor_id)', "Hostel and Floor Should be Unique!"), ]

    def name_get(self):
        res = []
        for record in self:
            name = record.hostel_id and record.hostel_id.name or ''
            if record.name:
                name = name + ' - ' + record.name
            res.append((record.id, name))
        return res

    @api.model
    def create(self, values):
        if values.get('hostel_id', False) and values.get('floor_id', False):
            already_exit = self.env['odoocms.hostel.floor'].search([('hostel_id', '=', values['hostel_id']), ('floor_id', '=', values['floor_id'])])
            if already_exit:
                raise UserError('Hostel Floors should be Unique. Floor Duplications are not allowed.')

        """check the floor count of hostel"""
        if values.get('hostel_id', False):
            floor = 0.0
            hostel_obj = self.env['odoocms.hostel'].browse(values['hostel_id'])
            floor_count = self.search_count([('hostel_id', '=', values['hostel_id']), ('id', '!=', self.id)])
            if hostel_obj:
                floor += float(hostel_obj.hostel_floors)
                if floor < floor_count:
                    raise ValidationError(_('Floor Count is High'))
        res = super(OdooCMSHostelFloors, self).create(values)
        return res

    def unlink(self):
        return super(OdooCMSHostelFloors, self).unlink()

    def write(self, values):
        already_exit = False
        if values.get('hostel_id', False) and self.floor_id:
            already_exit = self.env['odoocms.hostel.floor'].search([('hostel_id', '=', values['hostel_id']), ('floor_id', '=', self.floor_id.id)])
            if already_exit:
                raise UserError('Hostel Floors should be Unique. Floor Duplicates are not allowed.')
        if values.get('floor_id', False) and self.hostel_id:
            already_exit = self.env['odoocms.hostel.floor'].search([('floor_id', '=', values['floor_id']), ('hostel_id', '=', self.hostel_id.id)])
            if already_exit:
                raise UserError('Hostel Floors should be Unique. Floor Duplicates are not allowed.')
        res = super(OdooCMSHostelFloors, self).write(values)

    @api.depends('hostel_id', 'floor_no')
    def compute_floor_code(self):
        for rec in self:
            rec.code = ''
            code = ''
            if rec.hostel_id:
                code = "H"
                if rec.hostel_id.code:
                    code = code + rec.hostel_id.code
                code = code + "-F"
                if rec.floor_no:
                    code = code + rec.floor_no
                rec.code = code

    @api.depends('floor_id')
    def compute_floor_name(self):
        for rec in self:
            if rec.floor_id and rec.floor_id.name:
                rec.name = rec.floor_id.name
                rec.responsible = rec.hostel_id.hostel_warden and rec.hostel_id.hostel_warden.id
            if rec.floor_id and rec.floor_id.floor_no:
                rec.floor_no = rec.floor_id.floor_no

    def lock_floor(self):
        self.state = 'lock'

    def unlock_floor(self):
        self.state = 'draft'


class OdooCMSFloors(models.Model):
    _name = 'odoocms.floors'
    _description = "Floors Management"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', required=True, tracking=True)
    sequence = fields.Char('Sequence')
    floor_no = fields.Char(string="Floor No.", required=True, tracking=True)
    active = fields.Boolean('Active', default=True)
    hostel_floor_ids = fields.One2many('odoocms.hostel.floor', 'floor_id', 'Hostel Floors')
    state = fields.Selection([('draft', 'Draft'), ('lock', 'Locked')], string='Status', default='draft', tracking=True)

    _sql_constraints = [('name_uniq', 'unique (name)', "Floor Name already exists !"),]

    @api.model
    def create(self, values):
        if values.get('name', False):
            already_exit = self.env['odoocms.floors'].search([('name', '=', values['name'])])
            if already_exit:
                raise UserError('Duplicate Name Are Not Allow, Please Change The Name of the Floor.')
        res = super(OdooCMSFloors, self).create(values)
        return res

    def write(self, values):
        if values.get('name', False):
            already_exit = self.env['odoocms.floors'].search([('name', '=', values['name'])])
            if already_exit:
                raise UserError('Duplicate Name Are Not Allow, Please Change The Name of the Floor.')
        res = super(OdooCMSFloors, self).write(values)
        return res

    def lock_floor(self):
        self.state = 'lock'

    def unlock_floor(self):
        self.state = 'draft'
