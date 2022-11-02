# -*- coding: utf-8 -*-
import pdb
from odoo import api, fields, models, _
from datetime import date
from odoo.exceptions import UserError, ValidationError


class OdooCMSChangeStudentState(models.TransientModel):
    _name = 'odoocms.student.state.change'
    _description = 'Change Student State'

    state2 = fields.Selection([
        ('draft', 'Draft'), ('enroll', 'Admitted'), ('alumni', 'Alumni'), ('suspend', 'Suspend'),
        ('struck', 'Struck Off'),
        ('defer', 'Deferred'), ('withdrawn', 'WithDrawn'), ('cancel', 'Cancel'),
    ], 'Status - Temp', default='draft', tracking=True, required=True)

    def change_student_state(self):
        student_ids = self._context.get('active_ids')
        print(12121212121212121, self._context)
        print(11111111111111111, student_ids)
        student_rec = self.env['odoocms.student'].search([('id', 'in', student_ids)])
        print(2222222222222222222222222, student_rec)
        for student in student_rec:
            student.state2 = self.state2
            if self.state2 == 'block' and self.block_reason:
                student.block_reason = self.block_reason
        return {'type': 'ir.actions.act_window_close'}