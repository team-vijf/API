from flask import Flask
from flask_restplus import Api, Resource, fields
from apis import api
from core import db
from core import api_vars
import secrets

app = Flask(__name__)

api.init_app(app)

# API Model Definitions
join_request_model = api.model('Join Request', {'uid': fields.String('The Device UID.'), 'join_token': fields.String('The Join Token.'), 'type': fields.String('Device/App')})
access_request_model = api.model('Access Request', {'email': fields.String('Your HU Email.')})

# API Route Definitions
@api.route('/join')
class Join(Resource):
    @api.expect(join_request_model)
    def post(self):
        if api.payload['join_token'] == api_vars.JOIN_TOKEN:

            if api.payload['type'] != 'device' and api.payload['type'] != 'app':
                return {'status': 'failed', 'error': 'Type can only be device or app'}

            access_token = secrets.token_hex(40)

            database = db.Database()
            database.connect()
            database.query('''CREATE TABLE IF NOT EXISTS tokens ( uid varchar(255),
                                                                  type varchar(255),
                                                                  token varchar(255),
                                                                  time TIMESTAMP );''')
            database.query('''INSERT INTO tokens VALUES ('{}','{}','{}', Now());'''.format(api.payload['uid'], api.payload['type'], access_token))
            database.close()
            
            return {'status': 'ok', 'access_token': access_token}

        else:
            return {'status': 'failed', 'error': 'Incorrect join token.'}


@api.route('/access')
class Access(Resource):

    @api.expect(access_request_model)
    def post(self):
        if '@student.hu.' in api.payload['email']:

            access_token = secrets.token_hex(40)

            database = db.Database()
            database.connect()
            database.query('''CREATE TABLE IF NOT EXISTS tokens ( uid varchar(255),
                                                                  type varchar(255),
                                                                  token varchar(255),
                                                                  time TIMESTAMP );''')
            database.query('''INSERT INTO tokens VALUES ('{}','{}','{}', Now());'''.format(api.payload['email'], 'user', access_token))
            database.close()
            return {'status': 'ok', 'access_token': access_token}
        else:
            return {'status': 'failed', 'error': 'You can only apply for an access token with a HU email account.'}



if __name__ == '__main__':

    app.run(debug=api_vars.API_DEBUG, port=api_vars.API_PORT, host=api_vars.API_IP)