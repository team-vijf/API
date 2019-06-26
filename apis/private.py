from flask_restplus import Namespace, Resource, fields
from core import db
from functools import wraps
from flask import request
import sys

api = Namespace('Private', description='The private side of the Lokaalbezetting API')

newBuilding = api.model('New Building', {'name': fields.String('Name of the building, e.g. HL15'), 'streetname': fields.String('Streetname, e.g. Heidelberglaan'), 'buildingnumber': fields.Integer('Building number, e.g. 15')})
newFloor = api.model('New Floor', {'building_id': fields.String('UUID of the building this floor belongs to.'), 'floor_number': fields.String('Floor number')})
newClassroom = api.model('New Classroom', {'classcode': fields.String('The classcode of the classroom.'), 'floor_id': fields.String('UUID of the floor this classroom belongs to.')})
setLocation = api.model('Set Location', {'location': fields.String('Classcode of the location of the sensor device.')})

sensor_fields = api.model('Sensor Values', {'sensor_name': fields.String('Name of the sensor'), 'value': fields.String('Value of the sensor')})
sensor_list = api.model('Sensor Values List', {'sensors': fields.List(fields.Nested(sensor_fields))})

newFloorplan = api.model('New Floorplan', {'floor_id': fields.String('UUID of the floor this floorplan belongs to.'), 'floorplan': fields.String('Floorplan in XML form')})

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

@api.route('/floorplan/<string:floor_id>')
class Floorplan(Resource):

    @api.doc(security=['Token'])
    @token_required
    @api.response(200, 'Success')
    @api.response(401, 'Unauthorized')
    

    def get(self, floor_id):
        
        database = db.Database()

        try:
            result = database.query('''SELECT * FROM floorplans WHERE id_floors = '{}';'''.format(floor_id))
            if len(result) < 1:
                return {'status': 'failed', 'error': 'There is no floorplan for floor with UUID {}.'.format(floor_id)}
        except:
            return {'status': 'failed', 'error': 'Floor with UUID {} does not exist'.format(floor_id)}

        return {'status': 'ok', 'floorplan': str(result)}

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

        database.addFloorplan(floorPlan=api.payload['floorplan'].replace("'", "''"), floorId=api.payload['floor_id'])

        result = database.query('''SELECT * FROM floorplans WHERE id_floors = '{}';'''.format(api.payload['floor_id']))
        print(result)

        return {'status': 'ok'}