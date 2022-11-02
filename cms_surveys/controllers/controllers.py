
import json
import logging
import werkzeug
from odoo import fields, http, _
import odoo.modules.registry
from odoo.addons.base.models.ir_ui_view import keep_query
import json
import logging
import werkzeug

from datetime import datetime
from dateutil.relativedelta import relativedelta
from math import ceil
from odoo.addons.base.models.ir_ui_view import keep_query
from odoo.exceptions import UserError
from odoo.http import request, content_disposition
from odoo.tools import ustr
import odoo.addons.survey.controllers.main as Survey
# odoo.addons.portal.controllers.portal
_logger = logging.getLogger(__name__)

from odoo import fields, http, _
from odoo.http import route, request, content_disposition
from odoo.addons.survey.controllers.main import Survey



class Surveys(Survey):
# class Survey(http.Controller):

    @http.route('/survey/submit1/<string:survey_token>/<string:answer_token>', type='http', methods=['POST'], auth='public', website=True)
    def survey_submit(self, survey_token, answer_token, **post):
        """ Submit a page from the survey.
        This will take into account the validation errors and store the answers to the questions.
        If the time limit is reached, errors will be skipped, answers wil be ignored and
        survey state will be forced to 'done'

        TDE NOTE: original comment: # AJAX submission of a page -> AJAX / http ?? """
        access_data = Survey._get_access_data(self,survey_token, answer_token, ensure_token=True)
        # access_data = self._get_access_data(survey_token, answer_token, ensure_token=True)
        if access_data['validity_code'] is not True:
            return {}
        # if post['course_count_a']:
        if post.get('course_count_a', False):
            access_data['survey_sudo'].course_count_a = post['course_count_a']
        if post.get('course_count_b_plus', False):
            access_data['survey_sudo'].course_count_b_plus = post['course_count_b_plus']
        if post.get('course_count_b', False):
            access_data['survey_sudo'].course_count_b = post['course_count_b']
        if post.get('course_count_c_plus', False):
            access_data['survey_sudo'].course_count_c_plus = post['course_count_c_plus']
        if post.get('course_count_c', False):
            access_data['survey_sudo'].course_count_c = post['course_count_c']
        if post.get('course_count_d_plus', False):
            access_data['survey_sudo'].course_count_d_plus = post['course_count_d_plus']
        if post.get('course_count_d', False):
            access_data['survey_sudo'].course_count_d = post['course_count_d']
        if post.get('course_count_f', False):
            access_data['survey_sudo'].course_count_f = post['course_count_f']
        if post.get('course_count_w', False):
            access_data['survey_sudo'].course_count_w = post['course_count_w']
        if post.get('course_count_i', False):
            access_data['survey_sudo'].course_count_i = post['course_count_i']

        if access_data['survey_sudo']['class_assessments']:
            for assessment in access_data['survey_sudo'].class_assessments:
                if assessment.assessment_name in post:
                    assessment.count = post[assessment.assessment_name]
                # else:
                #     assessment.count = 0

        survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']
        if not answer_sudo.test_entry and not survey_sudo._has_attempts_left(answer_sudo.partner_id, answer_sudo.email, answer_sudo.invite_token):
            # prevent cheating with users creating multiple 'user_input' before their last attempt
            return {}

        if survey_sudo.questions_layout == 'page_per_section':
            page_id = int(post['page_id'])
            questions = request.env['survey.question'].sudo().search([('survey_id', '=', survey_sudo.id), ('page_id', '=', page_id)])
            # we need the intersection of the questions of this page AND the questions prepared for that user_input
            # (because randomized surveys do not use all the questions of every page)
            questions = questions & answer_sudo.question_ids
            page_or_question_id = page_id
        elif survey_sudo.questions_layout == 'page_per_question':
            question_id = int(post['question_id'])
            questions = request.env['survey.question'].sudo().browse(question_id)
            page_or_question_id = question_id
        else:
            questions = survey_sudo.question_ids
            questions = questions & answer_sudo.question_ids

        errors = {}
        # Answer validation
        if not answer_sudo.is_time_limit_reached:
            for question in questions:
                answer_tag = "%s_%s" % (survey_sudo.id, question.id)
                errors.update(question.validate_question(post, answer_tag))

        ret = {}
        if len(errors):
            # Return errors messages to webpage
            ret['errors'] = errors
        else:
            if not answer_sudo.is_time_limit_reached:
                for question in questions:
                    answer_tag = "%s_%s" % (survey_sudo.id, question.id)
                    request.env['survey.user_input_line'].sudo().save_lines(answer_sudo.id, question, post, answer_tag)

            go_back = False
            vals = {}
            if answer_sudo.is_time_limit_reached or survey_sudo.questions_layout == 'one_page':
                answer_sudo._mark_done()
            elif 'button_submit' in post:
                go_back = post['button_submit'] == 'previous'
                next_page, last = request.env['survey.survey'].next_page_or_question(answer_sudo, page_or_question_id, go_back=go_back)
                vals = {'last_displayed_page_id': page_or_question_id}

                if next_page is None and not go_back:
                    answer_sudo._mark_done()
                else:
                    vals.update({'state': 'skip'})

            if 'breadcrumb_redirect' in post:
                ret['redirect'] = post['breadcrumb_redirect']
            else:
                if vals:
                    answer_sudo.write(vals)

                ret['redirect'] = '/survey/fill/%s/%s' % (survey_sudo.access_token, answer_token)
                if go_back:
                    ret['redirect'] += '?prev=prev'

        return json.dumps(ret)

