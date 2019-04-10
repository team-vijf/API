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

@api.route('/buildings')
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

        joined = database.query('''SELECT b.id, b.name, b.streetname, b.buildingnumber, f.id, f.floornumber, c.classcode
                                   FROM buildings as b
                                   INNER JOIN floors as f ON f.id_buildings = b.id
                                   INNER JOIN classrooms as c ON c.id_floors = f.id;''')

        return {'status': 'ok', 'buildings': totalObject}
