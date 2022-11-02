
from odoo import api, models, fields, modules, SUPERUSER_ID, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import clean_context
from odoo.models import AbstractModel
from collections import defaultdict
import pdb


class MailActivityType(models.Model):
	_inherit = 'mail.activity.type'

	prev_function = fields.Char('Prev Code')
	post_function = fields.Char('Post Code')
	validation_function = fields.Char('Validation Code')
	cancel_function = fields.Char('Code on Cancel')
	# user_id = fields.Many2one('res.users', 'Assigned To', index=True,)
	category = fields.Selection(selection_add=[('approval', 'Approval')],string='Category')
	back_activity_type_id = fields.Many2one('mail.activity.type', string='Back Activity')
	special_state = fields.Char('Special State')
	module_category_id = fields.Many2one('ir.module.category','Module Category')
	force_prev = fields.Boolean('Prev. Activity?', compute='_is_prev_activity',store=True)

	@api.depends('back_activity_type_id')
	def _is_prev_activity(self):
		for rec in self:
			if rec.back_activity_type_id:
				rec.force_prev = True
			else:
				rec. force_prev = False


class MailActivity(models.Model):
	_inherit = 'mail.activity'

	activity_category = fields.Selection(related='activity_type_id.category', readonly=True)

	prev_function = fields.Char('Prev Code')
	post_function = fields.Char('Post Code')
	validation_function = fields.Char('Validation Code')
	cancel_function = fields.Char('Code on Cancel')
	# user_id = fields.Many2one('res.users', 'Assigned To', index=True,)

	# mail_activity_done
	active = fields.Boolean(default=True)
	done = fields.Boolean(default=False)
	state = fields.Selection(selection_add=[('done', 'Done')], compute='_compute_state')
	date_done = fields.Date('Completed Date', index=True, readonly=True,)
	special_state = fields.Char('Special State',related='activity_type_id.special_state',store=True)
	force_prev = fields.Boolean('Prev. Activity?', related='activity_type_id.force_prev', store=True)

	# back_activity_type_id = fields.Many2one('mail.activity.type', string='Back Activity Type', readonly=True)

	@api.depends('date_deadline', 'done')
	def _compute_state(self):
		super(MailActivity, self)._compute_state()
		for record in self.filtered(lambda activity: activity.done):
			record.state = 'done'

	@api.onchange('previous_activity_type_id')
	def _onchange_previous_activity_type_id(self):
		for record in self:
			if record.previous_activity_type_id.default_next_type_id:
				record.activity_type_id = record.previous_activity_type_id.default_next_type_id
				record.user_id = record.previous_activity_type_id.default_next_type_id.default_user_id or self.env.user.id

	def unlink(self):
		# self._check_access('unlink')
		for activity in self:
			if activity.date_deadline <= fields.Date.today():
				self.env['bus.bus'].sendone(
					(self._cr.dbname, 'res.partner', activity.user_id.partner_id.id),
					{'type': 'activity_updated', 'activity_deleted': True})

			record = self.env[activity.res_model].browse(activity.res_id)
			cancel_function = activity.cancel_function or activity.activity_type_id.cancel_function or False
			localdict = {'record': record}
			if cancel_function:
				safe_eval(cancel_function, localdict, mode="exec", nocopy=True)

		# self.action_feedback('Cancelled/ Rejected')
		return True

	# return super(MailActivity, self.sudo()).unlink()

	def _action_done(self, feedback=False, attachment_ids=None):
		# marking as 'done'
		messages = self.env['mail.message']
		next_activities_values = []

		# Search for all attachments linked to the activities we are about to unlink. This way, we
		# can link them to the message posted and prevent their deletion.
		attachments = self.env['ir.attachment'].search_read([
			('res_model', '=', self._name),
			('res_id', 'in', self.ids),
		], ['id', 'res_id'])

		activity_attachments = defaultdict(list)
		for attachment in attachments:
			activity_id = attachment['res_id']
			activity_attachments[activity_id].append(attachment['id'])

		for activity in self:
			# extract value to generate next activities
			if activity.force_next:
				Activity = self.env['mail.activity'].with_context(
					activity_previous_deadline=activity.date_deadline)  # context key is required in the onchange to set deadline
				vals = Activity.default_get(Activity.fields_get())

				vals.update({
					'previous_activity_type_id': activity.activity_type_id.id,
					'res_id': activity.res_id,
					'res_model': activity.res_model,
					'res_model_id': self.env['ir.model']._get(activity.res_model).id,
				})
				virtual_activity = Activity.new(vals)
				virtual_activity._onchange_previous_activity_type_id()
				virtual_activity._onchange_activity_type_id()
				next_activities_values.append(virtual_activity._convert_to_write(virtual_activity._cache))

			#Added these three lines
			activity.done = True
			activity.active = False
			activity.date_done = fields.Date.today()

			# post message on activity, before deleting it
			record = self.env[activity.res_model].browse(activity.res_id)
			record.message_post_with_view(
				'mail.message_activity_done',
				values={
					'activity': activity,
					'feedback': feedback,
					'display_assignee': activity.user_id != self.env.user
				},
				subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_activities'),
				mail_activity_type_id=activity.activity_type_id.id,
				attachment_ids=[(4, attachment_id) for attachment_id in attachment_ids] if attachment_ids else [],
			)

			# Moving the attachments in the message
			# TODO: Fix void res_id on attachment when you create an activity with an image
			# directly, see route /web_editor/attachment/add
			activity_message = record.message_ids[0]
			message_attachments = self.env['ir.attachment'].browse(activity_attachments[activity.id])
			if message_attachments:
				message_attachments.write({
					'res_id': activity_message.id,
					'res_model': activity_message._name,
				})
				activity_message.attachment_ids = message_attachments
			messages |= activity_message


		next_activities = self.env['mail.activity'].create(next_activities_values)

		# Remarked this one
		# self.unlink()  # will unlink activity, dont access `self` after that

		return messages, next_activities

	#This is to just store the feedback. For activity creation we don't use action_done() function.
	# We will create them in next pre functions.
	def action_feedback2(self, feedback=False):
		# res = super(MailActivity,self).action_feedback(feedback=feedback)
		# Changed original to avoid unlink
		message = self.env['mail.message']

		for activity in self:
			record = self.env[activity.res_model].browse(activity.res_id)
			activity.done = True
			activity.active = False
			activity.date_done = fields.Date.today()
			record.message_post_with_view(
				'mail.message_activity_done',
				values={
					'activity': activity,
					'feedback': feedback,
					'display_assignee': activity.user_id != self.env.user
				},
				subtype_id=self.env.ref('mail.mt_activities').id,
				mail_activity_type_id=activity.activity_type_id.id,
			)
			message |= record.message_ids[0]

		return message.ids and message.ids[0] or False



	def activity_format(self):
		for rec in self:
			activities = super().activity_format()
			for activity in activities:
				activity['login_user'] = rec.env.user.id
				activity['force_prev'] = rec.force_prev
			return activities


	def action_post_function(self):
		record = self.env[self.res_model].browse(self.res_id)
		localdict = {'record': record}
		post_function = self.post_function or self.activity_type_id.post_function or False
		if post_function:
			safe_eval(post_function, localdict, mode="exec", nocopy=True)

	def action_feedback_schedule_next(self, feedback=False):
		ctx = dict(
			clean_context(self.env.context),
			default_previous_activity_type_id=self.activity_type_id.id,
			activity_previous_deadline=self.date_deadline,
			default_res_id=self.res_id,
			default_res_model=self.res_model,
		)
		record = self.env[self.res_model].browse(self.res_id)
		localdict = {'record': record}
		validation_function = self.validation_function or self.activity_type_id.validation_function or False

		if validation_function:
			result = eval(validation_function)
			# safe_eval(validation_function, localdict, mode="exec", nocopy=True)
			if result:
				return {'warning': 'Activity: %s' % (result,)}

		record.write_state = self.activity_type_id.default_next_type_id.special_state
		post_function = self.post_function or self.activity_type_id.post_function or False

		if post_function:
			safe_eval(post_function, localdict, mode="exec", nocopy=True)

		force_next = self.force_next
		self.action_feedback2(feedback)  # will unlink activity, dont access self after that

		if force_next:
			Activity = self.env['mail.activity'].with_context(ctx)
			res = Activity.new(Activity.default_get(Activity.fields_get()))
			res._onchange_previous_activity_type_id()
			res._onchange_activity_type_id()
			if 'program_id' in record._fields:
				User = res.activity_type_id._get_role_users(record.program_id)
				res.user_id = User
			Activity.create(res._convert_to_write(res._cache))
			return {'info': 'Activity: %s created' % (res.activity_type_id.name,)}
		else:
			action_message = {
				'name': 'Schedule an Activity',
				'context': ctx,
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'mail.activity',
				'views': [(False, 'form')],
				'type': 'ir.actions.act_window',
				'target': 'new',
			}
			return {'action': action_message}

	def action_feedback_schedule_prev(self, feedback=False):
		ctx = dict(
			clean_context(self.env.context),
			default_activity_type_id=self.activity_type_id.back_activity_type_id.id,
			activity_previous_deadline=self.date_deadline,
			default_res_id=self.res_id,
			default_res_model= self.res_model,
			default_user_id= self.activity_type_id.back_activity_type_id.default_user_id.id or self.env.user.id
		)

		record = self.env[self.res_model].browse(self.res_id)
		record.write_state = self.activity_type_id.back_activity_type_id.special_state

		localdict = {'record': record}
		prev_function = self.prev_function or self.activity_type_id.prev_function or False

		force_prev = self.activity_type_id.back_activity_type_id
		self.action_feedback2(feedback)  # will unlink activity, dont access self after that
		if prev_function:
			safe_eval(prev_function, localdict, mode="exec", nocopy=True)

		if force_prev:
			Activity = self.env['mail.activity'].with_context(ctx)
			res = Activity.new(Activity.default_get(Activity.fields_get()))
			# res._onchange_previous_activity_type_id()
			res._onchange_activity_type_id()
			if 'program_id' in record._fields:
				User = res.activity_type_id._get_role_users(record.program_id)
				res.user_id = User
			Activity.create(res._convert_to_write(res._cache))
			return {'info': 'Activity: Turned back to %s ' % (res.activity_type_id.name,)}
		return {'info': 'Activity: Send back Successfully'}


