import pdb
from odoo import api, fields, models, _


class OdooCMSApproveFBSWiz(models.TransientModel):
    _name = 'odoocms.approve.fbs.wiz'
    _description = 'Approve FBS Wizard'

    @api.model
    def _get_fbs(self):
        fbs_id = self.env['odoocms.fbs'].browse(self._context.get('active_id', False))
        if fbs_id:
            return fbs_id.id

    fbs_id = fields.Many2one('odoocms.fbs','FBS',default=_get_fbs)

    def approve_fbs(self):
        self.ensure_one()
        for grade_class in self.fbs_id.grade_class_ids:
            if grade_class.fbs_action == 'new':
                grade_class.fbs_approve()

        return {'type': 'ir.actions.act_window_close'}
