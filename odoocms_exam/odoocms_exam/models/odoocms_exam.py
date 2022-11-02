
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date , datetime
import math
from odoo.tools.safe_eval import safe_eval
from odoo.osv import expression
import pdb

import logging
_logger = logging.getLogger(__name__)


def round_half_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n*multiplier + 0.5) / multiplier


class OdooCMSGradeGPA(models.Model):
    _name = 'odoocms.grade.gpa'
    _description = 'Grade GPA'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'gpa desc'
    
    name = fields.Char('Grade Name')
    gpa = fields.Float('GPA')

    to_be = fields.Boolean(default=True)

    remarks_type = fields.Selection([('warning', 'Warning'), ('probation', 'Probation'), ('suspension', 'Suspension'), ('withdraw', 'Withdraw')], string="Remarks Status")
    remarks = fields.Char('Remarks',tracking=True)

class OdooCMSGradeGPAMarks(models.Model):
    _name = 'odoocms.grade.gpamarks'
    _description = 'Grade Points Method'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'gpa desc'
    
    marks = fields.Integer('Marks Grade Name')
    gpa = fields.Float('Grade Value')


class OdooCMSClassGrade(models.Model):
    _inherit = 'odoocms.class.grade'
    
    def compute_result(self):
        for rec in self:
            for primary_class in rec.primary_class_ids:
                primary_class.compute_result()

    def result_verified(self):
        for rec in self:
            for primary_class in rec.primary_class_ids:
                primary_class.result_verified()
                
        
class OdooCMSClassPrimary(models.Model):
    _inherit = 'odoocms.class.primary'
    
    to_be = fields.Boolean(default=True)

    def compute_result(self):
        # freshman_grading = self.env['ir.config_parameter'].sudo().get_param('odoocms_exam.freshman_grading') or False
        freshman_grading = False
        if freshman_grading:
            freshman_terms = self.env.user.company_id.freshman_semesters
            freshman_passing_grades = self.env.user.company_id.freshman_passing_grades
            freshman_exculded_grades = self.env.user.company_id.freshman_exculded_grades
        
            for registration in self.registration_ids:
                if registration.grade:
                    grade_rec = self.env['odoocms.grade.gpa'].search([('name', '=', registration.grade)])
                    if registration.term_id.id in freshman_terms.ids:
                        if grade_rec in freshman_passing_grades:
                            registration.gpa = grade_rec.gpa
                        
                            registration.include_in_cgpa = True  # Mazhar
                            registration.include_in_transcript = True  # Mazhar
                        else:
                            registration.gpa = 0
                            registration.include_in_transcript = False
                            registration.include_in_cgpa = False
                    else:
                        registration.gpa = grade_rec.gpa
                else:
                    registration.gpa = 0
        else:
            for registration in self.registration_ids:
                registration.calculate_gpa()

    def result_verified(self):
        for registration in self.registration_ids:
            if registration.course_id_1:
                if registration.gpa < registration.course_id_1.gpa:
                    registration.include_in_cgpa = False
                else:
                    registration.course_id_1.include_in_cgpa = False
                    registration.repeat_code = '[RPT]'
                    registration.course_id_1.repeat_code = 'R*'
                    
        self.state = 'done'
        self.grade_class_id.state = 'done'
        self.class_ids.state = 'done'

    @api.model
    def cron_job(self, n=500):
        recs_count = self.search_count([('to_be', '=', True)])
        primary_class_ids = self.search([('to_be', '=', True)], limit=n)
        for primary_class_id in primary_class_ids: #.with_progress(msg="Compute Result ({})".format(recs_count)):
            primary_class_id.compute_result()

            # for reg in primary_class_id.registration_ids:
            #     reg.to_be = True

            # grade_class_id.finalize_result()
            # primary_class_id.state = 'done'
            primary_class_id.to_be = False


