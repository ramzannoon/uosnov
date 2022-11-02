import pdb
from odoo import api, fields, models, _


class OdooCMSExamDisposalWiz(models.TransientModel):
    _name = 'odoocms.exam.disposal.wiz'
    _description = 'Exam Disposal Wizard'

    @api.model
    def _get_batches(self):
        if self.env.context.get('active_model', False) == 'odoocms.batch.term' and self.env.context.get('active_ids', False):
            return self.env.context['active_ids']

    batch_term_ids = fields.Many2many('odoocms.batch.term', string = 'Batches/Intakes', default = _get_batches)

    def apply_disposal_rules(self):
        hist_list = []
        for batch_term in self.batch_term_ids:
            hist_list += batch_term._apply_disposal_rules()
            
        return {
            'domain': [('id', 'in', hist_list)],
            'name': _('Disposals'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'odoocms.exam.disposal.history',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }
   