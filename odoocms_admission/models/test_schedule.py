from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
import pdb


class OdooCMSEntryTestCenter(models.Model):
    _name = "odoocms.admission.test.center"
    _description = "Admission Test Center"

    name = fields.Char(string='City Name', required=True)
    code = fields.Char(string='City Code', required=True)
    test_type = fields.Selection([('cbt', 'Computer Based Test'), ('pbt', 'Paper Based Test')], default="cbt")
    time_ids = fields.One2many('odoocms.admission.test.time', 'time_id', 'Test Time')
    application_ids = fields.One2many('odoocms.application', 'center_id', 'Applications')
    app_count = fields.Integer('Count', compute='_count_apps', store=True)
    
    #discipline_id = fields.Many2one('odoocms.discipline', required=True)

    @api.depends('application_ids')
    def _count_apps(self):
        for rec in self:
            rec.app_count = len(rec.application_ids)


class OdooCMSEntryTestTime(models.Model):
    _name = "odoocms.admission.test.time"
    _description = "Admission Test Time"
    _rec_name = 'date'

    date = fields.Date('Test Date', required=True)
    time = fields.Float(string='Test Time', required=True)
    active_time = fields.Boolean('Active', default=True)
    capacity = fields.Integer('Capacity')
    time_id = fields.Many2one('odoocms.admission.test.center')
    app_count = fields.Integer('Count', compute='_count_apps', store=True)
    application_ids = fields.One2many('odoocms.application', 'slot_id', 'Applications')
    degree_ids = fields.Many2many('odoocms.degree','test_slot_degree_rel','slot_id','degree_id','Degrees')

    def name_get(self):
        res = []
        for record in self:
            if record.date:
                time = '%02d:%02d' % (divmod(record.time * 60, 60))
                name = str(record.date) + ' ( ' + str(time) + ' )'
                res.append((record.id, name))
        return res

    @api.depends('application_ids')
    def _count_apps(self):
        for rec in self:
            rec.app_count = len(rec.application_ids)
