import pdb
from odoo import api, fields, models, _
from odoo.http import request
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
from datetime import date , datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import pdb
from odoo.tools.safe_eval import safe_eval
from odoo.osv import expression


class OdooCMSExamDisposalWiz(models.TransientModel):
    _name = 'odoocms.exam.fbs.wiz'
    _description = 'Submit for FBS Wizard'

    @api.model
    def _get_batches(self):
        if self.env.context.get('active_model', False) == 'odoocms.batch' and self.env.context.get('active_ids', False):
            return self.env.context['active_ids']

    batch_ids = fields.Many2many('odoocms.batch', string = 'Batches/Intakes', default = _get_batches)

    
    def submit_fbs(self):
        for batch in self.batch_ids:
            disposal_history_id = self.env['odoocms.exam.disposal.history'].search(
                [('batch_id','=',batch.id),('term_id','=',batch.term_id.id)]
            )
            if not disposal_history_id:
                raise UserError('Please apply Disposals First')

            for section in batch.section_ids:
                for primary_class in section.primary_class_ids.filtered(lambda l: l.term_id == batch.term_id):
                    grade_class = primary_class.grade_class_id
              
                    if grade_class.fbs_id and grade_class.fbs_id.state == 'done':
                        activity = self.env.ref('odoocms_academic.mail_act_result_hod_to_dean')
                        grade_class.activity_schedule('odoocms_academic.mail_act_result_hod_to_dean', user_id=activity._get_role_users(grade_class.program_id))
                    else:
                        institute_id = batch.department_id.institute_id
                        fbs_id = self.env['odoocms.fbs'].search([
                            ('institute_id', '=', institute_id.id),
                            ('career_id', '=', batch.career_id.id),
                            ('term_id', '=', batch.term_id.id),
                            ('state', '=' , 'new')
                        ])
                        if not fbs_id:
                            data = {
                                'institute_id': institute_id.id,
                                'career_id': batch.career_id.id,
                                'term_id': batch.term_id.id
                            }
                            fbs_id = self.env['odoocms.fbs'].create(data)
                        fbs_id.assign_fbs()
                        grade_class.fbs_action = 'new'
                
                    grade_class.state = 'approval'
                    grade_class.primary_class_ids.state = 'approval'
                    grade_class.primary_class_ids.mapped('class_ids').state = 'approval'






