from flask_restplus import Namespace, Resource, fields
from core import db
from functools import wraps
from flask import request

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

        for building in buildings:
            buildingdict = dict()
            buildingdict['id'] = building[0]
            buildingdict['name'] = building[1]
            buildingdict['streetname'] = building[2]
            buildingdict['buildingnumber'] = building[3]
            buildingdict['floors'] = []
            totalObject.append(buildingdict)

        floors = database.query('''SELECT * FROM floors ORDER BY floornumber;''')

        for floor in floors:
            floordict = dict()
            floordict['id'] = floor[0]
            floordict['floornumber'] = int(floor[1])
            floordict['classrooms'] = []

            for building in totalObject:
                if building['id'] == floor[2]:
                    building['floors'].append(floordict)

        classrooms = database.query('''SELECT * FROM classrooms;''')

        for classroom in classrooms:
            classroomdict = dict()
            classroomdict['classcode'] = classroom[0]

            free = "Unknown"

            try:
                freeQuery = database.query('''SELECT free FROM occupation WHERE classcode = '{}' ORDER BY time DESC LIMIT 1;'''.format(classroom[0]))
                free = freeQuery[0][0]
            except:
                free = "Unknown"

            classroomdict['free'] = free

            for buildings in totalObject:
                for floor in buildings['floors']:
                    if floor['id'] == classroom[1]:
                        floor['classrooms'].append(classroomdict)

        return {'status': 'ok', 'buildings': totalObject}
