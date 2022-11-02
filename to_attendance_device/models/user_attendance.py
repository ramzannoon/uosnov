import logging

from odoo import models, fields, api, _
from odoo import tools

_logger = logging.getLogger(__name__)


class UserAttendance(models.Model):
    _name = 'user.attendance'
    _description = 'User Attendance'
    _order = 'timestamp DESC, user_id, status, attendance_state_id, device_id'

    device_id = fields.Many2one('attendance.device', string='Attendance Device', required=True, ondelete='restrict', index=True)
    user_id = fields.Many2one('attendance.device.user', string='Device User', required=True, ondelete='cascade', index=True)
    timestamp = fields.Datetime(string='Timestamp', required=True, index=True)
    status = fields.Integer(string='Device Attendance State', required=True,
                            help='The state which is the unique number stored in the device to'
                            ' indicate type of attendance (e.g. 0: Checkin, 1: Checkout, etc)')
    attendance_state_id = fields.Many2one('attendance.state', string='Odoo Attendance State',
                                          help='This technical field is to map the attendance'
                                          ' status stored in the device and the attendance status in Odoo', required=True, index=True)
    activity_id = fields.Many2one('attendance.activity', related='attendance_state_id.activity_id', store=True, index=True)
    hr_attendance_id = fields.Many2one('hr.attendance', string='HR Attendance', ondelete='set null',
                                       help='The technical field to link Device Attendance Data with Odoo\' Attendance Data', index=True)

    type = fields.Selection([('checkin', 'Check-in'),
                            ('checkout', 'Check-out')], string='Activity Type', related='attendance_state_id.type', store=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', related='user_id.employee_id', store=True, index=True)
    
    # TODO: remove this field `valid` in master/14+ as it is useless
    valid = fields.Boolean(string='Valid Attendance', index=True, readonly=True, default=False,
                           help="This field is to indicate if this attendance record is valid for HR Attendance Synchronization."
                           " E.g. The Attendances with Check out prior to Check in or the Attendances for users without employee"
                           " mapped will not be valid.")

    _sql_constraints = [
        ('unique_user_id_device_id_timestamp',
         'UNIQUE(user_id, device_id, timestamp)',
         "The Timestamp and User must be unique per Device"),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        attendances = super(UserAttendance, self).create(vals_list)
        attendances._update_valid()
        return attendances

    @api.constrains('status', 'attendance_state_id')
    def constrains_status_attendance_state_id(self):
        for r in self:
            if r.status != r.attendance_state_id.code:
                raise(_('Attendance Status conflict! The status number from device must match the attendance status defined in Odoo.'))

    def _update_valid(self):
        self_sorted = self.sorted('timestamp', reverse=True)
        all_att = self.env['user.attendance'].search([
            ('employee_id', 'in', self.employee_id.ids),
            ('timestamp', '<', self_sorted[-1:].timestamp),
            ('activity_id', 'in', self.activity_id.ids)])
        for r in self:
            prev_att = all_att.filtered(
                lambda att: \
                    att.employee_id == r.employee_id \
                    and att.timestamp < r.timestamp \
                    and att.activity_id == r.activity_id
                    ).sorted('timestamp')[-1:]
            if not prev_att:
                r.valid = True if r.type == 'checkin' else False
            else:
                r.valid = True if prev_att.type != r.attendance_state_id.type else False

    def _prepare_last_hr_attendance_domain(self):
        self.ensure_one()
        return [
            ('employee_id', '=', self.employee_id.id),
            ('check_in', '<=', self.timestamp),
            '|', ('activity_id', '=', False), ('activity_id', '=', self.activity_id.id),
            ]

    def _get_last_hr_attendance(self):
        self.ensure_one()
        return self.env['hr.attendance'].search(self._prepare_last_hr_attendance_domain(), limit=1, order='check_in DESC')

    def _prepare_hr_attendance_vals(self):
        return {
            'employee_id': self.employee_id.id,
            'check_in': self.timestamp,
            'checkin_device_id': self.device_id.id,
            'activity_id': self.activity_id.id,
            }

    def _create_hr_attendance(self):
        vals_list = []
        for r in self:
            vals_list.append(r._prepare_hr_attendance_vals())
        return self.env['hr.attendance'].create(vals_list)

    def _sync_attendance(self):
        error_msg = {}
        for attendance_activity in self.env['attendance.activity'].search([]):
            for employee in self.employee_id:
                unsync_user_attendances = self.filtered(lambda uatt: uatt.employee_id == employee and uatt.activity_id == attendance_activity).sorted('timestamp')
                for uatt in unsync_user_attendances:
                    with self.env.cr.savepoint(), tools.mute_logger('odoo.sql_db'):
                        last_hr_attendance = uatt._get_last_hr_attendance()
                        try:
                            uatt_update = False
                            if uatt.type == 'checkin':
                                if not last_hr_attendance or (last_hr_attendance.check_out and uatt.timestamp > last_hr_attendance.check_out):
                                    last_hr_attendance = uatt._create_hr_attendance()
                                    uatt_update = True
                            else:
                                if last_hr_attendance and not last_hr_attendance.check_out and uatt.timestamp >= last_hr_attendance.check_in:
                                    last_hr_attendance.with_context(not_manual_check_out_modification=True).write({
                                        'check_out': uatt.timestamp,
                                        'checkout_device_id': uatt.device_id.id
                                        })
                                    uatt_update = True
                            if uatt_update:
                                uatt.write({
                                    'hr_attendance_id': last_hr_attendance.id
                                    })
                        except Exception as e:
                            error_msg.setdefault(uatt.device_id, [])
                            msg = str(e)
                            if msg not in error_msg[uatt.device_id]:
                                error_msg[uatt.device_id].append(str(e))
        if bool(error_msg):
            for device, msg_list in error_msg.items():
                device.message_post(body="<ol>%s</ol>" % "".join(["<li>%s</li>" % msg for msg in msg_list]))

    def action_sync_attendance(self):
        self._sync_attendance()

    @api.model
    def _prepare_unsynch_data_domain(self):
        return [
            ('hr_attendance_id', '=', False),
            ('employee_id', '!=', False)
            ]

    @api.model
    def _cron_synch_hr_attendance(self):
        unsync_data = self.env['user.attendance'].search(self._prepare_unsynch_data_domain())
        unsync_data._sync_attendance()
