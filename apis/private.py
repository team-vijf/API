from flask_restplus import Namespace, Resource, fields
from core import db
from functools import wraps
from flask import request
import sys
import requests
import json
import threading
import time
import random

api = Namespace('Private', description='The private side of the Lokaalbezetting API')

newBuilding = api.model('New Building', {'name': fields.String('Name of the building, e.g. HL15'), 'streetname': fields.String('Streetname, e.g. Heidelberglaan'), 'buildingnumber': fields.Integer('Building number, e.g. 15')})
newFloor = api.model('New Floor', {'building_id': fields.String('UUID of the building this floor belongs to.'), 'floor_number': fields.String('Floor number')})
newClassroom = api.model('New Classroom', {'classcode': fields.String('The classcode of the classroom.'), 'floor_id': fields.String('UUID of the floor this classroom belongs to.')})
setLocation = api.model('Set Location', {'location': fields.String('Classcode of the location of the sensor device.')})

sensor_fields = api.model('Sensor Values', {'sensor_name': fields.String('Name of the sensor'), 'value': fields.String('Value of the sensor')})
sensor_list = api.model('Sensor Values List', {'sensors': fields.List(fields.Nested(sensor_fields))})

newFloorplan = api.model('New Floorplan', {'floor_id': fields.String('UUID of the floor this floorplan belongs to.'), 'floorplan': fields.String('Floorplan in XML form')})

def generate_sample_data():

    database = db.Database()

    while True:
        global stop
        if stop:
            break
        classrooms = database.query('''SELECT classcode FROM classrooms;''')
        for classroom in classrooms:
            free = random.choice([0,1])
            if free == 0:

                addValue = database.query('''INSERT INTO occupation ( classcode, free, time ) VALUES ( '{}', true, Now() ) ;'''.format(classroom[0]))

            elif free == 1:
                continue

        time.sleep(19)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']
        
        if not token:
            return {'status': 'failed', 'error': 'This endpoint requires a private access token'}, 401

        database = db.Database()
        matchedTokens = database.readToken(token=token, namespace='private')
        if matchedTokens == False:
            return {'status': 'failed', 'error': 'Could not check if token exists in database'}

        else:
            if len(matchedTokens) == 0:
                return {'status': 'failed', 'error': 'Incorrect token. Are you using a private access token?'}, 401
        

        return f(*args, **kwargs)

    return decorated

@api.route('/sensor_values')
class sensorValues(Resource):

    @api.doc(security='Token')
    @token_required
    @api.response(200, 'Success')
    @api.response(401, 'Unauthorized')
    @api.expect(sensor_list)
    def post(self):

        if 'sensors' not in api.payload:
            return {'status': 'failed', 'error': 'No sensor_values provided.'}

        # Check who it is
        token = request.headers['X-API-KEY']

        database = db.Database()
        uidQuery = database.query('''SELECT uid FROM tokens WHERE token = '{}';'''.format(token))
        uid = uidQuery[0][0]

        # Check if location was set
        locationQuery = database.query('''SELECT location FROM configs WHERE uid = '{}';'''.format(uid))
        location = locationQuery[0][0]

        if location == None:
            return {'status': 'failed', 'error': 'Device location was not set.'}

        sensors = api.payload['sensors']

        motion_value = int(sensors[0]['value'])

        if motion_value == 100:

            addValue = database.query('''INSERT INTO occupation ( classcode, free, time ) VALUES ( '{}', true, Now() ) ;'''.format(location))
            if addValue == False:
                return {'status': 'failed', 'error': 'Could not insert sensor value in database.'}

            # test = database.query('''select count(*) from occupation WHERE classcode = '{}' AND time > now() - interval '60 seconds';'''.format(location))

            # print(test[0][0])

            return {'status': 'ok'}


@api.route('/config')
class config(Resource):

    @api.doc(security='Token')
    @token_required
    @api.response(200, 'Success')
    @api.response(401, 'Unauthorized')
    def get(self):

        token = request.headers['X-API-KEY']

        database = db.Database()
        config = database.readConfig(token=token)

        if config == False:
            return {'status': 'failed', 'error': 'Could not retrieve config from database'}

        return {'status': 'ok', 'config': config}

@api.route('/config/location/set')
class setLocation(Resource):

    @api.doc(security='Token')
    @token_required
    @api.response(200, 'Success')
    @api.response(401, 'Unauthorized')
    @api.expect(setLocation)
    def post(self):
        
        if 'location' not in api.payload:
            return {'status': 'failed', 'error': 'You have to provide a classcode as location.'}

        token = request.headers['X-API-KEY']

        database = db.Database()

        try:
            result = database.query('''SELECT * FROM classrooms WHERE classcode = '{}';'''.format(api.payload['location']))
            if len(result) < 1:
                return {'status': 'failed', 'error': 'Classroom with classcode: {} does not exist'.format(api.payload['location'])}
        except:
            return {'status': 'failed', 'error': 'Classroom with classcode: {} does not exist'.format(api.payload['location'])}

        setConfig = database.setLocation(token=token, location=api.payload['location'])
        
        if setConfig == False:
            return {'status': 'failed', 'error': 'Could not set location.'}

        return {'status': 'ok'}


