# -*- coding: utf-8 -*-
import requests

from odoo import models, fields, api, _

class ResConfigInheritIAC(models.Model):
    _inherit = "res.users"

    iac_access_token = fields.Char(string="Access token")
    iac_url = fields.Char(string="Moodle URL")
    # iac_campuses = fields.Many2many('odoocms.campus', 'rel_moodle_odoocms_campus')

class IACMoodleConnector(models.Model):
    _name = 'iac.moodle.connector'
    _rec_name = 'access_token'

    access_token = fields.Char(string="Access token")
    requested_url = fields.Char(string='Requested URL')
    status = fields.Selection([
        ('disconnected', 'disconnected'),
        ('connected', 'Connected'),
    ], default='disconnected')
    # campus_ids = fields.Many2many('odoocms.campus')

    _sql_constraints = [
        ('access_token', 'unique(access_token)', "the input token already exist")]

    def moodle_login(self):
        data = {
            'wstoken': self.access_token,
            'wsfunction': 'core_user_get_users_by_field',
            'moodlewsrestformat': 'json',
            'field': 'id',
            'values[0]': '2',
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        try:
            request_data = requests.post(url=self.requested_url, params=data, headers=headers)
            if request_data.status_code not in [200]:
                raise models.ValidationError(f"You have entered Wrong url")
        except Exception as e:
            raise models.ValidationError(f"message: {e}")
        if request_data.status_code in [200] and 'errorcode' in request_data.json():
            raise models.ValidationError(f"{request_data.json()['message']}")

        self.env.user.iac_access_token = self.access_token
        self.env.user.iac_url = self.requested_url
        # self.env.user.moodle_campuses = self.campus_ids
        self.status = 'connected'
        message = '<h4 style="color:green;">"Connected" You are successfully login to moodle<h4>'
        return self.message_wizard('Login', message)


    def moodle_logout(self):
        self.env.user.iac_access_token = False
        self.env.user.iac_url = False
        # self.env.user.moodle_campuses = []
        self.status = 'disconnected'
        message = '<h4 style="color:red;">"Disconnected" You are successfully logout from moodle</h4>'
        return self.message_wizard('Logout', message)


    # To popup desired message on the screen
    def message_wizard(self, name=None, message=None):
        created_id = self.env['iac.wizard.message'].create({
            'text': (_(message))
        })
        return {
            'name': (_(name)),
            'type': 'ir.actions.act_window',
            'res_model': 'iac.wizard.message',
            'view_mode': 'form',
            'target': 'new',
            'res_id': created_id.id,
        }