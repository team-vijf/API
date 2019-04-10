from flask_restplus import Namespace, Resource, fields
from core import db
from functools import wraps
from flask import request

api = Namespace('Private', description='The private side of the Lokaalbezetting API')

newBuilding = api.model('New Building', {'name': fields.String('Name of the building, e.g. HL15'), 'streetname': fields.String('Streetname, e.g. Heidelberglaan'), 'buildingnumber': fields.String('Building number, e.g. 15')})


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

        return {'status': 'ok'}

