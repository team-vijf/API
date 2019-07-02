from flask_restplus import Namespace, Resource, fields
from core import db
from functools import wraps
from flask import request
from core import api_vars
import sys

api = Namespace('Public', description='The public side of the Lokaalbezetting API')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']
        
        if not token:
            return {'status': 'failed', 'error': 'This endpoint requires an access token'}, 401

        database = db.Database()
        matchedTokens = database.readToken(token=token, namespace='public')
        if matchedTokens == False:
            return {'status': 'failed', 'error': 'Could not check if token exists in database'}
        else:
            if len(matchedTokens) == 0:
                return {'status': 'failed', 'error': 'Incorrect token'}, 401
        
        return f(*args, **kwargs)

    return decorated

@api.route('/classrooms')
class Classrooms(Resource):

    @api.doc(security=['Token'])
    @token_required
    @api.response(200, 'Success')
    @api.response(401, 'Unauthorized')
    def get(self):

        classrooms = []

        database = db.Database()
        classroomsQuery = database.query('''SELECT classcode FROM classrooms;''')

        if classroomsQuery == False:
            return {'status': 'failed', 'error': 'Could not get classrooms from database.'}

        if len(classroomsQuery) < 1:
            return {'status': 'failed', 'error': 'There are no classrooms.'}

        for classroom in classroomsQuery:
            classroomdict = dict()
            classroomdict['classcode'] = classroom[0]
            classrooms.append(classroomdict)

        return {'status': 'ok', 'classrooms': classrooms}

@api.route('/occupation/buildings')
class Buildings(Resource):

    @api.doc(security=['Token'])
    @token_required
    @api.response(200, 'Success')
    @api.response(401, 'Unauthorized')
    def get(self):

        totalObject = []
        
        database = db.Database()
        buildings = database.query('''SELECT * FROM buildings ORDER BY name;''')

        if buildings == False:
            return {'status': 'failed', 'error': 'Could not get buildings from database'}

        if len(buildings) < 1:
            return {'status': 'failed', 'error': 'There are no buildings.'}

        for building in buildings:
            buildingdict = dict()
            buildingdict['id'] = building[0]
            buildingdict['name'] = building[1]
            buildingdict['streetname'] = building[2]
            buildingdict['buildingnumber'] = building[3]
            buildingdict['floors'] = []
            totalObject.append(buildingdict)

        floors = database.query('''SELECT * FROM floors ORDER BY floornumber;''')

        if floors == False:
            return {'status': 'failed', 'error': 'Could not get floors from database'}

        for floor in floors:
            floordict = dict()
            floordict['id'] = floor[0]
            floordict['floornumber'] = int(floor[1])
            floordict['classrooms'] = []

            for building in totalObject:
                if building['id'] == floor[2]:
                    building['floors'].append(floordict)

        classrooms = database.query('''SELECT * FROM classrooms;''')

        if classrooms == False:
            return {'status': 'failed', 'error': 'Could not get classrooms from database'}

        for classroom in classrooms:
            classroomdict = dict()
            classroomdict['classcode'] = classroom[0]

            free = "Unknown"

            try:
                freeQuery = database.query('''select count(*) from occupation WHERE classcode = '{}' AND time > now() - interval '60 seconds';'''.format(classroomdict['classcode']))
                

                if freeQuery[0][0] >= int(api_vars.MOTION_THRESHOLD):
                    free = False
                elif freeQuery[0][0] < int(api_vars.MOTION_THRESHOLD):
                    free = True
            except:
                free = "Unknown"

            classroomdict['free'] = free

            for buildings in totalObject:
                for floor in buildings['floors']:
                    if floor['id'] == classroom[1]:
                        floor['classrooms'].append(classroomdict)

        return {'status': 'ok', 'buildings': totalObject}

