from flask_restplus import Namespace, Resource, fields
from core import db
from functools import wraps
from flask import request

api = Namespace('Private', description='The private side of the Lokaalbezetting API')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']
        
        if not token:
            return {'status': 'failed', 'error': 'This endpoint requires a join token'}, 401

        database = db.Database()
        database.connect()
        check = database.query('''SELECT * FROM tokens WHERE token = '{}' AND type = 'app' OR type = 'device';'''.format(token))
        database.close()
        if len(check) == 0:
            return {'status': 'failed', 'error': 'Incorrect token'}, 401
        

        return f(*args, **kwargs)

    return decorated



@api.route('/devices/all')
class AllDevices(Resource):

    @api.doc(security='joinKey')
    @token_required
    @api.response(200, 'Success')
    @api.response(401, 'Unauthorized')
    def get(self):
        
        database = db.Database()
        database.connect()
        result = database.query('''SELECT * FROM tokens WHERE type = 'device';''')
        database.close()

        devices = []

        for row in result:
            devices.append({'uid': row[0], 'type': row[1], 'token': row[2]})

        return {'status': 'ok', 'devices': devices}


@api.route('/apps/all')
class AllApps(Resource):

    @api.doc(security='joinKey')
    @token_required
    @api.response(200, 'Success')
    @api.response(401, 'Unauthorized')
    def get(self):
        
        database = db.Database()
        database.connect()
        result = database.query('''SELECT * FROM tokens WHERE type = 'app';''')
        database.close()

        apps = []

        for row in result:
            apps.append({'uid': row[0], 'type': row[1], 'token': row[2]})

        return {'status': 'ok', 'apps': apps}



# @api.route('/configs/default/devices')
# class DefaultDevicesConfig(Resource):
#     def get(self):
#         # Get default config from database and return it
#         config = []
#         test_config = {'sensor1_threshold': '0.55', 'sensor2_threshold': '0.67'}
#         config.append(test_config)
#         return {'status': 'ok', 'config': config}

# @api.route('/configs/default/app')
# class DefaultAppConfig(Resource):
#     def get(self):
#         # Get default config from database and return it
#         config = []
#         test_config = {'feature_toggle1': 'True', 'feature2': 'False'}
#         config.append(test_config)
#         return {'status': 'ok', 'config': config}

# @api.route('/configs/<uid>')
# class SpecificConfig(Resource):
#     def get(self):
#         # Get device specific config from database and return it
#         config = []
#         test_config = {'sensor1_threshold': '0.55', 'sensor2_threshold': '0.67'}
#         config.append(test_config)
#         return {'status': 'ok', 'config': config}