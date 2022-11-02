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


class GradeImportWizard(models.TransientModel):
    _name = "odoocms.grade.import.wizard"
    _description = 'Grade Import Wizard'
    
    file = fields.Binary('File')
    register_only = fields.Boolean('Register Only',default=False)
    classes_only = fields.Boolean('Classes Only',default=True)
    

    def import_grade_data(self):
        reg = self.env['odoocms.student.course']
        sem = self.env['odoocms.student.semester']
        class_ids = self.env['odoocms.class']
        
        fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.file))
        fp.seek(0)
        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(0)

        rows = self.env['odoo.progress'].search([('name', '<', sheet.nrows)])
        for row_num in rows.with_progress(msg="Fee Import"):
            row = sheet.row_values(row_num.name)

        # for row_num in range(1, sheet.nrows):  # From row 2 to Last Row
        #     _logger.info('Subject Result of %s of %s' % (row_num, sheet.nrows))
        #     row = sheet.row_values(row_num)
            
            if self.classes_only:
                term = int(row[1])
                academic_semester = self.env['odoocms.academic.term'].search([('short_code', '=', term)])
                if not academic_semester:
                    raise UserError('Term not found: %s' % (term))
                class_nbr = int(row[4])
                class_id = self.env['odoocms.class'].search([('class_nbr', '=', class_nbr), ('term_id', '=', academic_semester.id)])
                data = {
                    'crse_id': int(row[0]),
                    'class_nature': row[5].lower(),
                    'strength': int(row[6]),
                    'class_section': row[7],
                }
                if not class_id:
                    data.update({
                        'term_id': academic_semester.id,
                        'course_code': row[2],
                        'course_name': row[3],
                        'class_nbr': class_nbr,
                        'name': row[3] + "-" + str(class_nbr),
                        'code': row[2] + "-" + str(class_nbr),
                    })
                    self.env['odoocms.class'].create(data)
                else:
                    class_id.write(data)
                
            else:
                student_code = row[0]
                semester = int(row[1])

                student = self.env['odoocms.student'].search([('code', '=', student_code)])
                if not student:
                    raise UserError('Student %s not found in database' % (student_code,))
                
                academic_semester = self.env['odoocms.academic.term'].search(
                    [('short_code', '=', semester)])
                if not academic_semester:
                    raise UserError('Academic Term %s not found in database' % semester)
                    
                class_nbr = int(row[2])
                # subject = row[2] + '-' + student.section_id.code
                class_id = self.env['odoocms.class'].search([('class_nbr', '=', class_nbr),('term_id','=',academic_semester.id)])
                if not class_id:
                    raise UserError('Class not found with class number %s' % class_nbr)
                    # return True
                    # data = {
                    #     'student': row[0],
                    #     'stream': row[1],
                    #     'class_nbr': row[2],
                    #     'units' : row[3],
                    #     'grade': row[4],
                    #     'repeat_code': row[5],
                    #     'include_in_cgpa': row[6],
                    #     # 'grade_date': row[7],
                    # }
                    # self.env['odoocms.missing.result'].sudo().create(data)
                    # continue


                
                #if not class_id.weightage or class_id.weightage < 1:
                #    class_id.weightage = row[3]
                
                # if row[3] != class_id.weightage:
                #     raise UserError('Weightage difference: Class %s Student (%s)' % (class_nbr, student_code))
                # if not class_id.class_nbr:
                #     class_id.class_nbr = class_nbr
                
                if class_id not in class_ids:
                    class_ids += class_id
                
                # grade = self.env['odoocms.exam.grade'].search([
                #     ('name', '=', row[4]),
                #     ('class_id','=',False)
                # ])
                # if not grade:
                #     raise UserError('Grade %s not found in database' % grade)
                
                semester_scheme = self.env['odoocms.semester.scheme'].search([
                        ('term_id', '=', academic_semester.id),
                        ('academic_session_id','=',student.academic_session_id.id)
                    ])
    
                #if semester_scheme:
                #    if not student.term_id or not student.semester_id:
                #        student.term_id = semester_scheme.term_id.id
                #        student.semester_id = semester_scheme.semester_id.id
                        
                st_sem = sem.search([('student_id', '=', student.id), ('term_id', '=', academic_semester.id), ])
                if not st_sem:
                    data = {
                        'student_id': student.id,
                        'term_id': academic_semester.id,
                        'semester_id': semester_scheme.semester_id.id if semester_scheme else student.semester_id.id,
                    }
                    st_sem = sem.create(data)
    
                scheme_line = class_id.study_scheme_line_id
                course_id_1 = reg.search([
                    ('course_code', '=', scheme_line.course_code), ('student_id', '=', student.id),
                    ('semester_date', '<', academic_semester.date_start), ('include_in_cgpa', '=', True)
                ])
                
                new_registration = student.register_course(academic_semester, scheme_line.course_code, st_sem, class_id.primary_class_id)
                if new_registration.get('reg', False):
                    registration = new_registration.get('reg')
                    grade_date = str(fields.Date.today())
                    # if row[7].ctype == 3:  # Date
                    # if row[7]:
                    #     date_value = xlrd.xldate_as_tuple(row[7], workbook.datemode)
                    #     grade_date = date(*date_value[:3]).strftime('%Y-%m-%d')
                    #     registration.grade_date = grade_date
                    #
                    # registration.repeat_code = row[5]
                    # registration.inc_in_cgpa = row[6]

                    # registration.grade = grade.name
                    registration.grade = row[3]

                    if course_id_1:
                        course_id_1.course_id_2 = registration.id
                        registration.course_id_1 = course_id_1.id
                    # registration.state = 'done'
                    
                # elif new_registration.get('error',False):
                
            if not self.register_only and not self.classes_only:
                for class_id in class_ids:

                    class_id.grade_upload_date = class_id.grade_upload_date2
                    class_id.grade_upload_date2 = date.today()

                    class_id.compute_result()
                    #class_id.finalize_result()