class OdooCMSStudentCourse(models.Model):
    _inherit = "odoocms.student.course"

    grade_points = fields.Float('Grade Points', compute='_get_grade_points', store=True)
    gpa = fields.Float('GPA', digits=(8, 2))

    include_in_cgpa = fields.Boolean('Include in CGPA', default=True)
    include_in_transcript = fields.Boolean('Include in Transcript', default=True)
    equivalent_code = fields.Char('Equivalent Code')

    earn_credit = fields.Boolean('Earn Credit', default=True)
    repeat_candidate = fields.Boolean('Repeat Candidate', default=False)
    valid_attempt = fields.Boolean('Valid Attempt', default=True)

    is_before_result = fields.Boolean(default=True)
    to_be = fields.Boolean(default=True)
    remarks = fields.Char('Remarks')

    # After this computation GPA calculation, Credit and earned Credit calculation is remaining. need to discuss

    def calculate_gpa(self):
        grade_point_method = self.env['ir.config_parameter'].sudo().get_param('odoocms_exam.gradpoints_method') or False
        for registration in self:
            if registration.grade:
                grade_rec = self.env['odoocms.grade.gpa'].search([('name', '=', registration.grade)])
                if grade_point_method == 'marks':
                    if registration.normalized_marks > 49:
                        grade_rec = self.env['odoocms.grade.gpamarks'].search([('marks', '=', registration.normalized_marks)])
                    else:
                        grade_rec = self.env['odoocms.grade.gpa'].search([('name', '=', 'F')])
            
                if grade_rec:
                    registration.gpa = grade_rec.gpa
                else:
                    raise UserError('Please Configure Grade GPA for %s' % (registration.grade,))
            else:
                registration.gpa = 0
            
    def cron_grade_i_to_f(self, days):
        i_grade_request = self.env['odoocms.student.course.incomplete'].search([('state','=', 'approve')]).mapped('registration_id.id')
        for rec in self.filtered(lambda l:l.id in i_grade_request):
            if date.today() - rec.grade_date > days:
                rec.grade_date = date.today()
                rec.grade = 'F'
                message = "Grade has been auto changed from 'I' to 'F' on %s", ( str(date.today()) )
                rec.message_post(body=message )

    @api.depends('gpa', 'credits')
    def _get_grade_points(self):
        for rec in self:
            if rec.credit > 0:
                rec.grade_points = rec.gpa * rec.credit
            else:
                rec.grade_points = rec.gpa * rec.credits

    def cron_job(self, n=1000):
        recs_count = self.search_count([('to_be', '=', True)])
        lines = self.search([('to_be', '=', True)], limit=n)
        for line in lines.sorted(key=lambda r: r.number, reverse=False):   #.with_progress(msg="Scanning Result ({})".format(recs_count)):
            line.calculate_gpa()
            if line.state in ('done','notify'):
                course_id_1 = self.search([
                    ('course_code', '=', line.course_code), ('student_id', '=', line.student_id.id),
                    ('number', '<', line.number), ('include_in_cgpa', '=', True)
                ])
                if course_id_1:
                    course_id_1.course_id_2 = line.id
                    line.course_id_1 = course_id_1.id
    
                    if line.gpa < line.course_id_1.gpa:
                        line.include_in_cgpa = False
                        line.course_id_1.include_in_cgpa = True
                    else:
                        line.course_id_1.include_in_cgpa = False
                        line.include_in_cgpa = True
                        
            st_term = self.env['odoocms.student.term'].search([
                ('student_id','=',line.student_id.id),
                ('term_id','=',line.term_id.id)
            ])
            st_term.to_be = True
            line.to_be = False


