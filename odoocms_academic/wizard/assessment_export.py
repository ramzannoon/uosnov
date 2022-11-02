import pdb
from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

try:
	import base64
except ImportError:
	_logger.debug('Cannot `import base64`.')
	

class AssessmentsExport(models.TransientModel):
	_name = 'odoocms.activities.export.wizard'
	_description = 'Assessment Export Wizard'

	@api.model
	def _get_class(self):
		class_id = self.env['odoocms.class'].browse(self._context.get('active_id', False))
		if class_id:
			return class_id.id

	@api.model
	def _get_is_group_class(self):
		class_id = self.env['odoocms.class'].browse(self._context.get('active_id', False))
		if class_id and len(class_id.primary_class_id.grade_class_id.primary_class_ids) > 1:
			return True
		else:
			return False

	class_id = fields.Many2one('odoocms.class', string='Class', default=_get_class)
	group_class = fields.Boolean('Group Class', default=_get_is_group_class)

	def make_excel(self):
		class_id = self.env['odoocms.class'].search([('id', '=', self.env.context['active_id'])])
		file_data = class_id.assessment_sheet_excel()
		
		wiz_id = self.env['assessment.report.save.wizard'].create({
			'data': base64.encodestring(file_data.getvalue()),
			'name': class_id.code + '_Assessment.xls'
		})

		return {
			'type': 'ir.actions.act_window',
			'name': 'Assessment Sheet',
			'res_model': 'assessment.report.save.wizard',
			'view_mode': 'form',
			'view_type': 'form',
			'res_id': wiz_id.id,
			'target': 'new'
		}

	
class assessment_report_save_wizard(models.TransientModel):
	_name = "assessment.report.save.wizard"
	_description = 'Assessment Report Wizard'
	
	name = fields.Char('filename', readonly=True)
	data = fields.Binary('file', readonly=True)


		








