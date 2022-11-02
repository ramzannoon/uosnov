import requests
import xml.etree.ElementTree as ET
import pdb
import json


def dict2xml(d, root_node=None):
	wrap = False if None == root_node or isinstance(d, list) else True
	root = 'objects' if None == root_node else root_node
	root_singular = root[:-1] if 's' == root[-1] and None == root_node else root
	xml = ''
	children = []
	
	if isinstance(d, dict):
		for key, value in dict.items(d):
			if isinstance(value, dict):
				children.append(dict2xml(value, key))
			elif isinstance(value, list):
				children.append(dict2xml(value, key))
			else:
				xml = xml + ' ' + key + '="' + str(value) + '"'
	else:
		for value in d:
			children.append(dict2xml(value, root_singular))
	
	end_tag = '>' if 0 < len(children) else '/>'
	
	if wrap or isinstance(d, dict):
		xml = '<' + root + xml + end_tag
	
	if 0 < len(children):
		for child in children:
			xml = xml + child
		
		if wrap or isinstance(d, dict):
			xml = xml + '</' + root + '>'
	
	return xml


def import_instructors(term='Fall2019'):
	params = (
		('term', term),
	)
	response = requests.get('http://159.65.165.29/UniTime/api/instructors', params=params, auth=('admin', 'admin'))
	depts = response.json()
	instructorsData = []
	for dept in depts:
		code = dept['deptCode']
		for instructor in dept.get('instructors',False):
			instructor_data = {
				'unitimeId': instructor['instructorId'],
				'first_name': instructor['firstName'],
				'last_name': instructor['lastName'],
				'position': instructor['position'],
				'deptcode': code,
			}
			instructorsData.append(instructor_data)
	return instructorsData
	

def import_rooms(term='Fall2019'):
	params = (
		('term', term),
	)
	response = requests.get('http://159.65.165.29/UniTime/api/rooms', params=params, auth=('admin', 'admin'))
	#rooms = json.dumps(response.content)
	rooms = response.json()
	roomData = []
	for room in rooms:
		room_data = {
			'externalId': room.get('externalId',False),
			'capacity': room.get('capacity', False),
			'examCapacity': room.get('examCapacity', False),
			'locationX': room.get('x', False),
			'locationY': room.get('y', False),
			'roomSharingNote': room.get('roomSharingNote', False),
			'eventNote': room.get('eventNote', False),
			'code': room.get('abbv', False),
			'name': room.get('name', False),
			'extra': {
				'building': room.get('building',False),
				'roomType': room.get('roomType', False),
				'eventDepartment': room.get('eventDepartment',False),
				'departments': room.get('departments',False),
				'features': room.get('features',False),
				'examTypes': room.get('examTypes',False),
				
			}
		}
		#days = []
		#for day in timePattern.findall("./days"):
		#	days.append({'code': day.attrib['code']})
		
		
		#time_pattern['days'] = days
		
		roomData.append(room_data)
	return roomData
			

#export Building-Rooms
def export_rooms(term='Fall2019'):
	headers = {
		'Content-Type': 'application/json;charset=UTF-8',
	}
	
	params = (
		('term', term),
	)
	
	payload = {
		"abbreviation": "113",
		"name": "Purdue Village Apts #113",
		"x": 339,
		"y": 404,
		"externalId": "14Q07A1C11FQD1GNDC1U"
	}
	data = json.dumps(payload)
	# data = open('room.json')
	#response = requests.post('http://159.65.165.29/UniTime/api/buildings', headers=headers, params=params, data=data,
	#    verify=False, auth=('admin', 'admin'))
	
	payload = {
		'building': {
			'abbreviation': '113'
		},
		'name': '204',
		'capacity': 10,
		'examCapacity': 5,
		'externalId': '113-204',
		'x': 48.8583736,
		'y': 2.2922926,
		'abbv': '204',
		'roomType': {
			'reference': 'genClassroom',
			'room': True
		},
		'departments': [
			{"code": "0100"},
			{"code": "0101", "preference": {"code": "P"}}
		],
		'controlDepartment': {
			'code': '0103',
		},
		'eventDepartment': {"code": "0100"},
		'groups': [
			{"abbv": "Classroom"},
			{"abbv": "Biol Labs", "department": {"code": "0101"}}
		],
		'features': [
			{"abbv": "AudRec"},
			{"abbv": "Comp"},
			{"name":"Projector","abbv": "projector"}
		],
		'examTypes': [
			{"reference": "final"}
		],
		# 'breakTime' : null,
		# 'eventStatus' : null,
		'eventNote': "What the hack?",
		'roomSharingNote': "Sorry, no sharing!"
	}
	data = json.dumps(payload)
	response = requests.post('http://159.65.165.29/UniTime/api/rooms', headers=headers, params=params, data=data,
		verify=False, auth=('admin', 'admin'))
	
	