@api.route('/occupation/building/<string:building_id>')
class Building(Resource):

    @api.doc(security=['Token'])
    @token_required
    @api.response(200, 'Success')
    @api.response(401, 'Unauthorized')

    def get(self, building_id):

        totalObject = []
        
        database = db.Database()
        buildings = database.query('''SELECT * FROM buildings WHERE id = '{}' ORDER BY name;'''.format(building_id))

        if buildings == False:
            return {'status': 'failed', 'error': '{} is not a valid UUID.'.format(building_id)}

        if len(buildings) < 1:
            return {'status': 'failed', 'error': 'Building with id {} does not exist.'.format(building_id)}

        for building in buildings:
            buildingdict = dict()
            buildingdict['id'] = building[0]
            buildingdict['name'] = building[1]
            buildingdict['streetname'] = building[2]
            buildingdict['buildingnumber'] = building[3]
            buildingdict['floors'] = []
            totalObject.append(buildingdict)

        floors = database.query('''SELECT * FROM floors ORDER BY floornumber;''')

        if floors == False:
            return {'status': 'failed', 'error': 'Could not get floors from database'}

        for floor in floors:
            floordict = dict()
            floordict['id'] = floor[0]
            floordict['floornumber'] = int(floor[1])
            floordict['classrooms'] = []

            for building in totalObject:
                if building['id'] == floor[2]:
                    building['floors'].append(floordict)

        classrooms = database.query('''SELECT * FROM classrooms;''')

        if classrooms == False:
            return {'status': 'failed', 'error': 'Could not get classrooms from database'}

        for classroom in classrooms:
            classroomdict = dict()
            classroomdict['classcode'] = classroom[0]

            free = "Unknown"

            try:
                freeQuery = database.query('''select count(*) from occupation WHERE classcode = '{}' AND time > now() - interval '60 seconds';'''.format(classroomdict['classcode']))
                if freeQuery[0][0] >= int(api_vars.MOTION_THRESHOLD):
                    free = False
                elif freeQuery[0][0] < int(api_vars.MOTION_THRESHOLD):
                    free = True
            except:
                free = "Unknown"

            classroomdict['free'] = free

            for buildings in totalObject:
                for floor in buildings['floors']:
                    if floor['id'] == classroom[1]:
                        floor['classrooms'].append(classroomdict)

        building = totalObject[0]

        return {'status': 'ok', 'id': building['id'], 'name': building['name'], 'streetname': building['streetname'], 'buildingnumber': building['buildingnumber'], 'floors': building['floors']}

@api.route('/occupation/floor/<string:floor_id>')
class Floor(Resource):

    @api.doc(security=['Token'])
    @token_required
    @api.response(200, 'Success')
    @api.response(401, 'Unauthorized')

    def get(self, floor_id):

        database = db.Database()
        
        floors = database.query('''SELECT * FROM floors WHERE id = '{}';'''.format(floor_id))

        if floors == False:
            return {'status': 'failed', 'error': 'Could not get floors from database'}

        if len(floors) < 1:
            return {'status': 'failed', 'error': 'Floor with id {} does not exist'.format(floor_id)}

        floor_id = floors[0][0]
        floor_number = int(floors[0][1])
        classrooms_object = []

        classrooms = database.query('''SELECT * FROM classrooms WHERE id_floors = '{}';'''.format(floor_id))

        if classrooms == False:
            return {'status': 'failed', 'error': 'Could not get classrooms from database'}

        if len(classrooms) < 1:
            return {'status': 'failed', 'error': 'Floor with id {} has no classrooms'.format(floor_id)}

        for classroom in classrooms:
            classroomdict = dict()
            classroomdict['classcode'] = classroom[0]

            free = "Unknown"

            try:
                freeQuery = database.query('''select count(*) from occupation WHERE classcode = '{}' AND time > now() - interval '60 seconds';'''.format(classroomdict['classcode']))
                if freeQuery[0][0] >= int(api_vars.MOTION_THRESHOLD):
                    free = False
                elif freeQuery[0][0] < int(api_vars.MOTION_THRESHOLD):
                    free = True
            except:
                free = "Unknown"

            classroomdict['free'] = free

            classrooms_object.append(classroomdict)

        return {'status': 'ok', 'id': floor_id, 'classrooms': classrooms_object}



@api.route('/occupation/classroom/<string:classcode>')
class Classroom(Resource):

    @api.doc(security=['Token'])
    @token_required
    @api.response(200, 'Success')
    @api.response(401, 'Unauthorized')

    def get(self, classcode):

        database = db.Database()
        
        classrooms = database.query('''SELECT * FROM classrooms WHERE classcode = '{}';'''.format(classcode))

        if classrooms == False:
            return {'status': 'failed', 'error': 'Could not get classrooms from database'}

        if len(classrooms) < 1:
            return {'status': 'failed', 'error': 'Classroom with classcode {} does not exist'.format(classcode)}

        classcode = classrooms[0][0]

        free = "Unknown"

        try:
            freeQuery = database.query('''select count(*) from occupation WHERE classcode = '{}' AND time > now() - interval '60 seconds';'''.format(classcode))
            if freeQuery[0][0] >= int(api_vars.MOTION_THRESHOLD):
                free = False
            elif freeQuery[0][0] < int(api_vars.MOTION_THRESHOLD):
                free = True
        except:
            free = "Unknown"
        
        return {'status': 'ok', 'classcode': classcode, 'free': free}

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

        return {'status': 'ok', 'floorplan': str(result[0][0])}

@api.route('/export')
class Export(Resource):

    @api.doc(security=['Token'])
    @token_required
    @api.response(200, 'Success')
    @api.response(401, 'Unauthorized')

    def get(self):

        database = db.Database()

        classrooms = database.query('''SELECT classcode FROM occupation;''')

        return {'status': 'ok', 'export': str(classrooms)}