class OdooCMSStudentTerm(models.Model):
    _inherit = "odoocms.student.term"
    
    grade_points = fields.Float('Grade Points',compute='get_sgpa',store=True)
    credits = fields.Float('Attempted Credits',compute='get_sgpa',store=True)
    earned_credits = fields.Float('Earned Credits', compute='get_sgpa', store=True)
    sgpa = fields.Float('SGPA',compute='get_sgpa',store=True)

    cgp = fields.Float('CGP', compute='get_sgpa', store=True)
    cch = fields.Float('ACCH', compute='get_sgpa', store=True)
    ecch = fields.Float('CCH', compute='get_sgpa', store=True)
    cgpa = fields.Float('CGPA', compute='get_sgpa', store=True)
    to_be = fields.Boolean(default=False)

    @api.depends('student_course_ids.grade_points','student_course_ids.credits','student_course_ids.state','student_course_ids.include_in_cgpa')
    def get_sgpa(self):
        sgpa_rounding = int(self.env['ir.config_parameter'].sudo().get_param('odoocms.sgpa_rounding') or '0')
        cgpa_rounding = int(self.env['ir.config_parameter'].sudo().get_param('odoocms.cgpa_rounding') or '0')

        excluded_grades = (self.env['ir.config_parameter'].sudo().get_param('odoocms_exam.excluded_grades') or 'I,W,XF').replace(' ','').split(',')
        for rec in self:
            credits = earned_credits = grade_points = 0
            for course in rec.student_course_ids:
                if course.include_in_cgpa and course.grade:   #  and course.type != 'thesis'
                    if course.credit > 0:
                        credits += course.credit
                    else:
                        credits += course.credits
                    grade_points += course.grade_points
                    if course.grade not in (excluded_grades):
                        if course.credit > 0:
                            earned_credits += course.credit
                        else:
                            earned_credits += course.credits

            rec.credits = credits
            rec.earned_credits = earned_credits
            rec.grade_points = grade_points
            rec.sgpa = round_half_up(grade_points / (earned_credits or 1.00),sgpa_rounding)

            cch = ecch = cgp = 0
            for term in rec.student_id.enroll_term_ids.filtered(
                    lambda l: l.number <= rec.number):
                ecch += term.earned_credits
                cch += term.credits
                cgp += term.grade_points

            rec.cch = cch
            rec.ecch = ecch
            rec.cgp = cgp
            rec.cgpa = round_half_up(cgp / (ecch or 1.00),cgpa_rounding)

    def cron_job(self,n=2000):
        recs_count = self.search_count([('to_be', '=', True)])
        terms = self.search([('to_be','=',True)],limit=n, order='student_id,number')
        for term in terms: #.with_progress(msg="Term Result ({})".format(recs_count)):
            term.get_sgpa()
            term.to_be = False

            