# sessionSetup
def get_session_setup(term='Fall2019'):
	params = (
		('term', term),
		('type', 'sessionSetup'),
	)
	response = requests.get('http://159.65.165.29/UniTime/api/exchange', params=params, auth=('admin', 'admin'))
	root = ET.fromstring(response.content)

	timePatterns = []
	for timePattern in root.findall("./timePatterns/timePattern"):
		print(timePattern.attrib)
		time_pattern = {
			'name': timePattern.attrib['name'],
			'nbrMeetings': timePattern.attrib['nbrMeetings'],
			'minsPerMeeting': timePattern.attrib['minsPerMeeting'],
			'type': timePattern.attrib['type'],
			'visible': timePattern.attrib['visible'],
			'nbrSlotsPerMeeting': timePattern.attrib['nbrSlotsPerMeeting'],
			'breakTime': timePattern.attrib['breakTime'],
		}
		days = []
		for day in timePattern.findall("./days"):
			days.append({'code': day.attrib['code']})
		times = []
		for slot in timePattern.findall("./time"):
			times.append({'start': slot.attrib['start']})
		
		time_pattern['days'] = days
		time_pattern['time'] = times
		timePatterns.append(time_pattern)
		
	datePatterns = []
	for datePattern in root.findall("./datePatterns/datePattern"):
		print(datePattern.attrib)
		date_pattern = {
			'name': datePattern.attrib['name'],
			'type': datePattern.attrib['type'],
			'visible': datePattern.attrib['visible'],
			'default': datePattern.attrib['default'],
		}
		dates = []
		for date in datePattern.findall("./dates"):
			dates.append({
				'fromDate': date.attrib['fromDate'],
				'toDate': date.attrib['toDate']
			})
		date_pattern['dates'] = dates
		
		datePatterns.append(date_pattern)
	
	departments = []
	for department in root.findall("./departments/department"):
		print(department.attrib)
		dept = {
			'name': department.attrib['name'],
			'code': department.attrib['code'],
			'externalId': department.attrib.get('externalId',''),
			'abbreviation': department.attrib['abbreviation'],
		}
		
		for event in department.findall("./eventManagement"):
			if event.attrib['enabled']:
				dept['event_mgmt'] = True
		for manager in department.findall("./externalManager"):
			dept['external_manager'] = manager.attrib['enabled']
			dept['external_manager_name'] = manager.attrib['label']
			dept['external_manager_abbreviation'] = manager.attrib['abbreviation']
			
		departments.append(dept)
		
	
	data = {
		'timePatterns': timePatterns,
		'datePatterns': datePatterns,
		'departments': departments,
	}
	return data


#<academicAreas>
#    <academicArea externalId="A" abbreviation="A" title="The Woebegon's Only Academic Area"/>
#  </academicAreas>
#  <academicClassifications>
#    <academicClassification externalId="01" code="01" name="Junior Year"/>
#    <academicClassification externalId="02" code="02" name="Senior Year"/>
#  </academicClassifications>
#  <posMajors>
#    <posMajor code="M1" academicArea="A" externalId="M1" name="Major 1"/>
#    <posMajor code="M2" academicArea="A" externalId="M2" name="Major 2"/>
#    <posMajor code="M3" academicArea="A" externalId="M3" name="Major 3"/>
#  </posMajors>
#  <posMinors/>