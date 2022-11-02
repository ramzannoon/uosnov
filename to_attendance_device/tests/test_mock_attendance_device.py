import pytz
from unittest.mock import patch
from psycopg2 import IntegrityError

from odoo import fields
from odoo.tools import mute_logger
from odoo.tests import SavepointCase
from odoo.tests import tagged
from odoo.exceptions import ValidationError, UserError

from ..pyzk.zk.base import Attendance, Finger, ZK
from ..pyzk.zk.user import User
from ..pyzk.zk.exception import ZKErrorConnection, ZKConnectionUnauthorized, ZKErrorResponse, ZKNetworkError

class ZkDeviceMock():
    users = [User(uid=1, name='test', user_id=1, privilege=1)]
    attendances = [Attendance(user_id=1, timestamp=fields.Datetime.now(), status=1, punch=0, uid=1)]
    fingers = [Finger(uid=1, fid=1, valid=1, template=b"J\xc7SS21\x00")]
        
    @classmethod
    def _connect(cls, *arg, **kargs):
        return True
    
    @classmethod
    def _disconnect(cls, *arg, **kargs):
        pass
    
    @classmethod
    def _enable_device(cls, *arg, **kargs):
        return True
    
    @classmethod
    def _disable_device(cls, *arg, **kargs):
        return True
    
    @classmethod
    def _get_firmware_version(cls, *arg, **kargs):
        return 'mock_firmware'
    
    @classmethod
    def _get_serialnumber(cls, *arg, **kargs):
        return 'mock_serialnumber'
    
    @classmethod
    def _get_platform(cls, *arg, **kargs):
        return 'mock_platform'
    
    @classmethod
    def _get_fp_version(cls, *arg, **kargs):
        return 'mock_fp_version'
    
    @classmethod
    def _get_device_name(cls, *arg, **kargs):
        return 'mock_device_name'

    @classmethod
    def _get_workcode(cls, *arg, **kargs):
        return 'mock_workcode'
    
    @classmethod
    def _get_oem_vendor(cls, *arg, **kargs):
        return 'mock_oem_vender'
    
    @classmethod
    def _get_time(cls, *arg):
        return fields.Datetime.now()
    
    @classmethod
    def _get_users(cls, *arg):
        return cls.users
    
    @classmethod
    def _set_user(cls, uid=None, name='', privilege=0, password='', group_id='', user_id='', card=0, *arg, **kargs):
        cls.users.append(User(uid=uid, name=name, user_id=user_id, privilege=privilege))
        
    @classmethod
    def _delete_user(cls, uid, user_id, *arg, **kargs):
        for user in cls.users:
            if user.uid == uid and user.user_id == user_id:
                cls.users.remove(user)
                break
            
    @classmethod
    def _save_user_template(cls, user, fingers, *arg, **kargs):
        user_existing = False
        for u in cls.users:
            if user.uid == u.uid and user.user_id == u.user_id:
                user_existing = True
                break
        if not user_existing:
            cls.users.append(user)
        for finger in fingers:
            finger_existing = False
            for f in cls.fingers:
                if finger.uid == f.uid and finger.fid == f.fid:
                    finger_existing = True
                    break
            if not finger_existing:
                cls.fingers.append(finger)
                
    @classmethod               
    def _get_templates(cls, *arg, **kargs):
        return cls.fingers
    
    @classmethod
    def _get_attendance(cls, *arg, **kargs):
        return cls.attendances
    
    @classmethod
    def _clear_attendance(cls, *arg, **kargs):
        cls.attendances.clear()
        
    @classmethod
    def _get_next_uid(cls, *arg, **kargs):
        max_uid = 0
        for user in cls.users:
            if user.uid > max_uid: max_uid = user.uid
        return max_uid + 1
        
    @classmethod
    def _restart(cls, *arg, **kargs):
        raise ZKErrorConnection("instance are not connected.")
        
    @classmethod
    def _clear_data(cls, *arg, **kargs):
        raise ZKErrorConnection("instance are not connected.")

