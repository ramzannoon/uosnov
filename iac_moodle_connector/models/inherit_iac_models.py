# -*- coding: utf-8 -*-
import requests
from random import randint
from odoo import models, fields, api, _
from datetime import datetime


# # &&&&&&& INHERIT CAMPUS TO ADD MOODLE REQUIRED FIELDS &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
class InheritIacCampus(models.Model):
    _inherit = 'odoocms.campus'

    iac_moodle_id = fields.Char(string='Moodle ID')
    iac_sync_state = fields.Selection([('sync', 'Sync'), ('not_sync', 'Unsync')], default='not_sync')

    def sync_campus_to_moodle(self):
        if self.env.user.iac_access_token is False or self.env.user.iac_url is False:
            raise models.ValidationError("You are not login to moodle. Plz check it")
        for record in self:
            if record.iac_moodle_id is False:
                url = self.env.user.iac_url
                data = {
                    'wstoken': self.env.user.iac_access_token,
                    'wsfunction': 'core_course_create_categories',
                    'moodlewsrestformat': 'json', }
                data['categories[0][parent]'] = '0'
                data['categories[0][name]'] = record.name
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
                try:
                    request_data = requests.post(url=url, params=data, headers=headers)
                    record.iac_moodle_id = str(request_data.json()[0].get('id'))
                    record.iac_sync_state = 'sync'
                except Exception as e:
                    raise models.ValidationError(
                        f"Something went wrong for ID {record.id}, {e}")


# # &&&&&&& INHERIT CAMPUS TO ADD MOODLE REQUIRED FIELDS &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
class InheritIacSchool(models.Model):
    _inherit = 'odoocms.institute'

    iac_moodle_id = fields.Char(string='Moodle ID')
    iac_sync_state = fields.Selection([('sync', 'Sync'), ('not_sync', 'Unsync')], default='not_sync')

    def sync_institute_to_moodle(self):
        if self.env.user.iac_access_token is False or self.env.user.iac_url is False:
            raise models.ValidationError("You are not login to moodle. Plz check it")
        for record in self:
            if record.iac_moodle_id is False:
                url = self.env.user.iac_url
                data = {
                    'wstoken': self.env.user.iac_access_token,
                    'wsfunction': 'core_course_create_categories',
                    'moodlewsrestformat': 'json', }
                data['categories[0][parent]'] = record.campus_id.iac_moodle_id
                data['categories[0][name]'] = record.name
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
                try:
                    request_data = requests.post(url=url, params=data, headers=headers)
                    record.iac_moodle_id = str(request_data.json()[0].get('id'))
                    record.iac_sync_state = 'sync'
                except Exception as e:
                    raise models.ValidationError(
                        f"Something went wrong for ID {record.id}, {e}")


class InheritIacDepartment(models.Model):
    _inherit = 'odoocms.department'

    iac_moodle_id = fields.Char(string='Moodle ID')
    iac_sync_state = fields.Selection([('sync', 'Sync'), ('not_sync', 'Unsync')], default='not_sync')
    acade_level_moodle_id = fields.Char()

    def sync_department_to_moodle(self):
        if self.env.user.iac_access_token is False or self.env.user.iac_url is False:
            raise models.ValidationError("You are not login to moodle. Plz check it")
        for record in self:
            if record.iac_moodle_id is False:
                url = self.env.user.iac_url
                data = {
                    'wstoken': self.env.user.iac_access_token,
                    'wsfunction': 'core_course_create_categories',
                    'moodlewsrestformat': 'json', }
                data['categories[0][parent]'] = record.institute_id.iac_moodle_id
                data['categories[0][name]'] = record.name
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
                try:
                    request_data = requests.post(url=url, params=data, headers=headers)
                    record.iac_moodle_id = str(request_data.json()[0].get('id'))
                    record.iac_sync_state = 'sync'
                except Exception as e:
                    raise models.ValidationError(
                        f"Something went wrong for ID {record.id}, {e}")


# &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& INHERIT PROGRAM  &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
class InheritiACAcademicProgram(models.Model):
    _inherit = 'odoocms.program'

    iac_moodle_id = fields.Char(string='Moodle ID')
    iac_sync_state = fields.Selection([('sync', 'Sync'), ('not_sync', 'Unsync')], default='not_sync')

    def sync_program_to_moodle(self):
        if self.env.user.iac_access_token is False or self.env.user.iac_url is False:
            raise models.ValidationError("You are not login to moodle. Plz check it")
        for record in self:
            if record.department_id.acade_level_moodle_id is False:
                url = self.env.user.iac_url
                data = {
                    'wstoken': self.env.user.iac_access_token,
                    'wsfunction': 'core_course_create_categories',
                    'moodlewsrestformat': 'json', }
                data['categories[0][parent]'] = record.department_id.iac_moodle_id
                data['categories[0][name]'] = record.career_id.name
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
                try:
                    request_data = requests.post(url=url, params=data, headers=headers)
                    record.department_id.acade_level_moodle_id = str(request_data.json()[0].get('id'))
                except Exception as e:
                    raise models.ValidationError(
                        f"Something went wrong for ID {record.id}, {e}")

            if record.iac_moodle_id is False:
                url = self.env.user.iac_url
                data = {
                    'wstoken': self.env.user.iac_access_token,
                    'wsfunction': 'core_course_create_categories',
                    'moodlewsrestformat': 'json', }
                data['categories[0][parent]'] = record.department_id.acade_level_moodle_id
                data['categories[0][name]'] = record.name
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
                try:
                    request_data = requests.post(url=url, params=data, headers=headers)
                    record.iac_moodle_id = str(request_data.json()[0].get('id'))
                    record.iac_sync_state = 'sync'
                except Exception as e:
                    raise models.ValidationError(
                        f"Something went wrong for ID {record.id}, {e}")
