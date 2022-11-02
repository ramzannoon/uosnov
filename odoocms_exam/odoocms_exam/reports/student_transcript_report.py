import base64
import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import os
import tempfile
import logging
_logger = logging.getLogger(__name__)

from PyPDF2 import PdfFileReader, PdfFileWriter
import  PyPDF2


class StudentTranscriptReport(models.AbstractModel):
    _name = 'report.odoocms_exam.student_transcript_report'
    _description = 'Student Transcript Report'

    @api.model
    def create_doc_report(self, docsid, data=None):
        input_files = []
        pdf_report_fd, pdf_report_path = tempfile.mkstemp(suffix='.pdf', prefix='transcripts.tmp.')
        f = open(pdf_report_path, 'wb')

        for student in docsid:
            student_rec = self.env['odoocms.student'].browse(student)

            pdf_content, transcript_pdf_report_path = student_rec.gen_transcript()
            input_files.append(transcript_pdf_report_path)

            transcript_data=self.env['odoocms.transcript.history']
            data={
                'date': date.today(),
                'student_id': student,
                'term_id': student_rec.term_id.id or False,
                'transcript': base64.encodestring(pdf_content),
            }
            transcript_data.sudo().create(data)

        #Here is to merge the pdf into one pdf
        input_streams = []
        try:
            for input_file in input_files:
                input_streams.append(open(input_file, 'rb'))
            writer = PdfFileWriter()
            for reader in map(PdfFileReader, input_streams):
                for n in range(reader.getNumPages()):
                    writer.addPage(reader.getPage(n))
            writer.write(f)
        finally:
            for f in input_streams:
                f.close()

        # Manual cleanup of the temporary files
        for temporary_file in input_files:
            try:
                os.unlink(temporary_file)
            except (OSError, IOError):
                _logger.error('Error when trying to remove file %s' % temporary_file)

        with open(pdf_report_path, 'rb') as pdf_document:
            output_pdf_content = pdf_document.read()
        pdf_document.close()

        return output_pdf_content


class StudentUnofficialTranscriptReport(models.AbstractModel):
    _name = 'reports.odoocms_exam.student_transcript_report2'
    _description = 'Student Unofficial Transcript Report'

    @api.model
    def create_doc_report(self, docsid, data=None):

        watermark_file_path = os.path.expanduser('/opt/odoo/custom/uet/odoocms_exam/static/description/water_mark.pdf')  #this is my addon path
        # watermark_file_path = os.path.expanduser('/opt/odoo/custom/addons/odoocms_exam/static/description/water_mark.pdf') # for server

        pdfWatermarkReader = PyPDF2.PdfFileReader(open(watermark_file_path, 'rb'))

        input_files = []
        pdf_report_fd, pdf_report_path = tempfile.mkstemp(suffix='.pdf', prefix='un-off-transcripts.tmp')
        f = open(pdf_report_path, 'wb')

        for student in docsid:
            student_rec = self.env['odoocms.student'].browse(student)

            pdf_content, input_pdf_report_path = student_rec.gen_transcript()
            input_files.append(input_pdf_report_path)

        #Here is to merge the pdf into one pdf
        input_streams = []
        try:
            for input_file in input_files:
                input_streams.append(open(input_file, 'rb'))
            writer = PdfFileWriter()
            for reader in map(PdfFileReader, input_streams):
                for n in range(reader.getNumPages()):
                    page = reader.getPage(n).mergePage(pdfWatermarkReader.getPage(0))
                    writer.addPage(reader.getPage(n))
            writer.write(f)
        finally:
            for f in input_streams:
                f.close()

        # Manual cleanup of the temporary files
        for temporary_file in input_files:
            try:
                os.unlink(temporary_file)
            except (OSError, IOError):
                _logger.error('Error when trying to remove file %s' % temporary_file)


        with open(pdf_report_path, 'rb') as pdf_document:
            output_pdf_content = pdf_document.read()
        pdf_document.close()

        return output_pdf_content
