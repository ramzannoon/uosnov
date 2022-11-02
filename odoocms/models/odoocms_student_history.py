import pdb

from odoo import models, fields, api, _
import logging

from datetime import datetime, date
from odoo.http import request
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class OdooCMSStudentHistory(models.Model):
    _name = 'odoocms.student.history'
    _description = 'Student History'
    _order = 'student_id'
    _rec_name = 'student_id'

    student_id = fields.Many2one('odoocms.student', 'Student', required=True)
    field_name_id = fields.Many2one('ir.model.fields', 'Change In Attribute')
    field_name = fields.Char('Change In')
    changed_from = fields.Text('Changed From')
    changed_to = fields.Text('Changed To')
    changed_by = fields.Many2one('res.users', 'Changed By')
    date = fields.Datetime('Changed At')
    method = fields.Char('By Method')
    date_effective = fields.Date('Date Effective')
    description = fields.Text('Description')
    

class OdooCMSStudent(models.Model):
    _inherit = 'odoocms.student'

    def write(self, vals):
        if vals.get('first_name', False) or vals.get('last_name', False):
            vals['name'] = vals.get('first_name', self.first_name or '') + ' ' + vals.get('last_name', self.last_name or '')
        if vals.get('state'):
            field_name_id = self.env['ir.model.fields'].search([('model','=',self._name),('name','=','state')])
            history_data = {
                'student_id': self.id,
                'field_name_id': field_name_id and field_name_id.id or False,
                'field_name': 'State',
                'changed_from': self.state,
                'changed_to': vals.get('state'),
                'changed_by': request.env.user.id,
                'date': datetime.now(),
                'date_effective': self._context.get('date_effective',False),
                'description': self._context.get('description',False),
                'method': self._context.get('method',False),
                
            }
            self.env['odoocms.student.history'].create(history_data)

        if vals.get('tag_ids'):
            to_be_removed = self.env['odoocms.student.tag']
            updated_tags  = self.env['odoocms.student.tag'].search([('id','in',vals.get('tag_ids')[0][2])])
            added_tags =  updated_tags - self.tag_ids
            for added_tag in added_tags:
                if added_tag.category_id and not added_tag.category_id.multiple:
                    if len(added_tags.filtered(lambda l: l.category_id == added_tag.category_id)) == 1:
                        to_be_removed += (updated_tags - added_tags).filtered(lambda l: l.category_id == added_tag.category_id)
                    else:
                        raise UserError('The following tags can not be used simultaneously %s' % (', '.join([k.name for k in added_tags.filtered(lambda l: l.category_id == added_tag.category_id)])))
            updated_tags -= to_be_removed
            vals.get('tag_ids')[0][2] = updated_tags.ids

        method = 'Manual'
        if vals.get('tag_apply_method'):
            method = vals.get('tag_apply_method')
            vals.pop('tag_apply_method')
        old_tags = self.tag_ids.mapped('name')
        res = super(OdooCMSStudent, self).write(vals)
        
        new_tags = self.tag_ids.mapped('name')
        if vals.get('tag_ids'):  # old_tags != new_tags
            history_data = {
                'student_id': self.id,
                'field_name': 'Tags',
                'changed_from': old_tags,
                'changed_to': new_tags,
                'changed_by': request.env.user.id,
                'date': datetime.now(),
                'method': method,
            }
            self.env['odoocms.student.history'].create(history_data)

        return res



