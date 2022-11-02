import pdb
from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from datetime import date



class OdooCMSAssignGradesWiz(models.TransientModel):
    _name = 'odoocms.assign.grades.wiz'
    _description = 'Assign Grades Wizard'

    @api.model
    def _get_class(self):
        grade_class_id = self.env['odoocms.class.grade'].browse(self._context.get('active_id', False))
        if grade_class_id:
            return grade_class_id.id

    @api.model
    def _get_grading(self):
        grade_class_id = self.env['odoocms.class.grade'].browse(self._context.get('active_id', False))
        if grade_class_id:
            return grade_class_id.grade_method_id.id
    
    grade_method_id = fields.Many2one('odoocms.grade.method', string='Grading', default=_get_grading)
    grade_class_id = fields.Many2one('odoocms.class.grade','Grade Class',default=_get_class)
    event = fields.Selection([('mid','Mid'),('final','Final')],string='Event',default='final')
    
    def assign_grades(self):
        self.ensure_one()
        self.grade_class_id.grade_method_id = self.grade_method_id.id
        self.grade_class_id.grade_calculation_date = date.today()

        if hasattr(self.grade_class_id, '%s' % self.grade_method_id.method):
            method = "grade_class_id.%s(event='%s')" % (self.grade_method_id.method,self.event)
            safe_eval(method, {'grade_class_id': self.grade_class_id}, mode='exec', nocopy=True)

        return {'type': 'ir.actions.act_window_close'}



