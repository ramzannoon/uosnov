# -*- coding: utf-8 -*-
import pdb
from odoo import api, fields, models,_



class OdooCMSConfirmClassesWizard(models.TransientModel):
	_name = 'odoocms.confirm.classes.wiz'
	_description = 'Confirm Classes Wizard'
				
	@api.model
	def _get_classes(self):
		if self.env.context.get('active_model', False) == 'odoocms.class' and self.env.context.get('active_ids', False):
			return self.env.context['active_ids']
			
	class_ids = fields.Many2many('odoocms.class', string='Classes', default=_get_classes,
		help="""Only selected Classes will be Confirmed.""")   #,
	
	def confirm_classes(self):
		for cls in self.class_ids:
			cls.convert_to_current()
		return {'type': 'ir.actions.act_window_close'}