@api.route('/buildings/new')
class newBuilding(Resource):

    @api.doc(security='Token')
    @token_required
    @api.response(200, 'Success')
    @api.response(401, 'Unauthorized')
    @api.expect(newBuilding)
    def post(self):

        print(api.payload)

        if 'name' not in api.payload or 'streetname' not in api.payload or 'buildingnumber' not in api.payload:
            return {'status': 'failed', 'error': 'You have to provide name, streetname and buildingnumber'}

        database = db.Database()
        try:
            result = database.query('''SELECT * FROM buildings WHERE name = '{}';'''.format(api.payload['name']))
            if len(result) > 0:
                return {'status': 'failed', 'error': 'Building with name {} already exists.'.format(api.payload['name'])}

        except:
            pass

        database.addBuilding(name=api.payload['name'], streetName=api.payload['streetname'], buildingNumber=api.payload['buildingnumber'])

        result = database.query('''SELECT * FROM buildings WHERE name = '{}';'''.format(api.payload['name']))
        created = {'id': result[0][0], 'name': result[0][1], 'street_name': result[0][2], 'building_number': result[0][3]}

        return {'status': 'ok', 'created': created}

@api.route('/floors/new')
class newBuilding(Resource):

    @api.doc(security='Token')
    @token_required
    @api.response(200, 'Success')
    @api.response(401, 'Unauthorized')
    @api.expect(newFloor)
    def post(self):

        if 'floor_number' not in api.payload or 'building_id' not in api.payload:
            return {'status': 'failed', 'error': 'You have to provide floornumber and the uuid of the building that the floor belongs to.'}

        database = db.Database()
        try:
            # Check if building exists
            try:
                result = database.query('''SELECT * FROM buildings WHERE id = '{}';'''.format(api.payload['building_id']))
                if len(result) < 1:
                    return {'status': 'failed', 'error': 'Building with UUID {} does not exist'.format(api.payload['building_id'])}
            except:
                return {'status': 'failed', 'error': 'Building with UUID {} does not exist'.format(api.payload['building_id'])}

            # Check if floor already exists
            result = database.query('''SELECT * FROM floors WHERE id_buildings = '{}' AND floornumber = '{}';'''.format(api.payload['building_id'], api.payload['floor_number']))
            if len(result) > 0:
                return {'status': 'failed', 'error': 'Floor already exists.'}

        except Exception as err:
            sys.stderr.write('Database Error: {}'.format(err))

        database.addFloor(floorNumber=api.payload['floor_number'], buildingId=api.payload['building_id'])

        result = database.query('''SELECT * FROM floors WHERE floornumber = '{}' AND id_buildings = '{}';'''.format(api.payload['floor_number'], api.payload['building_id']))
        created = {'id': result[0][0], 'floor_number': result[0][1], 'building_id': result[0][2]}

        return {'status': 'ok', 'created': created}

@api.route('/classrooms/new')
class newClassroom(Resource):

    @api.doc(security='Token')
    @token_required
    @api.response(200, 'Success')
    @api.response(401, 'Unauthorized')
    @api.expect(newClassroom)
    def post(self):

        if 'classcode' not in api.payload or 'floor_id' not in api.payload:
            return {'status': 'failed', 'error': 'You have to provide the classcode of the classroom and the uuid of the floor that the classroom belongs to.'}

        database = db.Database()

        try:
            # Check if floor exists
            try:
                result = database.query('''SELECT * FROM floors WHERE id = '{}';'''.format(api.payload['floor_id']))
                if len(result) < 1:
                    return {'status': 'failed', 'error': 'Floor with UUID {} does not exist'.format(api.payload['floor_id'])}
            except:
                return {'status': 'failed', 'error': 'Floor with UUID {} does not exist'.format(api.payload['floor_id'])}

            # Check if classroom already exists
            result = database.query('''SELECT * FROM classrooms WHERE id_floors = '{}' AND classcode = '{}';'''.format(api.payload['floor_id'], api.payload['classcode']))
            if len(result) > 0:
                return {'status': 'failed', 'error': 'Classroom already exists.'}

        except Exception as err:
            sys.stderr.write('Database Error: {}'.format(err))

        database.addClassroom(classCode=api.payload['classcode'], floorId=api.payload['floor_id'])

        result = database.query('''SELECT * FROM classrooms WHERE classcode = '{}' AND id_floors = '{}';'''.format(api.payload['classcode'], api.payload['floor_id']))
        created = {'classcode': result[0][0], 'floor_id': result[0][1]}

        return {'status': 'ok', 'created': created}

