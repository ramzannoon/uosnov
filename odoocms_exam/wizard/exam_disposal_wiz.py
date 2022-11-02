import pdb
from odoo import api, fields, models, _
from datetime import date , datetime

class OdooCMSExamDisposalWiz(models.TransientModel):
    _name = 'odoocms.exam.disposal.wiz'
    _description = 'Exam Disposal Wizard'

    @api.model
    def _get_batches(self):
        if self.env.context.get('active_model', False) == 'odoocms.batch.term' and self.env.context.get('active_ids', False):
            return self.env.context['active_ids']

    apply_on = fields.Selection([('batch','Batch'),('student','Students')],string='Apply on',default='student',)
    term_id = fields.Many2one('odoocms.academic.term', 'Academic Term')
    
    batch_term_ids = fields.Many2many('odoocms.batch.term', string = 'Batches/Intakes', default = _get_batches)
    student_term_ids = fields.Many2many('odoocms.student.term',string='Students')
    
    def apply_disposal_rules(self):
        hist_list = []
        if self.apply_on == 'batch':
            for batch_term in self.batch_term_ids:
                hist_list += batch_term._apply_disposal_rules()
        elif self.apply_on == 'student':
            history_ids = self.env['odoocms.exam.disposal.history']
            values = {
                # 'batch_id': self.batch_id.id,  # [(6, 0, self.batch_ids.mapped('id'))],
                # 'batch_term_id': self.id,
                'user_id': self.env.user.id,
                'date': datetime.now(),
                'term_id': self.term_id.id,
            }
            disposal_history_id = self.env['odoocms.exam.disposal.history'].create(values)
            history_ids += disposal_history_id

            students = self.student_term_ids.mapped('student_id')
            for student in students:
                student_enrolled = self.env['odoocms.student.course'].sudo().search([('term_id', '=', self.term_id.id)])
                if student_enrolled:
                    student.apply_disposals(disposal_history_id)

            hist_list = history_ids.mapped('id')
            
            
        return {
            'domain': [('id', 'in', hist_list)],
            'name': _('Disposals'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'odoocms.exam.disposal.history',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }
   