# mail_activity_done
class ResUsers(models.Model):
	_inherit = 'res.users'

	# @api.model
	# def create(self, vals):
	# 	print(11111111111111111111111, vals)
	# 	if vals['user_type'] == 'public':
	# 		self.env.ref("aarsol_activity.signup_email_template").send_mail(self.id)
	# 	return super(ResUsers, self).create(vals)

	# res = super(ResUsers, self).create(vals)
	# login_id = vals['login']
	# if res:
	# 	res_user = self.env['res.users'].search([('login', '=', login_id)])
	# 	if res_user.user_type == 'public':
	# 		self.env.ref("aarsol_activity.signup_email_template").send_mail(self.id)
	# return res

	# if vals.get('survey_seq_no', _('New')) == _('New') and vals['type'] == 'survey':
		# 	vals['survey_seq_no'] = self.env['ir.sequence'].next_by_code('survey.survey_sequence_num') or _('New')
		# elif vals.get('survey_seq_no', _('New')) == _('New') and vals['type'] == 'template':
		# 	vals['template_seq_no'] = self.env['ir.sequence'].next_by_code('survey.temp_sequence_num') or _('New')

	@api.model
	def systray_get_activities(self):
		# Here we totally override the method. Not very nice, but
		# we should perhaps ask Odoo to add a hook here.
		query = """SELECT m.id, count(*), act.res_model as model,
						CASE
							WHEN %(today)s::date - act.date_deadline::date = 0 Then 'today'
							WHEN %(today)s::date - act.date_deadline::date > 0 Then 'overdue'
							WHEN %(today)s::date - act.date_deadline::date < 0 Then 'planned'
						END AS states
					FROM mail_activity AS act
					JOIN ir_model AS m ON act.res_model_id = m.id
					WHERE user_id = %(user_id)s AND act.done = False
					GROUP BY m.id, states, act.res_model;
				"""
		self.env.cr.execute(query, {
			'today': fields.Date.context_today(self),
			'user_id': self.env.uid,
		})
		activity_data = self.env.cr.dictfetchall()
		model_ids = [a['id'] for a in activity_data]
		model_names = {n[0]: n[1] for n in self.env['ir.model'].browse(model_ids).name_get()}

		user_activities = {}
		for activity in activity_data:
			if not user_activities.get(activity['model']):
				user_activities[activity['model']] = {
					'name': model_names[activity['id']],
					'model': activity['model'],
					'icon': modules.module.get_module_icon(self.env[activity['model']]._original_module),
					'total_count': 0, 'today_count': 0,
					'overdue_count': 0, 'planned_count': 0,
					'type': 'activity',
				}
			user_activities[activity['model']]['%s_count' % activity['states']] += activity['count']
			if activity['states'] in ('today', 'overdue'):
				user_activities[activity['model']]['total_count'] += activity['count']

		return list(user_activities.values())


