from odoo import models, fields, api, _
from datetime import datetime
import logging
from odoo.http import request, content_disposition, route
from collections import Counter, OrderedDict
from itertools import product
from odoo.exceptions import UserError, AccessError, ValidationError
_logger = logging.getLogger(__name__)



class Surveys(models.Model):
    _inherit = "survey.survey"
    survey_seq_no = fields.Char(string="Survey ID", required=False, copy=False, readonly=False, index=True, store=True,
                                default=lambda self: _('New'))
    template_seq_no = fields.Char(string="Template ID", required=False, copy=False, readonly=False, index=True,
                                  store=True,
                                  default=lambda self: _('New'))
    start_date = fields.Datetime(string="Start Date", required=False, )
    end_date = fields.Datetime(string="End Date", required=False, )
    current_date = fields.Datetime(string="Current Date", required=False, default=fields.Datetime.now,
                                   compute='set_currentdate', store=True, )
    survey_form_type = fields.Many2one('survey.types', string='Form Types', required=True, )
    survey_form_type_name = fields.Char(related='survey_form_type.name', string='Form Types Name', required=False, )
    type = fields.Selection([
        ('survey', 'Survey'),
        ('template', 'Template'),
    ], string='Type', readonly=False, default='survey')
    student_id = fields.Many2one('odoocms.student', string='Student')
    batch_id = fields.Many2one('odoocms.batch', string='Batch')
    program_id = fields.Many2one('odoocms.program', related='batch_id.program_id', store=True, string='Program')
    department_id = fields.Many2one('odoocms.department', related='batch_id.department_id', store=True,
                                    string='Department')
    institute_id = fields.Many2one('odoocms.institute', related='department_id.institute_id', store=True,
                                   string='School')
    campus_id = fields.Many2one('odoocms.campus', related='institute_id.campus_id', store=True, string='Campus')
    career_id = fields.Many2one('odoocms.career', related='batch_id.career_id', store=True, string='Academic Level')

    faculty_staff_id = fields.Many2one('odoocms.faculty.staff', string='Faculty')

    term_id = fields.Many2one('odoocms.academic.term', string='Academic Term')
    primary_class_id = fields.Many2one(comodel_name='odoocms.class.primary', string='Primary Class', )
    class_id = fields.Many2one('odoocms.class', string='Class')
    course_id = fields.Many2one('odoocms.course', related='class_id.course_id', string='Course')
    class_id_name = fields.Char(related='class_id.name', string='Class Name')
    section_id = fields.Many2one('odoocms.batch.section', string='Section')

    course_count_a = fields.Char(string='A Grade')
    course_count_b_plus = fields.Char(string='B+ Grade')
    course_count_b = fields.Char(string='B Grade')
    course_count_c_plus = fields.Char(string='C+ Grade')
    course_count_c = fields.Char(string='C Grade')
    course_count_d_plus = fields.Char(string='D+ Grade')
    course_count_d = fields.Char(string='D Grade')
    course_count_f = fields.Char(string='F Grade')
    course_count_w = fields.Char(string='W Grade')
    course_count_i = fields.Char(string='I Grade')

    class_assessments = fields.One2many(comodel_name='survey.course_rev.assesments_types', inverse_name='survey_id',
                                        string='Class Assessments', copy=True)

    # quiz = fields.Char(string='Quiz')
    # assignment = fields.Char(string='Assignment')
    # oht = fields.Char(string='OHT')
    # final = fields.Char(string='Final')
    # project = fields.Char(string='Project')
    # lab_work = fields.Char(string='Lab Work')
    # final_lab = fields.Char(string='Final Lab')

    weighted_avg = fields.Float(string='Weighted Avg')
    score = fields.Float(string='Score')
    score_avg = fields.Float(string='Score Avg')
    rating = fields.Char(string='Rating')
    excellent = fields.Integer(string='Excellent')
    vgood = fields.Integer(string='V Good')
    good = fields.Integer(string='Good')
    avg = fields.Integer(string='Avg')
    poor = fields.Integer(string='Poor')

    bps = fields.Char(string='BPS')
    department = fields.Char(string='Department')

    def action_test_survey1(self):
        ''' Open the website page with the survey form into test mode'''
        self.ensure_one()
        survey_input_ids = self.env['survey.user_input'].sudo().search([('partner_id', '=', self.env.user.partner_id.id),('survey_id', '=', self.id)])
        return {
            'type': 'ir.actions.act_url',
            'name': "Test Survey",
            'target': 'self',
            'url': '/survey/fill/%s/%s' % (self.access_token, survey_input_ids.token),
            # '/survey/fill/%s/%s' % (survey_sudo.access_token, answer_sudo.token)
        }

    @api.model
    def create(self, vals):
        if vals.get('survey_seq_no', _('New')) == _('New') and vals['type'] == 'survey':
            vals['survey_seq_no'] = self.env['ir.sequence'].next_by_code('survey.survey_sequence_num') or _('New')
        elif vals.get('survey_seq_no', _('New')) == _('New') and vals['type'] == 'template':
            vals['template_seq_no'] = self.env['ir.sequence'].next_by_code('survey.temp_sequence_num') or _('New')

        survey = super(Surveys, self).create(vals)
        already_exists = self.env['survey.survey'].sudo().search(
            [('id', '!=', survey.id), ('title', '=', survey.title),
             ('state', '=', 'open')])
        if already_exists:
            raise UserError(
                _("Duplicate Survey is not Allowed. Survey already exists with: \n Title = ' %s '" % (
                    already_exists.title)))
        return survey

    @api.depends('title', 'end_date', 'type', 'answer_done_count')
    def set_currentdate(self):
        for rec in self:
            if rec.title and rec.type != 'template':
                rec.current_date = datetime.today()
                if rec.end_date:
                    registered = self.env['survey.user_input'].sudo().search([('survey_id', '=', rec.id)])
                    for register in registered:
                        register.deadline = rec.end_date
                    difference = rec.end_date - rec.current_date
                    if (difference).days < 0 and rec.state == 'open':
                        rec.state = 'closed'
                        survey_sudo = request.env['survey.survey'].sudo().search([('id', '=', rec.ids[0])])
                        question_sudo = request.env['survey.question'].sudo().search([('survey_id', '=', rec.ids[0])])
                        for question in question_sudo:
                            self.prepare_result(question)

    @api.onchange('end_date', 'title', 'state', 'current_date')
    def current_datechanged(self):
        for rec in self:
            if rec.title and rec.type != 'template':
                rec.current_date = datetime.today()
                if rec.end_date:
                    registered = self.env['survey.user_input'].sudo().search([('survey_id', '=', rec.id)])
                    for register in registered:
                        register.deadline = rec.end_date
                    difference = rec.end_date - rec.current_date
                    if (difference).days < 0 and rec.state == 'open':
                        rec.state = 'closed'
                        survey_sudo = request.env['survey.survey'].sudo().search([('id', '=', rec.ids[0])])
                        question_sudo = request.env['survey.question'].sudo().search([('survey_id', '=', rec.ids[0])])
                        for question in question_sudo:
                            self.prepare_result(question)

    @api.model
    def survey_inprogress_enddate(self):
        today = fields.Date.today()
        if today:
            surveys_inprogress = self.env['survey.survey'].search([('end_date', '<', today), ('state', '=', 'open')])
            if surveys_inprogress:
                for surveys in surveys_inprogress:
                    if surveys.state == 'open':
                        surveys.state = 'closed'

    @api.model
    def survey_prepare_result(self):
        survey_sudo = request.env['survey.survey'].sudo().search([('state', '!=', 'draft')])
        for survey in survey_sudo:
            question_sudo = request.env['survey.question'].sudo().search([('survey_id', '=', survey.id)])
            for question in question_sudo:
                self.prepare_result(question)

    @api.model
    def prepare_result(self, question, current_filters=None):

        """ Compute statistical data for questions by counting number of vote per choice on basis of filter """
        current_filters = current_filters if current_filters else []
        result_summary = {}
        input_lines = question.user_input_line_ids.filtered(lambda line: not line.user_input_id.test_entry)

        # Calculate and return statistics for choice
        if question.question_type in ['simple_choice', 'multiple_choice']:
            comments = []
            answers = OrderedDict(
                (label.id, {'text': label.value, 'count': 0, 'answer_id': label.id, 'answer_score': label.answer_score})
                for label in question.labels_ids)
            for input_line in input_lines:
                if input_line.answer_type == 'suggestion' and answers.get(input_line.value_suggested.id) and (
                        not (current_filters) or input_line.user_input_id.id in current_filters):
                    answers[input_line.value_suggested.id]['count'] += 1
                if input_line.answer_type == 'text' and (
                        not (current_filters) or input_line.user_input_id.id in current_filters):
                    comments.append(input_line)
            result_summary = {'answers': list(answers.values()), 'comments': comments}

        # Calculate and return statistics for matrix
        if question.question_type == 'matrix':
            excellent = vgood = good = avg = poor = 0
            rows = OrderedDict()
            answers = OrderedDict()
            options = OrderedDict()
            res = dict()
            comments = []
            [rows.update({label.id: label.value}) for label in question.labels_ids_2]
            [answers.update({label.id: label.value}) for label in question.labels_ids]
            for answer_option in answers:
                options[answer_option] = 0
            for cell in product(rows, answers):
                res[cell] = 0
            for input_line in input_lines:
                if input_line.answer_type == 'suggestion' and (not (
                        current_filters) or input_line.user_input_id.id in current_filters) and input_line.value_suggested_row:
                    res[(input_line.value_suggested_row.id, input_line.value_suggested.id)] += 1
                    options[input_line.value_suggested.id] += 1
                if input_line.answer_type == 'text' and (
                        not (current_filters) or input_line.user_input_id.id in current_filters):
                    comments.append(input_line)
            excellent = options[list(answers.keys())[0]]
            vgood = options[list(answers.keys())[1]]
            good = options[list(answers.keys())[2]]
            avg = options[list(answers.keys())[3]]
            poor = options[list(answers.keys())[4]]

            # Weighted  Avg
            if input_lines.user_input_id.__len__() > 0:
                weighted_avg = round(((((options[list(answers.keys())[0]] * 5) + (
                        options[list(answers.keys())[1]] * 4) + (options[list(answers.keys())[2]] * 3) + (
                                                options[list(answers.keys())[3]] * 2) + (
                                                options[list(answers.keys())[4]] * 1)) / (
                                               input_lines.user_input_id.__len__() * 5 * rows.__len__())) * 100), 2)
            else:
                weighted_avg = 0
            survey = self.env['survey.survey'].sudo().search([('id', '=', question.survey_id.id)])
            for rec in survey:
                rec.weighted_avg = weighted_avg
                rec.excellent = excellent
                rec.vgood = vgood
                rec.good = good
                rec.avg = avg
                rec.poor = poor
                if rec.weighted_avg >= 90 and rec.weighted_avg <= 100:
                    rec.rating = 'Excellent'
                elif rec.weighted_avg >= 75 and rec.weighted_avg < 90:
                    rec.rating = 'Very Good'
                elif rec.weighted_avg >= 65 and rec.weighted_avg < 75:
                    rec.rating = 'Good'
                elif rec.weighted_avg >= 50 and rec.weighted_avg < 65:
                    rec.rating = 'Satisfactory'
                elif rec.weighted_avg < 50:
                    rec.rating = 'Poor'
                else:
                    rec.rating = ''

            result_summary = {'answers': answers, 'rows': rows, 'result': res, 'comments': comments, 'options': options,
                              'weighted_avg': weighted_avg, 'rating': survey.rating}

        # Calculate and return statistics for free_text, textbox, date
        if question.question_type in ['free_text', 'textbox', 'date', 'datetime']:
            result_summary = []
            for input_line in input_lines:
                if not (current_filters) or input_line.user_input_id.id in current_filters:
                    result_summary.append(input_line)

        # Calculate and return statistics for numerical_box
        if question.question_type == 'numerical_box':
            result_summary = {'input_lines': []}
            all_inputs = []
            for input_line in input_lines:
                if not (current_filters) or input_line.user_input_id.id in current_filters:
                    all_inputs.append(input_line.value_number)
                    result_summary['input_lines'].append(input_line)
            if all_inputs:
                result_summary.update({'average': round(sum(all_inputs) / len(all_inputs), 2),
                                       'max': round(max(all_inputs), 2),
                                       'min': round(min(all_inputs), 2),
                                       'sum': sum(all_inputs),
                                       'most_common': Counter(all_inputs).most_common(5)})

        return result_summary
    #
    # @http.route('/survey/submit1/<string:survey_token>/<string:answer_token>', type='http', methods=['POST'], auth='public', website=True)
    # def survey_submit(self, survey_token, answer_token, **post):
    #     """ Submit a page from the survey.
    #     This will take into account the validation errors and store the answers to the questions.
    #     If the time limit is reached, errors will be skipped, answers wil be ignored and
    #     survey state will be forced to 'done'
    #
    #     TDE NOTE: original comment: # AJAX submission of a page -> AJAX / http ?? """
    #     access_data = self._get_access_data(survey_token, answer_token, ensure_token=True)
    #     if access_data['validity_code'] is not True:
    #         return {}
    #
    #     survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']
    #     if not answer_sudo.test_entry and not survey_sudo._has_attempts_left(answer_sudo.partner_id, answer_sudo.email, answer_sudo.invite_token):
    #         # prevent cheating with users creating multiple 'user_input' before their last attempt
    #         return {}
    #
    #     if survey_sudo.questions_layout == 'page_per_section':
    #         page_id = int(post['page_id'])
    #         questions = request.env['survey.question'].sudo().search([('survey_id', '=', survey_sudo.id), ('page_id', '=', page_id)])
    #         # we need the intersection of the questions of this page AND the questions prepared for that user_input
    #         # (because randomized surveys do not use all the questions of every page)
    #         questions = questions & answer_sudo.question_ids
    #         page_or_question_id = page_id
    #     elif survey_sudo.questions_layout == 'page_per_question':
    #         question_id = int(post['question_id'])
    #         questions = request.env['survey.question'].sudo().browse(question_id)
    #         page_or_question_id = question_id
    #     else:
    #         questions = survey_sudo.question_ids
    #         questions = questions & answer_sudo.question_ids
    #
    #     errors = {}
    #     # Answer validation
    #     if not answer_sudo.is_time_limit_reached:
    #         for question in questions:
    #             answer_tag = "%s_%s" % (survey_sudo.id, question.id)
    #             errors.update(question.validate_question(post, answer_tag))
    #
    #     ret = {}
    #     if len(errors):
    #         # Return errors messages to webpage
    #         ret['errors'] = errors
    #     else:
    #         if not answer_sudo.is_time_limit_reached:
    #             for question in questions:
    #                 answer_tag = "%s_%s" % (survey_sudo.id, question.id)
    #                 request.env['survey.user_input_line'].sudo().save_lines(answer_sudo.id, question, post, answer_tag)
    #
    #         go_back = False
    #         vals = {}
    #         if answer_sudo.is_time_limit_reached or survey_sudo.questions_layout == 'one_page':
    #             answer_sudo._mark_done()
    #         elif 'button_submit' in post:
    #             go_back = post['button_submit'] == 'previous'
    #             next_page, last = request.env['survey.survey'].next_page_or_question(answer_sudo, page_or_question_id, go_back=go_back)
    #             vals = {'last_displayed_page_id': page_or_question_id}
    #
    #             if next_page is None and not go_back:
    #                 answer_sudo._mark_done()
    #             else:
    #                 vals.update({'state': 'skip'})
    #
    #         if 'breadcrumb_redirect' in post:
    #             ret['redirect'] = post['breadcrumb_redirect']
    #         else:
    #             if vals:
    #                 answer_sudo.write(vals)
    #
    #             ret['redirect'] = '/survey/fill/%s/%s' % (survey_sudo.access_token, answer_token)
    #             if go_back:
    #                 ret['redirect'] += '?prev=prev'
    #
    #     return json.dumps(ret)



    # @api.model
    # def save_line_free_text(self, user_input_id, question, post, answer_tag):
    #     vals = {
    #         'user_input_id': user_input_id,
    #         'question_id': question.id,
    #         'survey_id': question.survey_id.id,
    #         'skipped': False,
    #     }
    #     if answer_tag in post and post[answer_tag].strip():
    #         vals.update({'answer_type': 'free_text', 'value_free_text': post[answer_tag]})
    #     else:
    #         vals.update({'answer_type': None, 'skipped': True})
    #     old_uil = self.search([
    #         ('user_input_id', '=', user_input_id),
    #         ('survey_id', '=', question.survey_id.id),
    #         ('question_id', '=', question.id)
    #     ])
    #     if old_uil:
    #         old_uil.write(vals)
    #     else:
    #         old_uil.create(vals)
    #     return True


    def copy_data(self, default=None):
        title = _("%s (copy)") % (self.title)
        default = dict(default or {}, title=title)
        surveys = super(Surveys, self).copy_data(default)
        for rec in surveys:
            if self.template_seq_no == 'Temp/0003' or self.template_seq_no == 'Temp/0010' or self.template_seq_no == 'Temp/0011':
                if self.institute_id.code:
                    rec['title'] = self.title + " - " + self.institute_id.code
                else:
                    rec['title'] = self.title
                rec['start_date'] = self.start_date
                rec['end_date'] = self.end_date
                rec['type'] = 'survey'
            elif self.template_seq_no == 'Temp/0001' or self.template_seq_no == 'Temp/0002':
                if self.class_id.code:
                    rec['title'] = self.title + " - " + self.class_id.code
                else:
                    rec['title'] = self.title
                rec['start_date'] = self.start_date
                rec['end_date'] = self.end_date
                rec['type'] = 'survey'
            elif self.template_seq_no == 'Temp/0009' or self.template_seq_no == 'Temp/0016':
                if self.primary_class_id.code:
                    rec['title'] = self.title + " - " + self.primary_class_id.code
                else:
                    rec['title'] = self.title
                rec['start_date'] = self.start_date
                rec['end_date'] = self.end_date
                rec['type'] = 'survey'
            elif self.template_seq_no == 'Temp/0008' or self.template_seq_no == 'Temp/0005' \
                    or self.template_seq_no == 'Temp/0004':
                if self.section_id.code:
                    rec['title'] = self.title + " - " + self.section_id.code
                else:
                    rec['title'] = self.title
                rec['start_date'] = self.start_date
                rec['end_date'] = self.end_date
                rec['type'] = 'survey'
            elif self.template_seq_no == 'Temp/0006':
                if self.student_id.name:
                    rec['title'] = self.title + " - " + self.student_id.name
                else:
                    rec['title'] = self.title
                rec['start_date'] = self.start_date
                rec['end_date'] = self.end_date
                rec['type'] = 'survey'
            elif self.survey_form_type.name == 'External survey':
                rec['title'] = self.title
                rec['start_date'] = self.start_date
                rec['end_date'] = self.end_date
                rec['type'] = 'survey'
            elif self.template_seq_no == 'Temp/0012':
                # if self.primary_class_id:
                rec['title'] = self.title
                rec['start_date'] = self.start_date
                rec['end_date'] = self.end_date
                rec['type'] = 'survey'

        return surveys

    def _get_access_data(self, survey_token, answer_token, ensure_token=True):
        """ Get back data related to survey and user input, given the ID and access
        token provided by the route.

         : param ensure_token: whether user input existence should be enforced or not(see ``_check_validity``)
        """
        survey_sudo, answer_sudo = self.env['survey.survey'].sudo(), self.env['survey.user_input'].sudo()
        has_survey_access, can_answer = False, False

        validity_code = self._check_validity(survey_token, answer_token, ensure_token=ensure_token)
        if validity_code != 'survey_wrong':
            survey_sudo, answer_sudo = self._fetch_from_access_token(survey_token, answer_token)
            try:
                survey_user = survey_sudo.with_user(self.env.user)
                survey_user.check_access_rights(self, 'read', raise_exception=True)
                survey_user.check_access_rule(self, 'read')
            except:
                pass
            else:
                has_survey_access = True
            can_answer = bool(answer_sudo)
            if not can_answer:
                can_answer = survey_sudo.access_mode == 'public'

        return {
            'survey_sudo': survey_sudo,
            'answer_sudo': answer_sudo,
            'has_survey_access': has_survey_access,
            'can_answer': can_answer,
            'validity_code': validity_code,
        }