class OdooCMSStudent(models.Model):
    _inherit = 'odoocms.student'

    grade_points = fields.Float('Grade Points', compute='_get_cgpa', store=True)
    credits = fields.Float('Total Credits', compute='_get_cgpa', store=True)
    cgpa = fields.Float('CGPA', compute='_get_cgpa', store=True)
    earned_credits = fields.Float('Pass Credits', compute='_get_cgpa', store=True)
    f_grades = fields.Integer('F Grades',compute='_get_f_grades',store=True)  #
    remarks_type = fields.Selection([('warning','Warning'),('probation','Probation'),('suspension','Suspension'),('withdraw','Withdraw')], string="Remarks Status")
    remarks = fields.Char('Remarks')

    deficient_course_ids = fields.One2many('odoocms.student.course', 'student_id', 'Deficient Courses', domain=[('state', '=', 'done'), ('is_deficient', '=', True)])
    disposal_type_id = fields.Many2one('odoocms.exam.disposal.type', string='Disposal Type', tracking=True)

    alternate_ids = fields.One2many('odoocms.student.course.alternate','student_id','Alternate Courses')

    @api.depends('enrolled_course_ids','enrolled_course_ids.grade','enrolled_course_ids.include_in_cgpa')
    def _get_f_grades(self):
        for student in self:
            f_grades = student.enrolled_course_ids.filtered(
                lambda l: l.active==True and (l.grade == 'XF' or (l.grade == 'F' and l.include_in_cgpa == True)))
            student.f_grades = len(f_grades)
        
    @api.depends('term_ids','term_ids.grade_points', 'term_ids.credits')
    def _get_cgpa(self):
        cgpa_rounding = int(self.env['ir.config_parameter'].sudo().get_param('odoocms.cgpa_rounding') or '0')
        for rec in self:
            credits = earned_credits = grade_points = 0
            for term in rec.term_ids:
                credits += term.credits
                grade_points += term.grade_points
                earned_credits += term.earned_credits

            rec.credits = credits
            rec.earned_credits = earned_credits
            rec.grade_points = grade_points
            rec.cgpa = round_half_up(grade_points / (credits or 1.00),cgpa_rounding)

    def _prereq_satisfy(self, pre_courses, operator='and'):
        #studied = self.result_course_ids.filtered(lambda l: l.include_in_cgpa and l.grade not in ('W', 'F','I','XF')).mapped('course_id')
        studied = self.enrolled_course_ids.filtered(lambda l: l.include_in_cgpa and l.grade not in ('W', 'F', 'I', 'XF')).mapped('course_id')
        
        if (not operator) or operator == 'and':
            for course in pre_courses:
                if course not in studied:
                    return False
            return True
        elif operator == 'or':
            for course in pre_courses:
                if course in studied:
                    return True
            return False
    
    def apply_disposals(self, disposal_history_id):
        flag = False
        disposal_type_id = False
        disposal_rule_ids = self.env['odoocms.exam.disposal.rule'].search([('active','=',True)]).sorted(key=lambda d: d.sequence, reverse=False)
        promoted_tag = self.env['odoocms.student.tag'].search([('name', '=', 'Promoted')])
        if not promoted_tag:
            values = {
                'name': 'Promoted',
                'code': 'Promoted',
            }
            promoted_tag = self.env['odoocms.student.tag'].create(values)
            
        for disposal_rule_id in disposal_rule_ids:
            domain = expression.AND([safe_eval(disposal_rule_id.domain), [('id', '=', self.batch_id.id)]]) if disposal_rule_id.domain else []
            batch = self.env['odoocms.batch'].search(domain)
            if not batch:
                continue
            if flag:
                break
                
            for rule_line in disposal_rule_id.line_ids.sorted(key=lambda d: d.sequence, reverse=True):
                # domain = [('id','=', student.id)]
                # rule_line_domain = 'student.' + eval(rule_line.domain)[0][0].replace(' ','').split('.')[0]
                # records = eval(rule_line_domain)[:rule_line.limit]
                # student_id =  self.env['odoocms.student'].search(domain)
                localdict = {
                    'result': False,
                    'student': self,
                    'disposal_term': disposal_history_id.term_id.id,
                    'self': self,
                }
                #pdb.set_trace()
                if rule_line.type == 'code':
                    # if rule_line.name == 'SGPA < 2':
                    #     pdb . set_ trace()
                    #     b = 5
                    try:
                        localdict['result'] = eval(rule_line.code, localdict)
                    except:
                        b = 5
                
                    if localdict['result']:
                        disposal_type_id = rule_line.disposal_rule_id.disposal_type_id
                        hist_values = {
                            'history_id': disposal_history_id.id,
                            'student_id': self.id,
                            'pre_disposal_type_id': self.disposal_type_id and self.disposal_type_id.id or False,
                            'disposal_type_id': disposal_type_id.id,
                            'rule_line_id': rule_line.id,
                        }
                        self.env['odoocms.exam.disposal.history.line'].create(hist_values)
                        tags = self.tag_ids + disposal_type_id.tag_id
                        flag = True
                        break
        if not flag:
            tags = self.tag_ids + promoted_tag
        
        data = {
            'disposal_type_id': disposal_type_id and disposal_type_id.id or False,
            'tag_ids': [[6, 0, tags.ids]]
        }
        if disposal_type_id and disposal_type_id.state:
            data['state'] = disposal_type_id.state.value
            
        self.write(data)
        student_term = self.enroll_term_ids.filtered(lambda s: s.term_id == self.term_id)
        if student_term:
            if disposal_type_id:
                student_term.disposal_type_id = disposal_type_id.id
                student_term.rule_line_id = rule_line.id
            else:
                student_term.disposal_type_id = False
                student_term.rule_line_id = False
                
    def get_datesheet(self,term_id):
        balance = 0
        # invoice = self.env['account.invoice'].search([('student_id', '=', st.id), ('state', '=', 'open')])
        # for inv in invoice:
        #     balance += sum(inv.residual for i in inv)
        personal_info = {
            "name": self.name,
            "code": self.code,
            "father": self.father_name,
            "career": self.career_id.name,
            "term": self.term_id.name,
            "program": self.program_id.name,
            "department": self.program_id.department_id.name,
            "semester": self.semester_id.name,
            "image_1920": self.image_1920,
            "balance": " " + str(balance),
            "cnic": self.cnic
        }
        course_list = []
        for course in self.env['odoocms.student.course'].search([
            ('student_id', '=', self.id), ('term_id', '=', term_id)]):
            datesheet_line = self.env['odoocms.datesheet.line'].search([
                ('batch_id', '=', course.batch_id.id), ('term_id', '=', term_id),
                ('course_id', '=', course.course_id.id)
            ],limit=1)
            
            course = {
                "time_start": datesheet_line and datesheet_line.time_start.name or '',
                "date": datesheet_line and datesheet_line.date or '',
                "code": course.course_id.code,
                "name": course.course_id.name
            }
            course_list.append(course)
    
        return personal_info, course_list

    @api.model
    def cron_job(self, n=500):
        recs_count = self.search_count([('to_be', '=', True)])
        students = self.search([('to_be', '=', True)], limit=n)
        for student in students:  # .with_progress(msg="Compute Result ({})".format(recs_count)):
            student._get_f_grades()
            student.to_be = False


