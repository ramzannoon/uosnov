import pdb
import time
from odoo import api, fields, models, _, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class StudentTimeTable(models.TransientModel):
    _name = 'student.time.table.wiz'
    _description = 'Student Time Table Report'

    # @api.model
    # def _get_program(self):
    #     program_id = self.env['odoocms.program'].browse(self._context.get('active_id', False))
    #     if program_id:
    #         return program_id.id
    #     return True

    program_id = fields.Many2one('odoocms.program', 'Program', required=True )
    batch_id = fields.Many2one('odoocms.batch', 'Batch', required=True)
    batch_section_id = fields.Many2one('odoocms.batch.section', 'Section', required=True)
    term_id = fields.Many2one('odoocms.academic.term', 'Term', required=True)


    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'form': data
        }

        return self.env.ref('odoocms_timetable.action_report_student_time_table').with_context(landscape=True).report_action(self, data=datas,config=False)