@tagged('post_install', '-at_install')
@patch.object(ZK, 'connect', ZkDeviceMock._connect)
@patch.object(ZK, 'disconnect', ZkDeviceMock._disconnect)
@patch.object(ZK, 'enable_device', ZkDeviceMock._enable_device)
@patch.object(ZK, 'disable_device', ZkDeviceMock._disable_device) 
@patch.object(ZK, 'get_users', ZkDeviceMock._get_users) 
@patch.object(ZK, 'set_user', ZkDeviceMock._set_user)
@patch.object(ZK, 'delete_user', ZkDeviceMock._delete_user)
@patch.object(ZK, 'save_user_template', ZkDeviceMock._save_user_template)
@patch.object(ZK, 'get_templates', ZkDeviceMock._get_templates)
@patch.object(ZK, 'get_attendance', ZkDeviceMock._get_attendance)
@patch.object(ZK, 'clear_attendance', ZkDeviceMock._clear_attendance)
@patch.object(ZK, 'get_next_uid', ZkDeviceMock._get_next_uid)
class TestAttendanceDeviceMock(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.registry.enter_test_mode(cls.cr)
        cls.attendance_device_location = cls.env['attendance.device.location'].create({
            'name': 'test_attendance_device_location',
            })
        cls.attendance_device = cls.env['attendance.device'].create({
            'name': 'test_attendance_device',
            'ip': 'ip_test',
            'port': 1111,
            'timeout': 20,
            'password':'1234',
            'location_id': cls.attendance_device_location.id,
            })

    @classmethod
    def tearDownClass(cls):
        cls.registry.leave_test_mode()
        super().tearDownClass()
    
    # =================Test functional==================
    # 7 Lấy thông tin thiết bị - Các thông tin kết nối hợp lệ
    @patch.object(ZK, 'get_firmware_version', ZkDeviceMock._get_firmware_version)
    @patch.object(ZK, 'get_serialnumber', ZkDeviceMock._get_serialnumber)
    @patch.object(ZK, 'get_platform', ZkDeviceMock._get_platform)
    @patch.object(ZK, 'get_fp_version', ZkDeviceMock._get_fp_version)
    @patch.object(ZK, 'get_device_name', ZkDeviceMock._get_device_name)
    @patch.object(ZK, 'get_workcode', ZkDeviceMock._get_workcode)      
    @patch.object(ZK, 'get_oem_vendor', ZkDeviceMock._get_oem_vendor)   
    def test_01_action_device_information(self):
        self.attendance_device.action_device_information()

        self.assertRecordValues(
            self.attendance_device,
            [
                {
                    'firmware_version': ZkDeviceMock._get_firmware_version(),
                    'serialnumber': ZkDeviceMock._get_serialnumber(),
                    'platform': ZkDeviceMock._get_platform(),
                    'fingerprint_algorithm': ZkDeviceMock._get_fp_version(),
                    'device_name': ZkDeviceMock._get_device_name(),
                    'work_code': ZkDeviceMock._get_workcode(),
                    'oem_vendor': ZkDeviceMock._get_oem_vendor(),
                    }
                ]
            )

    # 9. Hiển thị datetime của máy chấm công 
    @patch.object(ZK, 'get_time', ZkDeviceMock._get_time) 
    def test_02_action_show_time(self):
        with self.assertRaises(ValidationError, msg = "test_action_show_time passed"):
            self.attendance_device.action_show_time()
             
    # 10. Restart máy chấm công từ xa 
    @patch.object(ZK, 'restart', ZkDeviceMock._restart)
    @mute_logger('odoo.addons.to_attendance_device.models.attendance_device', 'ZKErrorConnection')
    def test_03_action_restart(self):
        with self.assertRaises(ValidationError, msg = "test_action_restart passed"):
            self.attendance_device.action_restart()
    
    # 11. Clear attendance data
    @mute_logger('odoo.addons.to_attendance_device.models.attendance_device', 'ZKErrorConnection')
    @patch.object(ZK, 'clear_data', ZkDeviceMock._clear_data)
    def test_04_action_clear_data(self):
        with self.assertRaises(ValidationError, msg = "test_action_clear_data passed"):
            self.attendance_device.action_clear_data()
    
    # 12. Download user 
    def test_05_action_user_download(self):
        self.attendance_device.action_user_download()
        self.assertEqual(self.attendance_device.device_users_count, 1, "test_action_user_download passed")
       
    # 12. Upload users  
    def test_06_action_user_upload(self):
        self.attendance_device.action_user_upload()
        self.assertEqual(len(ZkDeviceMock.users), 3, "test_action_user_upload passed")
   
    # 13. Map employee
    def test_07_action_employee_map(self):
        self.hr_empployee = self.env['hr.employee'].create({
            'name': 'Test',
            })
        self.attendance_device.action_employee_map()
        self.assertEqual(self.attendance_device.mapped_employees_count, 3, "test_action_employee_map passed")
    
    # 14. Download fingers template
    def test_08_action_finger_template_download(self):
        self.attendance_device.action_finger_template_download()
        self.attendance_device._compute_total_finger_template_records()
        self.assertEqual(self.attendance_device.total_finger_template_records, 1, "test_action_finger_template_download passed")
    
    # 15. Download attendances
    def test_09_action_attendance_download(self):
        self.attendance_device.action_attendance_download()
        self.attendance_device._compute_total_attendance_records()
        self.assertEqual(self.attendance_device.total_att_records, 1, "test_action_attendance_download passed")
        
    # 20. Upload nhân viên lên thiết bị chấm công:
    def test_10_action_employee_upload_to_device(self):
        employee_to_upload = self.env['hr.employee'].search([], limit=1)
        employee_upload_wizard = self.env['employee.upload.wizard'].create({
            'device_ids': (self.attendance_device.id,),
            'employee_ids': (employee_to_upload.id,)
            })
        employee_upload_line = self.env['employee.upload.line'].create({
            'wizard_id': employee_upload_wizard.id,
            'device_id': self.attendance_device.id,
            'employee_id': employee_to_upload.id,
            })
        employee_upload_wizard.action_employee_upload()
        self.assertEqual(self.attendance_device.device_users_count, 4, "test_action_employee_upload passed passed")

        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            employee_upload_wizard.action_employee_upload()
    
    # 16. Synchronize attendance
    def test_11_sync_attendance(self):
        self.attendance_device.create_employee_during_mapping = True
        self.test_09_action_attendance_download()
        total_hr_attendances = self.env['hr.attendance'].search_count([])
        attendance_wizard = self.env['attendance.wizard'].create({})
        attendance_wizard.cron_sync_attendance()
        self.assertEqual(self.env['hr.attendance'].search_count([]), 13, "test_sync_attendance passed")

    # ============ Tester bổ sung testcase: ============    
    # 14. Tạo mới 1 thiết bị chấm công có cùng thông tin IP, Port nhưng khác địa điểm với 1 thiết bị chấm công đang sử dụng
    def test_12_new_device_dupplicate_ip_port_location(self):
        new_att_device_location = self.env['attendance.device.location'].create({
            'name': 'new_att_device_location',
            })
        new_att_device = self.env['attendance.device'].create({
            'name': 'new_att_device',
            'ip': self.attendance_device.ip,
            'port': self.attendance_device.port,
            'timeout': 20,
            'password':'1234',
            'location_id': new_att_device_location.id,
            })
        self.assertEqual(self.env['attendance.device'].search_count([]), 2, "test_new_device_dupplicate_ip_port_location passed")        
        
    # 15. Xóa 1 thiết bị không ở trạng thái draft: Confirm/cancelled
    def test_13_delete_device_not_in_draft(self):
        with self.assertRaises(UserError, msg = "test_delete_device_not_in_draft passed"):
            self.attendance_device.state = 'confirmed'
            self.attendance_device.unlink()

    # 16. Xóa 1 thiết bị ở trạng thái draft và chưa có dữ liệu chấm công
    def test_14_delete_device_in_draft_no_attendance_data(self):
        new_att_device = self.env['attendance.device'].create({
            'name': 'new_att_device',
            'ip': 'new_ip',
            'port': 122,
            'timeout': 20,
            'password':'1234',
            'location_id': self.attendance_device_location.id,
            })
        new_att_device.unlink()
        self.assertEqual(self.env['attendance.device'].search_count([]), 1, "test_delete_device_in_draft_no_attendance_data passed")       
        
    # 17. Xóa thiết bị ở trạng thái Draft và đã có dữ liệu chấm công 
    def test_15_delete_device_in_draft_has_attendance_data(self):
        with self.assertRaises(UserError, msg = "test_delete_device_in_draft_has_attendance_data passed"):
            new_att_device = self.env['attendance.device'].create({
                'name': 'new_att_device',
                'ip': 'new_ip',
                'port': 122,
                'timeout': 20,
                'password':'1234',
                'location_id': self.attendance_device_location.id,
                })
            new_att_device_user = self.env['attendance.device.user'].create({
                'name': 'new user',
                'device_id': new_att_device.id,
                'user_id': 123,
                'uid': 123,
                })
            self.user_attendance = self.env['user.attendance'].create({
                'device_id': new_att_device.id,
                'user_id': new_att_device_user.id,
                'timestamp': fields.datetime.now(),
                'status': 1,
                'attendance_state_id': self.env['attendance.state'].search([])[1].id,
                })
            new_att_device.unlink()
        
    # Form test
    # Case 5: Time zone của máy chấm công tự cập nhật theo time zone của location 
    def test_16_compute_tz(self):
        self.attendance_device.location_id.tz = 'Asia/Ho_Chi_Minh'
        self.assertEqual(self.attendance_device.tz, 'Asia/Ho_Chi_Minh') 
        
   # Form test
    # Case 6: Sau khi thực hiện Download Users (tại form view của Device Manager), số lượng Users sẽ được tự cập nhật theo số lượng users có trong máy chấm công 
    def test_17_compute_device_users_count(self):
        self.env['attendance.device.user'].create({
            'name': 'test_attendance_device_user',
            'device_id': self.attendance_device.id,
            'user_id': 2
            })
        self.assertEqual(self.attendance_device.device_users_count, 1) 
        
    # Form test
    # Case 7: Số lượng Employee trên hệ thống đã được map với Device users trong máy chấm công được tự động cập nhật sau thao tác “Map Employee"
    def test_18_compute_mapped_employees_count(self):
        new_employee = self.env['hr.employee'].create({
            'name': 'Van A',
            })
        new_user = self.env['attendance.device.user'].create({
            'name': 'new_test_user',
            'device_id': self.attendance_device.id,
            'user_id': 2,
            'employee_id': new_employee.id,
            })
        self.assertEqual(self.attendance_device.mapped_employees_count, 1)
        pass
        
    # Form test
    # Case 8: Số lượng vân tay có trong máy chấm công tại form view Device Manager tự cập nhật sau thao tác Download Fingers Template (nếu máy chấm công có sự thay đổi số lượng vân tay) 
    def test_19_compute_total_finger_template_records(self):
        self.test_08_action_finger_template_download()
        self.env['finger.template'].create({
            'uid': 2,
            'fid': 2,
            'device_user_id': self.attendance_device.device_user_ids.search([('name','=','test')], limit=1).id,
            'device_id': self.attendance_device.id,
            })
        self.attendance_device._compute_total_finger_template_records()
        self.assertEqual(self.attendance_device.total_finger_template_records, 2, "test_compute_total_finger_template_records passed")
        
    # Form test
    # Case 9: Số lượng bản ghi thông tin chấm công (Attendance Records) tự cập nhật sau khi thực hiện Download Attendance 
    def test_20_compute_total_attendance_records(self):
        self.test_09_action_attendance_download()
        self.env['user.attendance'].create({
            'device_id': self.attendance_device.id,
            'user_id': self.attendance_device.device_user_ids.search([('name','=','test')], limit=1).id,
            'timestamp': fields.datetime.now(),
            'status': 1,
            'attendance_state_id': self.env['attendance.state'].search([('code','=',1)], limit=1).id,
            })
        self.attendance_device._compute_total_attendance_records()
        self.assertEqual(self.attendance_device.total_att_records, 2, "test_compute_total_attendance_records passed")        