class OdooCMSBatch(models.Model):
    _inherit = "odoocms.batch"

    def batch_term_hook(self,batch_term_data):
        # batch_term_data['disposal_rule_ids'] = [(6, 0, self.disposal_rule_ids.ids)]
        return batch_term_data
    
    
class OdooCMSBatchTerm(models.Model):
    _inherit = "odoocms.batch.term"
    
    #disposal_rule_ids = fields.Many2many('odoocms.exam.disposal.rule', related='batch_id.disposal_rule_ids', store=True, string='Disposal Rules')

    def apply_disposal_rules(self):
        hist_list = self._apply_disposal_rules()
        return {
            'domain': [('id', 'in', hist_list)],
            'name': _('Disposals'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'odoocms.exam.disposal.history',
            # 'view_id': False,
            'type': 'ir.actions.act_window'
        }
    
    def _apply_disposal_rules(self):
        # comp_domain = student.program_id.registration_domain
        # comp_domain = expression.AND([safe_eval(comp_domain), [('term_id', '=', new_term.id)]]) if comp_domain else []
        not_disposal_classes = self.env['odoocms.class.grade']
        for grade_class in self.grade_class_ids:
            if grade_class.primary_class_ids and grade_class.state not in ('disposal','approval','verify','done'):
                not_disposal_classes += grade_class
    
        if not_disposal_classes:
            raise UserError('%s Classes are not in the Disposal Status\n' % (', '.join([k.code for k in (not_disposal_classes)])))
    
        if self.waiting_ids:
            raise UserError('There are some Registrations in the Pre-Disposal Status')
            
        history_ids = self.env['odoocms.exam.disposal.history']
        values = {
            'batch_id': self.batch_id.id,  # [(6, 0, self.batch_ids.mapped('id'))],
            'batch_term_id': self.id,
            'user_id': self.env.user.id,
            'date': datetime.now(),
            'term_id': self.term_id.id,
        }
        disposal_history_id = self.env['odoocms.exam.disposal.history'].create(values)
        history_ids += disposal_history_id
    
        students = self.batch_id.student_ids.filtered(
            lambda l: all(tag.code not in ['suspension of registration','extra','deferred'] for tag in l.tag_ids)
                and l.state == 'enroll' and l.enroll_term_ids)

        for student in students:
            student_enrolled = self.env['odoocms.student.course'].sudo().search([('term_id','=',self.term_id.id)])
            if student_enrolled:
                student.apply_disposals(disposal_history_id)
                        
        hist_list = history_ids.mapped('id')
        return hist_list
    
    def result_verified(self):
        self.ensure_one()
        for grade_class in self.grade_class_ids:
            grade_class.result_verified()
