# -*- coding: utf-8 -*-
import time
import tempfile
import binascii
import xlrd
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime
from odoo.exceptions import Warning
from odoo import models, fields, exceptions, api, _

import logging

_logger = logging.getLogger(__name__)
from io import StringIO
import io
from odoo.exceptions import UserError, ValidationError
import numpy as np
import pdb

# try:
#     import csv
# except ImportError:
#     _logger.debug('Cannot `import csv`.')
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class AssessmentImportWizard(models.TransientModel):
    _name = "odoocms.assessment.import.wizard"
    _description = 'Assessment Import Wizard'
    
    file = fields.Binary('File')
    # import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='Select',default='xls')
    session_id = fields.Many2one('odoocms.academic.session', 'Academic Session')
    batch_id = fields.Many2one('odoocms.batch', 'Intake')
    term_id = fields.Many2one('odoocms.academic.term', 'Term')
    class_id = fields.Many2one('odoocms.class', 'Class')    

    def import_assessment_data(self):
        self.env['odoocms.class'].assessment_import_excell(binascii.a2b_base64(self.file))
        
        return {'type': 'ir.actions.act_window_close'}


        
        

        
        
        



