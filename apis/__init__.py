from flask_restplus import Api
from flask import url_for

from .private import api as private
from .public import api as public

authorizations = {
    'accessKey' : {
        'type' : 'apiKey',
        'in' : 'header',
        'name' : 'X-API-KEY'
    },
    'joinKey' : {
        'type' : 'apiKey',
        'in' : 'header',
        'name' : 'X-API-KEY'
    }
}

motd = '''Welkom bij de Lokaalbezetting API. 
Als je een gebruiker bent, vraag je een Access Key aan onder /access. 
Sensor devices en Apps melden zich aan onder /join.'''


api = Api(
    title='Lokaalbezetting API',
    version='0.1',
    doc='/',
    default='Global',
    default_label='Global endpoints that do not require a token to access',
    authorizations=authorizations,
    description=motd
)

api.add_namespace(private, path='/private')
api.add_namespace(public, path='/public')
