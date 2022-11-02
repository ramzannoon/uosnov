
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime,date
import pdb

import logging
_logger = logging.getLogger(__name__)


class OdooCMSExamDisposalType(models.Model):
    _name = 'odoocms.exam.disposal.type'
    _description = 'Exam Disposal Types'
    _order = 'sequence'

    name = fields.Char(string='Disposal Type')
    description = fields.Char(string='Description')
    sequence = fields.Integer(string='Sequence')
    tag_id = fields.Many2one('odoocms.student.tag','Tag')


class OdooCMSExamDisposalRules(models.Model):
    _name = 'odoocms.exam.disposal.rule'
    _description = 'Exam Disposal Rules'
    _rec_name = 'disposal_type_id'
    _order = 'sequence'

    batch_ids = fields.Many2many('odoocms.batch', 'odoocms_batch_rule_rel', 'disposal_rule_id', 'batch_id', string = 'Batches')
    disposal_type_id = fields.Many2one('odoocms.exam.disposal.type', string='Disposal Type')
    line_ids = fields.One2many('exam.disposal.rule.line', 'disposal_rule_id', string='Rule Lines', copy=True)
    sequence = fields.Integer(string='Sequence')


class ExamDisposalRulesLines(models.Model):
    _name = 'exam.disposal.rule.line'
    _description = 'Exam Disposal Rule Lines'
    _order = 'sequence'

    type = fields.Selection([('code','Python Code'), ('domain', 'Domain')], string='Type')
    domain = fields.Char(string='Conditions')
    code = fields.Text(string='Python Code')
    operator = fields.Selection([('=', '='), ('<', '<'), ('>', '>'), ('!=', '!='), ('<=', '<='), ('>=', '>=')], string='Operator')
    count = fields.Integer(string='Count')
    limit = fields.Integer(string='Limit')
    disposal_rule_id = fields.Many2one('odoocms.exam.disposal.rule', string='Disposal Rule')
    sequence = fields.Integer(string='Sequence')


class OdooCMSBatch(models.Model):
    _inherit = 'odoocms.batch'

    disposal_rule_ids = fields.Many2many('odoocms.exam.disposal.rule', 'odoocms_batch_rule_rel', 'batch_id', 'disposal_rule_id', string='Disposal Rules')
    
    
class OdooCMSExamDisposalHistory(models.Model):
    _name = 'odoocms.exam.disposal.history'
    _description = 'Exam Disposal History'

    name = fields.Char('Name',help='History Number etc...', default=lambda self:self.env['ir.sequence'].next_by_code('odoocms.exam.disposal.history'), copy=False, readonly=True)
    batch_id = fields.Many2one('odoocms.batch', string = 'Batch')
    term_id = fields.Many2one('odoocms.academic.term', string='Term')
    user_id = fields.Many2one('res.users', string='User')
    date = fields.Datetime(string='Date', default=datetime.now())
    line_ids = fields.One2many('odoocms.exam.disposal.history.line', 'history_id', string='History Lines')
    
    
class OdooCMSExamDisposalHistoryLine(models.Model):
    _name = 'odoocms.exam.disposal.history.line'
    _description = 'Exam Disposal History Line'

    history_id = fields.Many2one('odoocms.exam.disposal.history', string='History')
    student_id = fields.Many2one('odoocms.student', string='Student')
    pre_disposal_type_id = fields.Many2one('odoocms.exam.disposal.type', string='Pre Disposal')
    disposal_type_id = fields.Many2one('odoocms.exam.disposal.type', string='Disposal')