# &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& INHERIT BATCHES  &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
class InheritiACBaches2(models.Model):
    _inherit = 'odoocms.batch'

    iac_moodle_id = fields.Char(string='Moodle ID')
    iac_sync_state = fields.Selection([('sync', 'Sync'), ('not_sync', 'Unsync')], default='not_sync')

    def sync_batch_to_moodle(self):
        if self.env.user.iac_access_token is False or self.env.user.iac_url is False:
            raise models.ValidationError("You are not login to moodle. Plz check it")
        for record in self:
            if record.iac_moodle_id is False:
                url = self.env.user.iac_url
                data = {
                    'wstoken': self.env.user.iac_access_token,
                    'wsfunction': 'core_course_create_categories',
                    'moodlewsrestformat': 'json', }
                data['categories[0][parent]'] = record.program_id.iac_moodle_id
                data['categories[0][name]'] = record.name
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
                try:
                    request_data = requests.post(url=url, params=data, headers=headers)
                    record.iac_moodle_id = str(request_data.json()[0].get('id'))
                    record.iac_sync_state = 'sync'
                except Exception as e:
                    raise models.ValidationError(
                        f"Something went wrong for ID {record.id}, {e}")

# &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& INHERIT CLASSES  &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
class InheritiACComponentClasses(models.Model):
    _inherit = 'odoocms.class'

    course_moodle_id = fields.Char(string='Course Moodle Id')
    course_short_name = fields.Char(compute='_compute_course_short_name', store=True)
    campus_id = fields.Many2one('odoocms.campus', related='primary_class_id.campus_id', store=True)
    # section_sync_state = fields.Selection([('sync', 'Sync'), ('not_sync', 'Unsync')], default='not_sync')
    section_related = fields.Char(related='primary_class_id.section_id.batch_section_moodle_id')
    # section_sync_state = fields.Char(compute='_compute_section_sync_state', store=True)
    course_sync_state = fields.Selection([('sync', 'Sync'), ('not_sync', 'Unsync')], default='not_sync')

    @api.depends('code')
    def _compute_course_short_name(self):
        for rec in self:
            if rec.course_short_name is False:
                rec.course_short_name = rec.name[0:3] + rec.primary_class_id.section_id.name[
                                                        -2:] + rec.primary_class_id.section_id.batch_id.name[0:3] + str(
                    randint(1, 100))
    #
    # @api.depends('section_related')
    # def _compute_section_sync_state(self):
    #     for rec in self:
    #         if rec.section_related is not False:
    #             self.section_sync_state = 'sync'
    #         else:
    #             self.section_sync_state = 'not_sync'

    def sync_sections_in_moodle(self):
        if self.env.user.iac_access_token is False or self.env.user.iac_url is False:
            raise models.ValidationError("You are not login to moodle. Plz check it")
        for record in self:
            if record.primary_class_id.section_id.batch_section_moodle_id is False:
                url = self.env.user.iac_url
                data = {
                    'wstoken': self.env.user.iac_access_token,
                    'wsfunction': 'core_course_create_categories',
                    'moodlewsrestformat': 'json', }
                data['categories[0][parent]'] = record.primary_class_id.section_id.batch_id.iac_moodle_id
                data['categories[0][name]'] = record.primary_class_id.section_id.name
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
                try:
                    request_data = requests.post(url=url, params=data, headers=headers)
                    record.primary_class_id.section_id.batch_section_moodle_id = request_data.json()[0].get('id')
                except Exception as e:
                    raise models.ValidationError(
                        f"Something went wrong for ID {record.id}, {e}")

    def sync_courses_in_moodle(self):
        if self.env.user.iac_access_token is False or self.env.user.iac_url is False:
            raise models.ValidationError("You are not login to moodle. Plz check it")
        for record in self:
            if record.course_moodle_id is False:
                if record.primary_class_id.section_id.batch_section_moodle_id is False:
                    raise models.ValidationError(
                        f"Course is not created in ID {record.id} due to this Parent category is not set OR have no moodle id.")

                url = self.env.user.iac_url
                data = {
                    'wstoken': '37339b53a23774174f33efe970130eb0',
                    'wsfunction': 'core_course_create_courses',
                    'moodlewsrestformat': 'json',
                    'courses[0][fullname]': record.course_id.name,
                    'courses[0][shortname]': record.course_short_name,
                    'courses[0][categoryid]': record.primary_class_id.section_id.batch_section_moodle_id,
                }
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
                try:
                    request_data = requests.post(url=url, params=data, headers=headers)
                    record.course_moodle_id = str(request_data.json()[0].get('id'))
                except Exception as e:
                    raise models.ValidationError(
                        f"Something went wrong for ID {record.id}, {e}")

#

class InheritiACBatchSection(models.Model):
    _inherit = 'odoocms.batch.section'

    batch_section_moodle_id = fields.Char(string='Moodle Id', help="this is moodle record id of the current record")

class InheritiACStudent(models.Model):
    _inherit = 'odoocms.student'

    moodle_student_id = fields.Char(string='Moodle Id', help="this is moodle record id of the current record")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    # city_id = fields.Many2one('odoocms.city', related='campus_id.moodle_city_id', store=True)