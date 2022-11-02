import pdb
from odoo import api, fields, models, _


class OdooCMSApproveDBSWiz(models.TransientModel):
    _name = 'odoocms.approve.dbs.wiz'
    _description = 'Approve DBS Wizard'

    @api.model
    def _get_dbs(self):
        dbs_id = self.env['odoocms.dbs'].browse(self._context.get('active_id', False))
        if dbs_id:
            return dbs_id.id

    dbs_id = fields.Many2one('odoocms.dbs','DBS',default=_get_dbs)

    def approve_dbs(self):
        self.ensure_one()
        for grade_class in self.dbs_id.grade_class_ids:
            if grade_class.dbs_action == 'new':
                grade_class.dbs_approve()

        return {'type': 'ir.actions.act_window_close'}