@api.route('/floorplan/new')
class Floorplan(Resource):

    @api.doc(security=['Token'])
    @token_required
    @api.response(200, 'Success')
    @api.response(401, 'Unauthorized')
    @api.expect(newFloorplan)
    
    def post(self):

        if 'floorplan' not in api.payload or 'floor_id' not in api.payload:
            return {'status': 'failed', 'error': 'You have to provide floor_id and the floorplan'}

        database = db.Database()

        try:
            result = database.query('''SELECT * FROM floors WHERE id = '{}';'''.format(api.payload['floor_id']))
            if len(result) < 1:
                return {'status': 'failed', 'error': 'Floor with UUID {} does not exist'.format(api.payload['floor_id'])}
        except:
            return {'status': 'failed', 'error': 'Floor with UUID {} does not exist'.format(api.payload['floor_id'])}

        try:
            result = database.query('''SELECT * FROM floorplans WHERE id_floors = '{}';'''.format(api.payload['floor_id']))
            if len(result) > 0:
                return {'status': 'failed', 'error': 'There is already a floorplan for floor with UUID {}.'.format(api.payload['floor_id'])}
        except:
            return {'status': 'failed', 'error': 'There is already a floorplan for floor with UUID {}.'.format(api.payload['floor_id'])}

        database.addFloorplan(floorPlan=api.payload['floorplan'].replace("'", "''"), floorId=api.payload['floor_id'])

        result = database.query('''SELECT * FROM floorplans WHERE id_floors = '{}';'''.format(api.payload['floor_id']))

        return {'status': 'ok', 'floorplan': result[0][0]}

@api.route('/debug/create_hl15')
class SampleBuilding(Resource):

    @api.doc(security=['Token'])
    @token_required
    @api.response(200, 'Success')
    @api.response(401, 'Unauthorized')
    def get(self):

        url = 'http://localhost'

        try:
            request_access = {'uid': 'debug', 'shared_secret': 'secret', 'type': 'device'}
            r = requests.post('{}/access/private'.format(url), json=request_access)
            r_reply = json.loads(r.text)

            auth_header = {'X-API-KEY': r_reply['token']} 

            building = {'name': 'HL15', 'streetname': 'Heidelberglaan', 'buildingnumber': 15}
            r = requests.post('{}/private/buildings/new'.format(url), json=building, headers=auth_header)
            r_reply = json.loads(r.text)

            if r_reply['status'] == 'failed':

                if 'exists' in r_reply['error']:

                    r = requests.get('{}/public/occupation/buildings'.format(url), headers=auth_header)
                    r_reply = json.loads(r.text)

                    for line in r_reply['buildings']:
                        if line['name'] == building['name']:
                            building_uuid = line['id']

            else:

                building_uuid = r_reply['created']['id']

            r = requests.post('{}/private/floors/new'.format(url), json={'building_id': building_uuid, 'floor_number': '4'}, headers=auth_header)
            r_reply = json.loads(r.text)

            if r_reply['status'] == 'failed':

                if 'exists' in r_reply['error']:

                    r = requests.get('{}/public/occupation/buildings'.format(url), headers=auth_header)
                    r_reply = json.loads(r.text)

                    for line in r_reply['buildings']:
                        if line['id'] == building_uuid:
                            for floor in line['floors']:
                                if floor['floornumber'] == 4:
                                    floor_uuid = floor['id']

            else:

                floor_uuid = r_reply['created']['id']

            classrooms = ["HL15-4.064", "HL15-4.062", "HL15-4.060", "HL15-5.052", "HL15-4.070", "HL15-4.072", "HL15-4.074", "HL15-4.066", "HL15-4.056", "HL15-4.085", "HL15-4.083", "HL15-4.090", "HL15-4.092", "HL15-4.044", "HL15-4.091", "HL15-4.043", "HL15-4.101", "HL15-4.037", "HL15-4.030", "HL15-4.028", "HL15-4.026", "HL15-4.094", "HL15-4.096", "HL15-4.098", "HL15-4.104", "HL15-4.042", "HL15-4.036", "HL15-4.038", "HL15-4.114", "HL15-4.118", "HL15-4.009", "HL15-4.007", "HL15-4.005", "HL15-4.002", "HL15-4.008", "HL15-4.014", "HL15-4.018", "HL15-4.020"]

            for classroom in classrooms:
                r = requests.post('{}/private/classrooms/new'.format(url), json={'classcode': classroom, 'floor_id': floor_uuid}, headers=auth_header)
                r_reply = json.loads(r.text)

            return {'status': 'ok'}

        except Exception as err:
            return {'status': 'failed', 'error': str(err)}

@api.route('/debug/sample_data_generator/start')
class SampleData(Resource):

    @api.doc(security=['Token'])
    @token_required
    @api.response(200, 'Success')
    @api.response(401, 'Unauthorized')
    def get(self):
        global x
        global stop
        stop = False
        x = threading.Thread(target=generate_sample_data)
        x.start()
        return {'status': 'ok', 'message': 'Sample data generation started'}

@api.route('/debug/sample_data_generator/stop')
class SampleData(Resource):

    @api.doc(security=['Token'])
    @token_required
    @api.response(200, 'Success')
    @api.response(401, 'Unauthorized')
    def get(self):
        global x
        global stop
        stop = True
        x.join()
        return {'status': 'ok', 'message': 'Sample data generation stopped'}