# class UserInputSurveys(models.Model):
#     _inherit = "survey.user_input"
#
#     # @api.model
#     # def create(self, vals):
#     #     userinputsurvey = super(UserInputSurveys, self).create(vals)
#     #     if userinputsurvey.state == 'new':
#     #         userinputsurvey.state = 'skip'
#     #     return userinputsurvey
#
#
# class SurveyLabelInherit(models.Model):
#     """ A suggested answer for a question """
#     _inherit = 'survey.label'
#
#     # @api.model
#     # def create(self, vals):
#     #     userinput_line_survey = super(SurveyLabelInherit, self).create(vals)
#     #     for userinput_line in userinput_line_survey:
#     #         if userinput_line:
#     #             if userinput_line.value == 'Excellent':
#     #                 userinput_line.answer_score = 5
#     #             elif userinput_line.value == 'V Good':
#     #                 userinput_line.answer_score = 4
#     #             elif userinput_line.value == 'Good':
#     #                 userinput_line.answer_score = 3
#     #             elif userinput_line.value == 'Avg' or userinput_line.value == 'Fair':
#     #                 userinput_line.answer_score = 2
#     #             elif userinput_line.value == 'Poor':
#     #                 userinput_line.answer_score = 1
#     #             else:
#     #                 continue
#     #     return userinput_line


