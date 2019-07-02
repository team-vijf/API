from flask import Flask, render_template, url_for, make_response
from flask_restplus import Api, Resource, fields
from flask_cors import CORS
from apis import api
from core import db
from core import api_vars
import secrets
import json

app = Flask(__name__, template_folder='html')
CORS(app)
api.init_app(app)

@api.representation('text/csv')
def data_csv(data, code, headers):
    '''Get result in csv '''
    resp = make_response(convert_data(data), code)
    resp.headers.extend(headers)
    return resp

def convert_data(data):

    converted_data = json.loads(str(data))

    if converted_data['status'] == 'failed':
        return data
    else:
        try:
            data = converted_data['export']
        except:
            return data

    if type(data) == dict:
        csv = '''classcode,time of detection
'''
        for classroom in data:
            for detection in data[classroom]:
                row = '''{},{}
'''.format(classroom, detection)
                csv += row
        return csv

    else:
        return None

# We define models so we can define what the API has to expect for certain endpoints
private_access_request = api.model('Private Access Request', {'uid': fields.String('A unique identifier.'), 'shared_secret': fields.String('The shared secret.'), 'type': fields.String('Can either be device or app.')})
public_access_request = api.model('Public Access Request', {'email': fields.String('Your HU Email.')})

@api.route('/access/private')
class privateAccess(Resource):
    '''
    This endpoint is meant for sensor devices and web-app instances to register theirselves and get hold of an API Key.
    They can use this API Key to write sensor-data, write logs and do other operations that require security.
    '''

    @api.expect(private_access_request)
    @api.response(200, 'Success')
    @api.response(401, 'Unauthorized')
    def post(self):

        # If the provided shared_secret is correct (According to core/api_vars)
        if api.payload['shared_secret'] == api_vars.SHARED_SECRET:

            # If the type is not device or app, then return an error
            if api.payload['type'] != 'device' and api.payload['type'] != 'app':
                return {'status': 'failed', 'error': 'Type can only be device or app'}

            # Generate a 40 character token
            token = secrets.token_hex(40)

            # Try to write the token to the database
            database = db.Database()
            if database.writeToken(uid=api.payload['uid'], type=api.payload['type'], token=token):
                # If the operation was successful
                return {'status': 'ok', 'token': token}

            else:
                # If there was a database error
                return {'status': 'failed', 'error': 'Could not write token to database'}

        # If the join_token was incorrect
        else:
            return {'status': 'failed', 'error': 'Incorrect shared secret.'}, 401


@api.route('/access/public')
class publicAccess(Resource):
    '''
    This endpoint is meant for users that seek to access information such as room-occupation via the API.
    We created this endpoint besides the webapp so that users can build upon the data we collect.
    '''

    @api.expect(public_access_request)
    def post(self):

        # We only want students and staff of the HU to be able to apply for an access token
        if '@student.hu.' in api.payload['email'] or '@hu.' in api.payload['email']:

            # Generate a 40 character token
            token = secrets.token_hex(40)

            # Try to write the token to the database
            database = db.Database()
            if database.writeToken(uid=api.payload['email'], type='user', token=token):
                # If the operation was successful
                return {'status': 'ok', 'token': token}

            else:
                # If there was a database error
                return {'status': 'failed', 'error': 'Could not write token to database'}
            
        # If the email wasn't of a HU student / staffmember
        else:
            return {'status': 'failed', 'error': 'You can only apply for an access token with a HU email account.'}, 401

@app.route('/admin')
def index():

    return render_template('index.html')



if __name__ == '__main__':

    app.run(debug=api_vars.API_DEBUG, port=api_vars.API_PORT, host=api_vars.API_IP)