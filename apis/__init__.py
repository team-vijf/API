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

api = Api(
    title='Lokaalbezetting API',
    version='0.1',
    doc='/',
    default='Global',
    default_label='Global endpoints that do not require a token to access',
    authorizations=authorizations
)

api.add_namespace(private, path='/private')
api.add_namespace(public, path='/public')