class SurveyTypes(models.Model):
    """ A survey types"""
    _name = 'survey.types'
    _description = 'Survey Types'

    name = fields.Char(string='Survey Types', required=True, )
    form_type_seq_no = fields.Char(string="Form ID", required=False, copy=False, readonly=False, index=True, store=True,
                                   default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        if vals.get('form_type_seq_no', _('New')) == _('New'):
            vals['form_type_seq_no'] = self.env['ir.sequence'].next_by_code('survey.form_type_sequence_no') or _('New')
        surveyform = super(SurveyTypes, self).create(vals)
        return surveyform


class SurveyUserInputLineInherit(models.Model):
    _inherit = 'survey.user_input.line'

    @api.onchange('state')
    def current_state_change(self):
        for rec in self:
            if rec.survey_id.template_seq_no == 'Temp/0012':
                rec.prepare_result(rec.survey_id, rec.question, None)



    # @api.model
    # def save_lines(self, user_input_id, question, post, answer_tag):
    #     """ Save answers to questions, depending on question type
    #
    #         If an answer already exists for question and user_input_id, it will be
    #         overwritten (in order to maintain data consistency).
    #     """
    #     if question:
    #         if question.survey_id:
    #             question.survey_id.course_count_a = question.survey_id
    #
    #     try:
    #         saver = getattr(self, 'save_line_' + question.question_type)
    #     except AttributeError:
    #         _logger.error(question.question_type + ": This type of question has no saving function")
    #         return False
    #     else:
    #         saver(user_input_id, question, post, answer_tag)


class SurveyUserInputInherit(models.Model):
    _inherit = 'survey.user_input'

    course_id = fields.Many2one('odoocms.course', related='survey_id.course_id', string='Course', store=True)
    career_id = fields.Many2one('odoocms.career', related='survey_id.career_id', string='Academic Level', store=True)
    institute_id = fields.Many2one('odoocms.institute', related='survey_id.institute_id', string='School', store=True)
    department_id = fields.Many2one('odoocms.department', related='survey_id.department_id', string='Department', store=True)
    campus_id = fields.Many2one('odoocms.campus', related='survey_id.campus_id', string='Campus', store=True)
    batch_id = fields.Many2one('odoocms.batch', related='survey_id.batch_id', string='Batch', store=True)


class SurveyAssestmentTypes(models.Model):
    _name = 'survey.course_rev.assesments_types'
    _description = 'Survey Assesments Types'

    survey_id = fields.Many2one('survey.survey', string='Survey', ondelete="cascade")
    primary_class_id = fields.Many2one(comodel_name='odoocms.class.primary', string='Primary Class', )
    assessment_name = fields.Char(string='Assessment Name', )
    count = fields.Char(string='Count', )
    # class_id = fields.Many2one('odoocms.class.primary', string='Class', )
    # template_id = fields.Many2one('odoocms.career', related='survey_id.career_id', string='Academic Level', store=True)
